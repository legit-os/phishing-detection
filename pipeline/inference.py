import sys
import json
import os
import glob
import joblib
import pandas as pd

# Import utilities
from utils.phishtank_checker import check_url
from utils.domain_ssl_checker import check_domain_and_ssl
from utils.content_inspector import inspect_page_content
from utils.feature_extractor import extract_features

def get_latest_model_path(models_dir: str, model_name: str) -> str:
    """Finds the most recent .joblib file for the specified model."""
    search_pattern = os.path.join(models_dir, f"{model_name.lower()}_*.joblib")
    files = glob.glob(search_pattern)
    if not files:
        raise FileNotFoundError(f"No model found for '{model_name}' in {models_dir}")
    return sorted(files)[-1]

def run_inference(url: str, model_name: str, api_key: str = None, models_dir: str = 'models') -> dict:
    """
    Runs the end-to-end phishing detection inference pipeline using a normalized scoring system.
    Weights: Phishtank (Highest), Domain/SSL (2nd), Content Inspection (3rd), ML Prediction (4th).
    """
    result = {
        'url': url,
        'is_phishing': False,
        'total_risk_score': 0,
        'reason': '',
        'details': {}
    }
    
    # 1. Phishtank API Check (Highest Weight - Instant Override)
    is_phishtank_flagged = check_url(url, api_key)
    result['details']['phishtank_flagged'] = is_phishtank_flagged
    
    if is_phishtank_flagged:
        result['is_phishing'] = True
        result['total_risk_score'] = 100
        result['reason'] = 'Flagged by PhishTank database (Instant Override).'
        return result
        
    # --- Normalized Scoring System ---
    # Threshold for Phishing = 45 points
    # Domain/SSL: Max 50 pts (30 age, 20 SSL)
    # Content: Max 40 pts (15 hidden, 15 suspicious form, 10 obfuscated)
    # ML: Max 15 pts
    
    # 2. Domain & SSL Inspection (2nd Importance)
    ssl_results = check_domain_and_ssl(url)
    result['details']['domain_ssl_inspection'] = ssl_results
    ssl_risk_score = ssl_results.get('risk_score', 0)
    result['total_risk_score'] += ssl_risk_score
    
    # 3. Content & Code Inspection (3rd Importance)
    content_results = inspect_page_content(url)
    result['details']['content_inspection'] = content_results
    
    content_risk_score = 0
    if content_results.get('has_hidden_login'):
        content_risk_score += 15
    if content_results.get('suspicious_form_action'):
        content_risk_score += 15
    if content_results.get('has_obfuscated_js'):
        content_risk_score += 10
        
    result['total_risk_score'] += content_risk_score
    
    # 4. Machine Learning Prediction (4th Importance)
    features = extract_features(url)
    result['details']['extracted_features'] = features
    
    feature_order = [
        'dom_len', 'is_ip', 'tld_len', 'subdom_cnt', 'digit_cnt', 
        'qm_cnt', 'amp_cnt', 'dot_cnt', 'dash_cnt', 'under_cnt', 
        'letter_ratio', 'digit_ratio', 'spec_ratio', 'is_https', 
        'slash_cnt', 'path_len', 'query_len'
    ]
    
    feature_values = {k: features[k] for k in feature_order}
    df_features = pd.DataFrame([feature_values])
    
    try:
        model_path = get_latest_model_path(models_dir, model_name)
        model = joblib.load(model_path)
        
        ml_pred = int(model.predict(df_features)[0])
        result['details']['ml_prediction'] = ml_pred
        
        if ml_pred == 1:
            result['total_risk_score'] += 15
            
    except Exception as e:
        result['details']['ml_error'] = str(e)

    # --- Final Decision Evaluation ---
    if result['total_risk_score'] >= 45:
        result['is_phishing'] = True
        result['reason'] = f"Cumulative risk score reached threshold ({result['total_risk_score']} >= 45)."
    else:
        result['reason'] = f"Cumulative risk score is below threshold ({result['total_risk_score']} < 45). Appears legitimate."
        
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python inference.py <url> <model_name> [api_key] [models_dir]")
        sys.exit(1)
        
    url_input = sys.argv[1]
    model_input = sys.argv[2]
    api_key_input = sys.argv[3] if len(sys.argv) > 3 else None
    models_dir_input = sys.argv[4] if len(sys.argv) > 4 else 'models'
    
    final_result = run_inference(url_input, model_input, api_key_input, models_dir_input)
    print(json.dumps(final_result, indent=2))
