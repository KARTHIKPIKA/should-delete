import re
from datetime import datetime
import untangle


def extract_date_from_record(record):

    # Regular expression to match the date
    date_regex = r"Record date:\s*(\d{4}-\d{2}-\d{2})"

    # Search for the date in the text
    match = re.search(date_regex, record)
    if match:
        # Extract the date string
        date_str = match.group(1)
        # Convert the date string to a datetime object
        return datetime.strptime(date_str, "%Y-%m-%d")
    else:
        return None


def parse_patient_record(xml_file_path):
    first_date = datetime(1900, 1, 1)
    obj = untangle.parse(xml_file_path)
    concatenated_medical_records = obj.PatientMatching.TEXT.cdata
    medical_records = concatenated_medical_records.split(
        "***************************************************************************************"
    )[:-1]
    max_record_date = max(
        extract_date_from_record(medical_record) or first_date
        for medical_record in medical_records
    )

    criteria = {}
    for tag in obj.PatientMatching.TAGS.children:
        criteria[tag._name] = tag["met"]
    return medical_records, concatenated_medical_records, max_record_date.strftime("%Y-%m-%d"), criteria
