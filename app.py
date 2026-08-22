import streamlit as st
import time
import os
import glob
import joblib
import pandas as pd
import requests

from utils.phishtank_checker import check_url
from utils.domain_ssl_checker import check_domain_and_ssl
from utils.content_inspector import inspect_page_content
from utils.feature_extractor import extract_features

def get_latest_model_path(models_dir: str, model_name: str) -> str:
    search_pattern = os.path.join(models_dir, f"{model_name.lower()}_*.joblib")
    files = glob.glob(search_pattern)
    if not files:
        raise FileNotFoundError(f"No model found for '{model_name}' in {models_dir}")
    return sorted(files)[-1]

st.set_page_config(page_title="Phishing Detection", page_icon="🎣", layout="centered")

st.title("🎣 Phishing URL Detector")
st.write("Analyze any URL against our multi-layered detection pipeline.")

# Sidebar
st.sidebar.header("Configuration")
model_choice = st.sidebar.selectbox("Select ML Model", ["RandomForest", "XGBoost", "LightGBM", "LogisticRegression", "DecisionTree"])
api_key = st.sidebar.text_input("PhishTank API Key (Optional)", type="password")

# Main Interface
url_input = st.text_input("Enter URL to analyze", placeholder="https://example.com")

if st.button("Analyze URL", type="primary"):
    if not url_input:
        st.warning("Please enter a URL.")
    else:
        st.subheader("Live Analysis Pipeline")
        
        # Pre-check if website is reachable
        try:
            with st.spinner("Verifying website exists..."):
                url_to_check = url_input if url_input.startswith(('http://', 'https://')) else f"http://{url_input}"
                # Using a generic header to bypass basic bot blockers, focusing just on connection
                requests.get(url_to_check, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.ConnectionError:
            st.error("🚨 This website cannot be reached or does not exist.")
            st.stop()
        except requests.exceptions.Timeout:
            st.error("🚨 Connection timed out. The website might be down.")
            st.stop()
        except requests.exceptions.RequestException:
            pass # If it's a 403, 404, or SSL error, it still exists, so we proceed.
        
        total_risk_score = 0
        instant_override = False
        
        # 1. Phishtank
        with st.status("1. Checking PhishTank Database...", expanded=True) as status_phish:
            st.write(f"Querying PhishTank for {url_input}")
            flagged = check_url(url_input, api_key if api_key else None)
            if flagged:
                st.error("⚠️ URL is flagged as malicious in PhishTank!")
                total_risk_score = 100
                instant_override = True
                status_phish.update(label="1. PhishTank Check - FAILED", state="error")
            else:
                st.success("✅ Not found in PhishTank.")
                status_phish.update(label="1. PhishTank Check - PASSED", state="complete")
                
        if instant_override:
            st.error("🚨 **FINAL RESULT: PHISHING** (Instant Override by PhishTank)")
            st.stop()
            
        # 2. Domain & SSL
        with st.status("2. Inspecting Domain Age & SSL...", expanded=True) as status_ssl:
            st.write("Fetching WHOIS and certificate data...")
            ssl_results = check_domain_and_ssl(url_input)
            st.json(ssl_results)
            ssl_risk = ssl_results.get('risk_score', 0)
            total_risk_score += ssl_risk
            if ssl_risk > 0:
                st.warning(f"Suspicious signals found. Risk Score += {ssl_risk}")
                status_ssl.update(label="2. Domain & SSL - WARNING", state="complete")
            else:
                st.success("Domain and SSL appear normal.")
                status_ssl.update(label="2. Domain & SSL - PASSED", state="complete")
                
        # 3. Content Inspection
        with st.status("3. Inspecting HTML/JS Content...", expanded=True) as status_content:
            st.write("Fetching live page content...")
            content_results = inspect_page_content(url_input)
            st.json(content_results)
            
            content_risk_score = 0
            if content_results.get('has_hidden_login'): content_risk_score += 15
            if content_results.get('suspicious_form_action'): content_risk_score += 15
            if content_results.get('has_obfuscated_js'): content_risk_score += 10
            
            total_risk_score += content_risk_score
            
            if content_risk_score > 0:
                st.warning(f"Suspicious HTML/JS found. Risk Score += {content_risk_score}")
                status_content.update(label="3. Content Inspection - WARNING", state="complete")
            else:
                st.success("No suspicious HTML/JS heuristics detected.")
                status_content.update(label="3. Content Inspection - PASSED", state="complete")
                
        # 4. ML Prediction
        with st.status(f"4. Running {model_choice} ML Prediction...", expanded=True) as status_ml:
            st.write("Extracting URL features...")
            features = extract_features(url_input)
            st.json(features)
            
            feature_order = [
                'dom_len', 'is_ip', 'tld_len', 'subdom_cnt', 'digit_cnt', 
                'qm_cnt', 'amp_cnt', 'dot_cnt', 'dash_cnt', 'under_cnt', 
                'letter_ratio', 'digit_ratio', 'spec_ratio', 'is_https', 
                'slash_cnt', 'path_len', 'query_len'
            ]
            feature_values = {k: features[k] for k in feature_order}
            df_features = pd.DataFrame([feature_values])
            
            st.write("Loading model and predicting...")
            try:
                model_path = get_latest_model_path('models', model_choice)
                model = joblib.load(model_path)
                ml_pred = int(model.predict(df_features)[0])
                
                if ml_pred == 1:
                    total_risk_score += 15
                    st.warning("ML Model predicts: PHISHING (+15 Risk Score)")
                    status_ml.update(label="4. ML Prediction - WARNING", state="complete")
                else:
                    st.success("ML Model predicts: LEGITIMATE")
                    status_ml.update(label="4. ML Prediction - PASSED", state="complete")
            except Exception as e:
                st.error(f"Model Error: {e}")
                status_ml.update(label="4. ML Prediction - ERROR", state="error")
                
        # FINAL DECISION
        st.markdown("---")
        st.header("Final Verdict")
        
        if total_risk_score >= 45:
            st.error(f"🚨 **PHISHING DETECTED** 🚨")
            st.write(f"Cumulative Risk Score: **{total_risk_score} / 100** (Threshold: 45)")
        else:
            st.success(f"✅ **LEGITIMATE SITE** ✅")
            st.write(f"Cumulative Risk Score: **{total_risk_score} / 100** (Threshold: 45)")
