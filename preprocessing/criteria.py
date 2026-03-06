criteria_definition_raw = {
    "ABDOMINAL": "History of intra-abdominal surgery, small or large intestine resection, or small bowel obstruction",
    "ADVANCED_CAD": (
        "Advanced cardiovascular disease (CAD). For the purposes of this annotation, we define 'advanced' as "
        "having 2 or more of the following: "
        "• Taking 2 or more medications to treat CAD "
        "• History of myocardial infarction (MI) "
        "• Currently experiencing angina "
        "• Ischemia, past or present"
    ),
    "ALCOHOL_ABUSE": "Current alcohol use over weekly recommended limits",
    "ASP_FOR_MI": "Use of aspirin to prevent MI",
    "CREATININE": "Serum creatinine > upper limit of normal",
    "DIETSUPP_2MOS": "Taken a dietary supplement (excluding vitamin D) in the past 2 months",
    "DRUG_ABUSE": "Drug abuse, current or past",
    "ENGLISH": "Patient must speak English",
    "HBA1C": "Any hemoglobin A1c (HbA1c) value between 6.5% and 9.5%",
    "KETO_1YR": "Diagnosis of ketoacidosis in the past year",
    "MAJOR_DIABETES": (
        "Major diabetes-related complication. For the purposes of this annotation, we define 'major complication' "
        "(as opposed to 'minor complication') as any of the following that are a result of (or strongly correlated with) "
        "uncontrolled diabetes: "
        "• Amputation "
        "• Kidney damage "
        "• Skin conditions "
        "• Retinopathy "
        "• nephropathy "
        "• neuropathy"
    ),
    "MAKES_DECISIONS": "Patient must make their own medical decisions",
    "MI_6MOS": "MI in the past 6 months",
}


criteria_definition_refined = {
    "ABDOMINAL": "History of intra-abdominal surgery. This could include any form of intra-abdominal surgery, including but not limited to small/large intestine resection or small bowel obstruction.",
    "ADVANCED_CAD": (
        "Advanced cardiovascular disease (CAD). For the purposes of this annotation, we define 'advanced' as having 2 or more of the following: "
        "(a) Taking 2 or more medications to treat CAD (b) History of myocardial infarction (MI) (c) Currently experiencing angina (d) Ischemia, past or present. "
        "The patient must have at least 2 of these categories (a,b,c,d) to meet this criterion, otherwise the patient does not meet this criterion. "
        "For ADVANCED-CAD, be strict in your evaluation of the patient – if they just have cardiovascular disease, then they do not meet this criterion."
    ),
    "ALCOHOL_ABUSE": "Current alcohol use over weekly recommended limits.",
    "ASP_FOR_MI": "Use of aspirin for preventing myocardial infarction (MI).",
    "CREATININE": "Serum creatinine level above the upper normal limit.",
    "DIETSUPP_2MOS": (
        "Consumption of a dietary supplement (excluding vitamin D) in the past 2 months. To assess this criterion, go through the list of medications-and-supplements "
        "taken from the note. If a substance could potentially be used as a dietary supplement (i.e., it is commonly used as a dietary supplement, even if it is not explicitly stated as being used as such), "
        "then the patient meets this criterion. Be lenient and broad in what is considered a dietary supplement. For example, a 'multivitamin' and 'calcium carbonate' "
        "should always be considered dietary supplements if they are included in this list."
    ),
    "DRUG_ABUSE": "Current or past history of drug abuse.",
    "ENGLISH": (
        "Patient speaks English. Assume that the patient speaks English, unless otherwise explicitly noted. "
        "If the patient's language is not mentioned in the note, then assume they speak English and thus meet this criterion."
    ),
    "HBA1C": "Any hemoglobin A1c (HbA1c) value between 6.5% and 9.5%.",
    "KETO_1YR": "Diagnosis of ketoacidosis within the past year.",
    "MAJOR_DIABETES": (
        "Major diabetes-related complication. Examples of 'major complication' (as opposed to 'minor complication') include, but are not limited to, any of the following that are a result of "
        "(or strongly correlated with) uncontrolled diabetes: Amputation, Kidney damage, Skin conditions, Retinopathy, Nephropathy, Neuropathy. "
        "Additionally, if multiple conditions together imply a severe case of diabetes, then count that as a major complication."
    ),
    "MAKES_DECISIONS": (
        "Patient must make their own medical decisions. Assume that the patient makes their own medical decisions, unless otherwise explicitly noted. "
        "If there is no information provided about the patient's ability to make their own medical decisions, then assume they do make their own decisions and therefore meet this criterion."
    ),
    "MI_6MOS": "Myocardial infarction (MI) within the past 6 months.",
}
