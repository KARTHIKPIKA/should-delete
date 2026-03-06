import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd

from config import OUTPUTS_DIR, RESULTS_AGGREGATED_DIR


def process_langfuse_traces(traces, ground_truth):
    # First, we load JSONs into dictionaries
    traces.output = traces.output.apply(json.loads)
    traces.metadata = traces.metadata.apply(json.loads)

    # Then, we filter the traces that don't have the right metadata
    traces = traces.loc[traces.metadata.apply(len) == 5].reset_index(drop=True)

    # Then, we extract the metadata into columns
    for metadata_col in traces.loc[0, ["metadata"]].squeeze().keys():
        traces[metadata_col] = traces.metadata.apply(lambda x: x[metadata_col])
    traces["patient_id"] = traces.patient_id.astype(str)

    # Then, we extract the input and output into columns
    traces["rationale"] = traces.output.apply(lambda x: x[0])
    traces["is_met_predicted"] = traces.output.apply(lambda x: x[1])

    # Then, we keep only the latest occurence of each patient_id x criterion x configuration
    traces = (
        traces.sort_values("timestamp", ascending=False)
        .drop_duplicates("metadata")
        .reset_index(drop=True)
    )

    # Then, we merge the ground truth with the traces
    ground_truth["criterion_name"] = ground_truth.criterion
    ground_truth["total_images"] = ground_truth.image_paths.apply(len)

    merged = traces.merge(
        ground_truth, how="inner", on=["patient_id", "criterion_name"]
    )

    # And finally, we keep only the columns of interest
    columns = [
        "id",
        "patient_id",
        "criterion_name",
        "top_k_images",
        "use_retrieval_guidelines",
        "timestamp",
        "latency",
        "inputCost",
        "outputCost",
        "totalCost",
        "inputTokens",
        "outputTokens",
        "totalTokens",
        "is_met",
        "is_met_predicted",
        "rationale",
        "images_used",
        "total_images",
    ]

    return merged[columns]


def main():
    parser = argparse.ArgumentParser(
        description="A script to generate metrics using LangFuse traces."
    )

    # Positional arguments
    parser.add_argument(
        "ground_truth_input_path",
        help="Where to find the dataframe containing references to images and ground truth. Relative to the outputs directory.",
    )

    parser.add_argument(
        "langfuse_traces_input_path",
        help="File to find the LangFuse traces. Relative to the outputs/results_aggregated directory.",
    )

    args = parser.parse_args()

    print("Loading input dataframe...")
    ground_truth = pd.read_pickle(OUTPUTS_DIR / (args.ground_truth_input_path + ".pkl"))
    traces = pd.read_csv(RESULTS_AGGREGATED_DIR / args.langfuse_traces_input_path)

    print("Processing LangFuse traces...")
    process_langfuse_traces(traces, ground_truth).to_csv(
        RESULTS_AGGREGATED_DIR / "all_results.csv", index=False
    )


if __name__ == "__main__":
    main()
