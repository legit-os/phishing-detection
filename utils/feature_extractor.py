import urllib.parse
import tldextract
import ipaddress
import json
import sys

def extract_features(url: str) -> dict:
    """Extracts 17 numeric features from a raw URL exactly matching the model inputs."""
    # Ensure URL has a scheme for accurate parsing
    if not url.startswith('http://') and not url.startswith('https://'):
        # For parsing, default to http if missing
        parse_url = 'http://' + url
    else:
        parse_url = url
        
    parsed = urllib.parse.urlparse(parse_url)
    ext = tldextract.extract(parse_url)
    
    # 1. dom_len
    domain = ext.domain
    dom_len = len(domain)
    
    # 2. is_ip
    is_ip = 0
    try:
        ipaddress.ip_address(domain)
        is_ip = 1
    except ValueError:
        pass
        
    # 3. tld_len
    tld = ext.suffix
    tld_len = len(tld)
    
    # 4. subdom_cnt
    subdomain = ext.subdomain
    subdom_cnt = len([s for s in subdomain.split('.') if s]) if subdomain else 0
    
    # 5. digit_cnt
    digit_cnt = sum(c.isdigit() for c in url)
    
    # 6. qm_cnt
    qm_cnt = url.count('?')
    
    # 7. amp_cnt
    amp_cnt = url.count('&')
    
    # 8. dot_cnt
    dot_cnt = url.count('.')
    
    # 9. dash_cnt
    dash_cnt = url.count('-')
    
    # 10. under_cnt
    under_cnt = url.count('_')
    
    # Ratios
    url_len = len(url)
    if url_len == 0:
        url_len = 1 # Avoid division by zero
        
    # 11. letter_ratio
    letter_cnt = sum(c.isalpha() for c in url)
    letter_ratio = letter_cnt / url_len
    
    # 12. digit_ratio
    digit_ratio = digit_cnt / url_len
    
    # 13. spec_ratio
    special_cnt = sum(not c.isalnum() for c in url)
    spec_ratio = special_cnt / url_len
    
    # 14. is_https
    is_https = 1 if url.startswith('https://') else 0
    
    # 15. slash_cnt
    slash_cnt = url.count('/')
    
    # 16. path_len
    path_len = len(parsed.path)
    
    # 17. query_len
    query_len = len(parsed.query)
    
    return {
        'dom_len': dom_len,
        'is_ip': is_ip,
        'tld_len': tld_len,
        'subdom_cnt': subdom_cnt,
        'digit_cnt': digit_cnt,
        'qm_cnt': qm_cnt,
        'amp_cnt': amp_cnt,
        'dot_cnt': dot_cnt,
        'dash_cnt': dash_cnt,
        'under_cnt': under_cnt,
        'letter_ratio': letter_ratio,
        'digit_ratio': digit_ratio,
        'spec_ratio': spec_ratio,
        'is_https': is_https,
        'slash_cnt': slash_cnt,
        'path_len': path_len,
        'query_len': query_len
    }

if __name__ == '__main__':
    # Test script if run from command line
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.example.com/path?query=1"
    features = extract_features(test_url)
    print(json.dumps(features, indent=2))
