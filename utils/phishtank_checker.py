import sys
import json
import requests
import base64

def check_url(url: str, app_key: str = None) -> bool:
    """
    Checks a URL against the PhishTank database using their API.
    Returns True if the URL is a verified phishing site, False otherwise.
    """
    api_url = "http://checkurl.phishtank.com/checkurl/"
    
    # Base64 encode the URL to handle special characters properly
    b64_url = base64.b64encode(url.encode('utf-8')).decode('utf-8')
    
    data = {
        'url': b64_url,
        'format': 'json'
    }
    
    if app_key:
        data['app_key'] = app_key
        
    headers = {
        'User-Agent': 'phishtank/phishing-detection-agent'
    }
    
    try:
        # 10s timeout to avoid hanging the inference process
        response = requests.post(api_url, data=data, headers=headers, timeout=10)
        
        # If rate limited, HTTP 509 is returned. raise_for_status() catches this.
        response.raise_for_status()
        
        result = response.json()
        
        if 'results' in result:
            in_db = result['results'].get('in_database')
            is_valid = result['results'].get('valid')
            
            # Robustly parse truthy values
            in_database_bool = in_db is True or str(in_db).lower() in ('true', 'y', '1')
            is_valid_bool = is_valid is True or str(is_valid).lower() in ('true', 'y', '1')
            
            if in_database_bool and is_valid_bool:
                return True
                
        return False
        
    except Exception as e:
        # In case of API failure, timeout, or rate limiting,
        # fallback to False so the ML models can still analyze the URL.
        print(f"PhishTank API error: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python phishtank_checker.py <url> [app_key]")
        sys.exit(1)
        
    test_url = sys.argv[1]
    test_key = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Checking URL: {test_url}")
    is_phishing = check_url(test_url, test_key)
    
    print(f"Result: {'PHISHING' if is_phishing else 'NOT FOUND or NOT VERIFIED'}")
