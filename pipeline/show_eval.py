"""
Pretty-print model evaluation metrics from models_registry.json.
Used by the Jenkins pipeline for the human-in-the-loop approval gate.
"""
import json
import sys
import os


def main():
    registry_path = sys.argv[1] if len(sys.argv) > 1 else "models/models_registry.json"

    if not os.path.exists(registry_path):
        print(f"ERROR: Registry file not found at {registry_path}")
        sys.exit(1)

    with open(registry_path) as f:
        registry = json.load(f)

    # Header
    header = f"{'Model':<22} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1 Score':>10}"
    separator = "-" * len(header)

    print("\n" + separator)
    print("  MODEL EVALUATION RESULTS (Test Set)")
    print(separator)
    print(header)
    print(separator)

    for entry in registry:
        m = entry["metrics"]
        print(
            f"{entry['model_name']:<22} "
            f"{m['accuracy']:>9.4f} "
            f"{m['precision']:>10.4f} "
            f"{m['recall']:>9.4f} "
            f"{m['f1_score']:>10.4f}"
        )

    print(separator + "\n")


if __name__ == "__main__":
    main()
