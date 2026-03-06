from glob import glob
import os
import pandas as pd

from config import IMAGES_DIR, DATA_DIR
from .xml_parsing import parse_patient_record
from .image_generation import text_to_images
from .criteria import criteria_definition_raw, criteria_definition_refined


def process_xml_files():

    df = pd.DataFrame({"file_path": glob((DATA_DIR / "*.xml").as_posix())})
    df["patient_id"] = df["file_path"].apply(
        lambda x: os.path.basename(x).split(".")[0]
    )
    (
        df["medical_records"],
        df["concatenated_medical_records"],
        df["assessment_as_of_date"],
        df["criteria"],
    ) = zip(*df["file_path"].apply(parse_patient_record))
    return df


def convert_medical_records_to_images(row):
    files = []
    for medical_record_id, medical_record in enumerate(row["medical_records"]):
        images = text_to_images(medical_record)
        for page, img in enumerate(images):
            path = (
                IMAGES_DIR / f"{row["patient_id"]}_{medical_record_id}_{page + 1}.png"
            )
            img.save(path)
            files.append(path)
    return files


def plug_criteria_definition(df):
    df["criterion_description"] = df.criterion.map(criteria_definition_raw)
    df["criterion_description_refined"] = df.criterion.map(criteria_definition_refined)
    return df


def explode_criteria(df):
    m = (
        pd.DataFrame([*df["criteria"]], df.index)
        .stack()
        .rename_axis([None, "criterion"])
        .reset_index(1, name="is_met")
    )

    exploded_criteria = df.join(m)
    return exploded_criteria
