from datetime import datetime
import socket
import ssl
import whois
import sys
import json

def get_domain_age(domain: str) -> dict:
    """Fetches the creation date and calculates the age of a domain in days."""
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if not creation_date:
            return {"error": "Creation date not found"}

        age_days = (datetime.now() - creation_date).days

        return {
            "creation_date": creation_date.strftime("%Y-%m-%d"),
            "age_days": age_days,
        }
    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}"}

def get_ssl_details(domain: str) -> dict:
    """Connects to the domain via port 443 to retrieve SSL cert info."""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        expiry_str = cert.get("notAfter")
        expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
        days_until_expiry = (expiry_date - datetime.now()).days

        issuer = dict(x[0] for x in cert.get("issuer", ()))
        common_name = issuer.get("commonName", "Unknown")

        return {
            "issuer": common_name,
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "days_until_expiry": days_until_expiry,
        }
    except Exception as e:
        return {"error": f"SSL retrieval failed: {str(e)}"}

def check_domain_and_ssl(url: str) -> dict:
    """Extracts domain from URL and runs age and SSL checks, calculating a risk score."""
    from urllib.parse import urlparse
    import tldextract
    
    # Ensure scheme for urlparse
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        
    ext = tldextract.extract(url)
    domain = f"{ext.domain}.{ext.suffix}"
    
    result = {
        'domain': domain,
        'age_days': None,
        'days_until_expiry': None,
        'issuer': None,
        'risk_score': 0,
        'errors': []
    }
    
    # 1. Fetch Age
    age_info = get_domain_age(domain)
    if 'error' in age_info:
        result['errors'].append(age_info['error'])
    else:
        result['age_days'] = age_info['age_days']
        # Rule: If age < 30 days, highly suspicious (+30 pts)
        if result['age_days'] < 30:
            result['risk_score'] += 30
            
    # 2. Fetch SSL
    ssl_info = get_ssl_details(domain)
    if 'error' in ssl_info:
        result['errors'].append(ssl_info['error'])
    else:
        result['days_until_expiry'] = ssl_info['days_until_expiry']
        result['issuer'] = ssl_info['issuer']
        
        # Rule: Short-lived SSL (<90 days) from free providers (+20 pts)
        free_providers = ["Let's Encrypt", "ZeroSSL", "Cloudflare"]
        is_free_issuer = any(provider.lower() in result['issuer'].lower() for provider in free_providers)
        if result['days_until_expiry'] < 90 and is_free_issuer:
            result['risk_score'] += 20
            
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python domain_ssl_checker.py <domain>")
        sys.exit(1)
        
    target = sys.argv[1]
    print(json.dumps(check_domain_and_ssl(target), indent=2))
