import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import RESULTS_BY_CONFIGURATION_DIR
from metrics import compute_metrics_by_group, generate_and_save_metrics

def main():
    parser = argparse.ArgumentParser(description="A script to generate metrics.")

    # Positional arguments
    parser.add_argument(
        "input_path",
        help="Directory to find the results of the assessment. Metrics will be saved in the same dir. Relative to the outputs directory.",
    )

    args = parser.parse_args()

    print("Loading input dataframe...")
    df = pd.read_csv(RESULTS_BY_CONFIGURATION_DIR / args.input_path / "results.csv")
    df = df.loc[df.patient_id != "sample"]

    print("Calculating metrics...")
    generate_and_save_metrics(df.is_met, df.is_met_predicted, ["Not Met", "Met"], RESULTS_BY_CONFIGURATION_DIR / args.input_path / "confusion_matrix.png")
    compute_metrics_by_group(df, "criterion", "is_met", "is_met_predicted").to_csv(RESULTS_BY_CONFIGURATION_DIR / args.input_path / "metrics_by_group.csv", index=False)

if __name__ == "__main__":
    main()
