from async_lru import alru_cache # to cache the results
from langfuse.decorators import observe, langfuse_context
import os

from config import PROMPTS_DIR
from preprocessing.embeddings import generate_embedding
from .utils import call_openai_async, image_to_base64


def generate_medical_records_message(
    image_paths=None, concatenated_medical_records=None
):  
    # if images are provided then converts each image to base 64 and packages as image messages.
    if image_paths is not None:
        return [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_to_base64(image_path)}"
                },
            }
            for image_path in image_paths
        ]
    # if text is provided , it packages as plain text message
    elif concatenated_medical_records is not None:
        return [
            {
                "type": "text",
                "text": concatenated_medical_records,
            }
        ]
    else:
        raise ValueError(
            "Either image_paths or concatenated_medical_records must be provided"
        )


# Tracks the entire function as a trace , every call is logged with name
@observe(name="Patient ID - Harvard Dataset")
async def assess(
    criterion_description,
    assessment_as_of_date,
    image_paths,
    patient_id,
    criterion_name,
    concatenated_medical_records,
    top_k_images=None,
    index=None,
    use_retrieval_guidelines=False,
    additional_trace_metadata=None,
    use_text_based_assessment=False,
):

    with open(PROMPTS_DIR / "all_in_one_assessment_system.txt") as f:
        all_in_one_assessment_system_prompt = f.read()
    with open(PROMPTS_DIR / "all_in_one_assessment_user.txt") as f:
        all_in_one_assessment_user_prompt = f.read()

    if additional_trace_metadata is None:
        additional_trace_metadata = {}

    if top_k_images:

        most_relevant_images = []


        # generate guidelines for each criterion , for each guideline search vector DB for relevant images , combine all remove duplicates
        if use_retrieval_guidelines:
            guidelines = await generate_guidelines(criterion_description)

            for guideline in guidelines:
                index_answer = index.search(
                    guideline,
                    lambda query: generate_embedding(input_type="document", text=query),
                    patient_id,
                    top_k_images,
                )
                most_relevant_images.extend(
                    [file["file_name"] for file in index_answer]
                )
            most_relevant_images = list(set(most_relevant_images))
        
        # without guidelines , search vector DB using the criterion description as query
        else:
            index_answer = index.search(
                criterion_description,
                lambda query: generate_embedding(input_type="document", text=query),
                patient_id,
                top_k_images,
            )
            most_relevant_images = [file["file_name"] for file in index_answer]

        # filters image_paths to keep only the most relevant ones
        image_paths = [
            image_path
            for image_path in image_paths
            if os.path.basename(image_path).split(".")[0] in most_relevant_images
        ]


    # Decides whether to send text or images to OpenAI
    if use_text_based_assessment:
        medical_records_message = generate_medical_records_message(
            concatenated_medical_records=concatenated_medical_records
        )
    else:
        medical_records_message = generate_medical_records_message(
            image_paths=image_paths
        )


    # Full message structure for OpenAI
    messages = [
        {"role": "developer", "content": all_in_one_assessment_system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Here are the medical records of the patient:",
                }
            ]
            + medical_records_message
            + [
                {
                    "type": "text",
                    "text": all_in_one_assessment_user_prompt.format(
                        criterion_description=criterion_description,
                        assessment_as_of_date=assessment_as_of_date,
                    ),
                },
            ],
        },
    ]

    answer = await call_openai_async(
        model="o1",
        messages=messages,
        response_format={"type": "json_object"},
        convert_json_answer_to_dict=True,
    )

    metadata = {
        "patient_id": patient_id,
        "criterion_name": criterion_name,
        "top_k_images": top_k_images,
        "use_retrieval_guidelines": use_retrieval_guidelines,
        "images_used": len(image_paths),
    }

    metadata.update(additional_trace_metadata)

    langfuse_context.update_current_trace(metadata=metadata)

    return answer["rationale"], answer["is_met"]


@alru_cache(maxsize=128)
async def generate_guidelines(criterion_description):
    with open(PROMPTS_DIR / "guidelines_generation_system.txt") as f:
        guidelines_generation_system = f.read()

    with open(PROMPTS_DIR / "guidelines_generation_user.txt") as f:
        guidelines_generation_user = f.read()

    messages = [
        {"role": "system", "content": guidelines_generation_system},
        {
            "role": "user",
            "content": guidelines_generation_user.format(
                criterion_description=criterion_description
            ),
        },
    ]

    answer = await call_openai_async(
        model="gpt-4o",
        messages=messages,
        response_format={"type": "json_object"},
        convert_json_answer_to_dict=True,
    )

    return answer["guidelines"]
