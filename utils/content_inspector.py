import sys
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import tldextract
import re

def inspect_page_content(url: str) -> dict:
    """
    Fetches a live URL and inspects its HTML and JavaScript 
    for common phishing heuristics.
    """
    result = {
        'url': url,
        'has_hidden_login': False,
        'has_obfuscated_js': False,
        'suspicious_form_action': False,
        'risk_score': 0,
        'error': None
    }
    
    # Ensure scheme
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
        
    try:
        # Set a short timeout and headers to act like a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Hidden Forms (especially login forms)
        forms = soup.find_all('form')
        for form in forms:
            # Check if form is hidden
            style = form.get('style', '').lower()
            is_hidden = ('display: none' in style or 
                         'display:none' in style or 
                         'visibility: hidden' in style or 
                         'visibility:hidden' in style)
            
            # Check if it has a password field
            has_password = form.find('input', type='password') is not None
            
            if is_hidden and has_password:
                result['has_hidden_login'] = True
                result['risk_score'] += 3
                break
                
        # 2. Obfuscated Scripts
        scripts = soup.find_all('script')
        obfuscated_patterns = [
            r'\beval\(',
            r'\bunescape\(',
            r'document\.write\(\s*unescape',
            r'String\.fromCharCode'
        ]
        
        for script in scripts:
            if script.string:
                content = script.string
                # Long unspaced lines are common in obfuscation
                if max((len(line) for line in content.split('\n')), default=0) > 500:
                    result['has_obfuscated_js'] = True
                    result['risk_score'] += 1
                
                # Check for bad patterns
                for pattern in obfuscated_patterns:
                    if re.search(pattern, content):
                        result['has_obfuscated_js'] = True
                        result['risk_score'] += 2
                        break
                        
        # 3. Suspicious Form Actions
        page_domain = tldextract.extract(url).registered_domain
        for form in forms:
            action = form.get('action')
            if action and action.strip() != "":
                action_domain = tldextract.extract(urllib.parse.urljoin(url, action)).registered_domain
                # If form submits to a completely different registered domain
                if action_domain and action_domain != page_domain:
                    result['suspicious_form_action'] = True
                    result['risk_score'] += 3
                    break
                    
    except requests.exceptions.RequestException as e:
        result['error'] = str(e)
        
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python content_inspector.py <url>")
        sys.exit(1)
        
    test_url = sys.argv[1]
    print(f"Inspecting URL: {test_url}")
    
    findings = inspect_page_content(test_url)
    print(json.dumps(findings, indent=2))
