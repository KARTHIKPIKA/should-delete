import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import EMBEDDING_DIM, OUTPUTS_DIR, FAISS_DB_PATH, METADATA_PATH
from preprocessing.embeddings import generate_embedding
from preprocessing.vector_db import ImageEmbeddingIndex


def main():
    parser = argparse.ArgumentParser(
        description="A script to generate embeddings for images in the dataset and save them in a local FAISS DB."
    )

    # Positional arguments
    parser.add_argument(
        "input_file_name",
        help="Where to find the dataframe containing references to images. Relative to the outputs directory.",
    )

    args = parser.parse_args()

    print("Loading input dataframe...")
    df = pd.read_pickle(OUTPUTS_DIR / (args.input_file_name + ".pkl"))
    patients = df.drop_duplicates("patient_id")

    # Initialize the index ( Creates a fresh empty FAISS vector index with the correct embedding dimensions )
    index = ImageEmbeddingIndex(EMBEDDING_DIM)

    print("Embedding images and adding them to the index...")

    # for every patient's image (takes each image path , passes it to generate_embedding() -> convert imag to vector numbers , add those to FAISS index)
    index.add_images(
        patients,
        lambda image_path: generate_embedding(
            input_type="document", image_path=image_path
        ),
    )

    print("Saving the index...")
    # Save the index ( saves two files to disk )
    index.save_index(FAISS_DB_PATH.as_posix(), METADATA_PATH)


if __name__ == "__main__":
    main()
