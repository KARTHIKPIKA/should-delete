import argparse # for handling the command line interface arguments
import os # for filesystem
import sys # to modify import paths

# Go up 2 folders from this file, and add that folder to Python's search path so I can import anything from the project root.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio # for asynchronous calling (async parallel requests)
from langfuse.decorators import langfuse_context # it is open-source LLM observability & monitoring tool.
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm.asyncio import tqdm # This displays Progress bar for asynchronous tasks

from assessment import assess # Has LLM funtionality
# Below values are extracted for experiment configuration
from config import (
    EMBEDDING_DIM,
    FAISS_DB_PATH,
    METADATA_PATH,
    OUTPUTS_DIR,
    RESULTS_BY_CONFIGURATION_DIR,
    DEFAULT_TEST_SIZE,
    MAX_OPENAI_CONCURRENCY,
)


#load FAISS index and retrive top-k images
from preprocessing.vector_db import ImageEmbeddingIndex


# Custom argument parser that converts the command line key ,value pairs into python dictionary
class StoreDictKeyPair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        result_dict = {}
        for kv in values:
            key, value = kv.split("=", 1)  # Split only on the first '=' (for url like stuff)
            result_dict[key] = value
        setattr(namespace, self.dest, result_dict)


# core worker function
async def process_row(
    semaphore, # how many rows to process simultaneously
    row, # each patient x criterion pair
    use_refined_criteria=False,
    top_k_images=None,
    index=None,
    use_retrieval_guidelines=False,
    additional_trace_metadata=None,
    use_text_based_assessment=False,
):
    async with semaphore: # Concurrency control to prevent too many API calls
        sample = row.to_dict() # converts each row to dictionary

        criteria_column = (
            "criterion_description_refined"
            if use_refined_criteria
            else "criterion_description"
        )

        return await assess(
            criterion_description=sample[criteria_column],
            assessment_as_of_date=sample["assessment_as_of_date"],
            image_paths=sample["image_paths"],
            patient_id=sample["patient_id"],
            criterion_name=sample["criterion"],
            concatenated_medical_records=sample["concatenated_medical_records"],
            top_k_images=top_k_images,
            index=index,
            use_retrieval_guidelines=use_retrieval_guidelines,
            additional_trace_metadata=additional_trace_metadata,
            use_text_based_assessment=use_text_based_assessment,
        )



async def main():
    # Creates the CLI argument parser with a description
    parser = argparse.ArgumentParser(
        description="A script to assess eligibility criteria for patients in the dataset."
    )

    # Positional arguments
    parser.add_argument(
        "input_file_name",
        help="Where to find the dataframe containing references to images and ground truth. Relative to the outputs directory.",
    )
    parser.add_argument(
        "output_path",
        help="Where to save the results. Relative to the outputs/results_by_configuration directory.",
    )

    # Optional arguments with defaults
    parser.add_argument(
        "--test_size",
        type=float,
        default=DEFAULT_TEST_SIZE,
        help="The proportion of patients to use for testing (default: 0.9)",
    )

    parser.add_argument(
        "--top_k_images",
        type=int,
        default=None,
        help="The number of most relevant images to use for the assessment (default: None - all images)",
    )

    parser.add_argument(
        "--run_on_test_split",
        action="store_true",
        help="Whether to run the assessment on the test split of the data (default: False)",
    )

    parser.add_argument(
        "--use_refined_criteria",
        action="store_true",
        help="Whether to use the refined criteria descriptions (default: False)",
    )

    parser.add_argument(
        "--use_retrieval_guidelines",
        action="store_true",
        help="Whether to use the generated guidelines for images retrieval (default: False)",
    )

    parser.add_argument(
        "--use_text_based_assessment",
        action="store_true",
        help="Whether to use the text-based assessment rather than visual (default: False)",
    )

    # Accept arbitrary keyword arguments
    parser.add_argument(
        "--additional_trace_metadata",
        nargs="*",
        action=StoreDictKeyPair,
        metavar="KEY=VALUE",
        default={},
        help="Accepts any additional keyword arguments in the form KEY=VALUE.",
    )

    args = parser.parse_args()


    # initializes the Vector DB Index (if user want image retreival top_k provided , create ImageEmbeddingIndex , Load FAISS database from disk otherwise skip use all)
    if args.top_k_images:
        # Initialize the index
        index = ImageEmbeddingIndex(EMBEDDING_DIM)
        index.load_index(FAISS_DB_PATH.as_posix(), METADATA_PATH)
    else:
        index = None


    # creating output directory
    os.makedirs(RESULTS_BY_CONFIGURATION_DIR / args.output_path, exist_ok=True)


    # loads input data from pickle file into a pandas Dataframe
    print("Loading input dataframe...")
    df = pd.read_pickle(OUTPUTS_DIR / (args.input_file_name + ".pkl"))
    

    print("Split patients into train and test sets...")
    train_patients, _ = train_test_split(
        df.patient_id.unique(), test_size=args.test_size, random_state=0
    )


    # adds "split" Column to each row and marks patient as "train"/"test"
    df["split"] = df["patient_id"].apply(
        lambda x: "train" if x in train_patients else "test"
    )


    # Filters the dataframe to keep only train or test rows based on CLI flag
    if args.run_on_test_split:
        df = df[df["split"] == "test"]
    else:
        df = df[df["split"] == "train"]


    print(f"Assessing eligibility criteria ({MAX_OPENAI_CONCURRENCY} in parallel)...")
    semaphore = asyncio.Semaphore(MAX_OPENAI_CONCURRENCY) # limits how many rows to process at same time
    tasks = [ 
        process_row(  # Each row becomes one async task
            semaphore,
            row,
            use_refined_criteria=args.use_refined_criteria,
            top_k_images=int(args.top_k_images) if args.top_k_images else None,
            index=index,
            use_retrieval_guidelines=args.use_retrieval_guidelines,
            additional_trace_metadata=args.additional_trace_metadata,
            use_text_based_assessment=args.use_text_based_assessment,
        )
        for _, row in df.iterrows()
    ]
    results = await tqdm.gather(*tasks) # runs all taks concurrently with progress bar

    df["is_met_predicted"] = [result[1] for result in results]
    df["generated_rationale"] = [result[0] for result in results]

    cols = [
        "patient_id",
        "criterion",
        "is_met",
        "is_met_predicted",
        "generated_rationale",
    ]

    print(f"Saving the results to outputs/{args.output_path}...")
    df[cols].to_csv(
        RESULTS_BY_CONFIGURATION_DIR / args.output_path / "results.csv", index=False
    )
    langfuse_context.flush() # making sure all monitoring logs are sent before script exits


if __name__ == "__main__":
    asyncio.run(main())
