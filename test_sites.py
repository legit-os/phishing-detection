import sys
import json
sys.path.append('.') # Ensure utils and pipeline can be found

from pipeline.inference import run_inference

sites_to_test = [
    "https://github.com",
    "https://microsoft.com",
    "http://secure-update-login-verification.com",
    "http://mybank-alert-security-update.com"
]

results = []

for site in sites_to_test:
    print(f"Testing {site}...")
    try:
        res = run_inference(site, "randomforest")
        results.append(res)
    except Exception as e:
        results.append({"url": site, "error": str(e)})

print("\n--- ALL RESULTS ---")
print(json.dumps(results, indent=2))
