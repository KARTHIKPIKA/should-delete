import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tqdm import tqdm # for progress bars

from config import OUTPUTS_DIR # imports output directory path from config file
from preprocessing import (
    process_xml_files,
    convert_medical_records_to_images,
    plug_criteria_definition,
    explode_criteria,
)


def main():
    parser = argparse.ArgumentParser(
        description="A script to convert XML files from Harvard's n2c2 dataset into images and a ground truth dataset."
    )

    # Positional arguments
    parser.add_argument(
        "output_file_name",
        help="Where to save the dataframe containing references to images and ground truth. Relative to the outputs directory.",
    )

    args = parser.parse_args()

    tqdm.pandas() # shows a progress bar when applying funtions to dataframe rows

    print("Converting XML files to dataframe...")
    df = process_xml_files()


    # for every row in dataframe it takes medical record text and converts it into images and saves them
    print("Converting medical records to images...")
    df["image_paths"] = df.progress_apply(convert_medical_records_to_images, axis=1)


    print("Exploding criteria...")
    df = explode_criteria(df) # if patient has multiple criteria then it splits them inot seperate rows
    df = plug_criteria_definition(df) # adds full description of each criterion to the dataframe

    df["is_met"] = df["is_met"].map({"met": True, "not met": False})

    assert (
        df.is_met.nunique() == 2
    ), "The 'is_met' column should have only two unique values."

    print(
        f"Saving the dataset to outputs/{args.output_file_name}.csv and outputs/{args.output_file_name}.pkl..."
    )
    cols = [
        "patient_id",
        "assessment_as_of_date",
        "criterion",
        "criterion_description",
        "criterion_description_refined",
        "concatenated_medical_records",
        "is_met",
        "image_paths",
    ]
    df[cols].to_csv(OUTPUTS_DIR / (args.output_file_name + ".csv"), index=False) # for human readable format
    df[cols].to_pickle(OUTPUTS_DIR / (args.output_file_name + ".pkl")) # preserves python objects like image paths perfectly


if __name__ == "__main__":
    main()
