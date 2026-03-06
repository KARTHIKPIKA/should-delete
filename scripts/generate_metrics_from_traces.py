import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd

from config import RESULTS_AGGREGATED_DIR
from metrics import compute_metrics_by_group, plots, plot_costs, plot_latencies


def main():
    print("Loading input dataframe...")
    df = pd.read_csv(RESULTS_AGGREGATED_DIR / "all_results.csv")

    print("Generating metrics...")
    metrics_by_configuration = compute_metrics_by_group(
        df, ["top_k_images", "use_retrieval_guidelines"], "is_met", "is_met_predicted"
    )

    plots(metrics_by_configuration)

    metrics_by_configuration.to_csv(
        RESULTS_AGGREGATED_DIR / "metrics_by_configuration.csv",
        index=False,
    )

    metrics_by_configuration_and_criterion = compute_metrics_by_group(
        df,
        ["criterion_name", "top_k_images", "use_retrieval_guidelines"],
        "is_met",
        "is_met_predicted",
    )

    for criterion in metrics_by_configuration_and_criterion["criterion_name"].unique():
        criterion_metrics = metrics_by_configuration_and_criterion.loc[
            metrics_by_configuration_and_criterion["criterion_name"] == criterion
        ]
        plots(criterion_metrics, f"by_criterion/{criterion} ")

    metrics_by_configuration_and_criterion.to_csv(
        RESULTS_AGGREGATED_DIR / "metrics_by_configuration_and_criterion_name.csv",
        index=False,
    )
    
    plot_latencies(df)
    plot_costs(df)


if __name__ == "__main__":
    main()
