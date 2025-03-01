import base64
import requests
import os
from mistralai import Mistral
from utils import *
import argparse

API_KEY="U3g8x7dBaIlNdoLnfgI81jyvtHLYZZCW"
DEFAULT_MODEL="pixtral-12b-2409"


# Path to your image
img_name = "oa_os_oc_center_single_RAVEN_9918_test.png"
image_path = "../Datasets/3_comp/output_data/" + img_name

# Getting the base64 string
base64_image = encode_image(image_path)

# Retrieve the API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"] if "MISTRAL_API_KEY" in os.environ else API_KEY

# Specify model
model = "pixtral-12b-2409"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

task_prompt: str = "The image displays an intelligence test question featuring a 3x3 grid with nine boxes, one of which is empty and marked with a question mark (?). Your task is to select the correct shape from six options (labeled A to F) to fill the empty box, completing the pattern that links all the shapes together. You must first give your explanation and then provide your answer at the end of your response in the format: 'The correct answer is: _'."

# Define the messages for the chat
# messages = [
#     {
#         "role": "user",
#         "content": [
#             {
#                 "type": "text",
#                 "text": task_prompt
#             },
#             {
#                 "type": "image_url",
#                 "image_url": f"data:image/jpeg;base64,{base64_image}" 
#             }
#         ]
#     }
# ]

# # Get the chat response
# chat_response = client.chat.complete(
#     model=model,
#     messages=messages
# )

# # Print the content of the response
# print(chat_response.choices[0].message.content)


if __name__ == "__main__":
    ##############################################################################################################
    # Parse the arguments
    ##############################################################################################################
    parser = argparse.ArgumentParser(description="Arguments specficying the configuration, dataset type and output path.")

    parser.add_argument("--dataset_type", type=str, help="The type of dataset to be used. Example: --dataset_type 3_comp", required=True)
    parser.add_argument("--config", type=str, help="The configuration of the dataset to be used. Example: --config oa_os_oc", required=True)
    parser.add_argument("--output_path", type=str, help="The path to save the output data. Example: --output_path output/3_comp", required=True)
    parser.add_argument("--api_key", type=str, help="The API key for the Mistral API.", required=False, default=API_KEY)
    parser.add_argument("--model", type=str, help=f"The model to be used for the Mistral API. The default model is set to {DEFAULT_MODEL}", required=False, default=DEFAULT_MODEL)

    ARGS = parser.parse_args()
    CONFIG = ARGS.config
    DATASET_TYPE = ARGS.dataset_type
    OUTPUT_PATH = ARGS.output_path

    configs = ["na_ns_nc", "na_ns_oc", "na_os_nc", "na_os_oc", "oa_ns_nc", "oa_ns_oc", "oa_os_nc", "oa_os_oc"]
    dataset_types = ["3_comp", "4_comp"]

    assert CONFIG in configs, f"Invalid configuration: {CONFIG}."
    assert DATASET_TYPE in dataset_types, f"Invalid dataset type: {DATASET_TYPE}."
    assert OUTPUT_PATH is not None, "Output path not specified."

    ##############################################################################################################
    # Load the data sheet
    # data/DATASET_TYPE/CONFIG/CONFIG_answers.csv
    ##############################################################################################################

    data_file_path = "../Datasets/answer_sheets/data/"
    base_img_path = "../Datasets/3_comp/output_data/"

    data = load_csv(data_file_path + f"{DATASET_TYPE}/{CONFIG}/{CONFIG}_answers.csv") 
    for item in data:
        print(item)
    

    ##############################################################################################################
    # Mistral API
    ##############################################################################################################


    ##############################################################################################################
    # Save the answers
    ##############################################################################################################

    
