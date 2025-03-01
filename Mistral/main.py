import base64
import requests
import os
from mistralai import Mistral
from utils import *
import argparse

API_KEY_PATH="../../mistral_api_key.txt"
API_KEY=""
DEFAULT_MODEL="pixtral-12b-2409"

task_prompt: str = "The image displays an intelligence test question featuring a 3x3 grid with nine boxes, one of which is empty and marked with a question mark (?). Your task is to select the correct shape from six options (labeled A to F) to fill the empty box, completing the pattern that links all the shapes together. You must first give your explanation and then provide your answer at the end of your response in the format: 'The correct answer is: _'."


if __name__ == "__main__":
    with open(API_KEY_PATH, "r") as file:
        API_KEY = file.read
    
    ##############################################################################################################
    # Parse the arguments
    ##############################################################################################################
    parser = argparse.ArgumentParser(description="Arguments specficying the configuration, dataset type and output path.")

    parser.add_argument("--dataset_type", type=str, help="The type of dataset to be used. Example: --dataset_type 3_comp", required=True)
    parser.add_argument("--config", type=str, help="The configuration of the dataset to be used. Example: --config oa_os_oc", required=True)
    parser.add_argument("--output_path", type=str, help="The path to save the output data. Example: --output_path output/3_comp", required=True)
    parser.add_argument("--api_key", type=str, help="The API key for the Mistral API.", required=False, default=API_KEY)
    parser.add_argument("--model", type=str, help=f"The model to be used for the Mistral API. The default model is set to {DEFAULT_MODEL}", required=False, default=DEFAULT_MODEL)
    parser.add_argument("--num_runs", type=int, help="The number of runs to be executed.", required=False, default=3)

    ARGS = parser.parse_args()
    CONFIG = ARGS.config
    DATASET_TYPE = ARGS.dataset_type
    OUTPUT_PATH = ARGS.output_path
    MODEL = ARGS.model
    NUM_RUNS = ARGS.num_runs

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
    len_data = len(data) - 1 # The first row is the header
    print(f"Loaded {len_data} items from the data sheet.")
    assert len_data > 0, "No data loaded from the data sheet."
    
    # +1 as the index starts from 0
    assert int(data[-1][0]) + 1 == len_data, f"The number of items in the data sheet does not match the last index. Expected {len_data}, got {data[-1][0]}."

    ############################################################################################################
    # Mistral API
    ##############################################################################################################
    client = Mistral(api_key=ARGS.api_key)

    ##############################################################################################################
    # Prepare the messages
    ##############################################################################################################
    messages = []
    for i in range(1, len_data):
        item = data[i]
        id = item[0]
        img_path = f"../{item[1]}"
        correct_answer = item[2]

        # Debugging
        # print(f"ID: {id}, Image path: {img_path}, Correct answer: {correct_answer}")

        base64_image = encode_image(img_path)
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": task_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        )
    
    # for message in messages[0:1]:
    #     print(message)

    ##############################################################################################################
    # Generate the answers; run the model
    ##############################################################################################################
    responses = []
    for i in range(NUM_RUNS):
        print(f"Run {i + 1}/{NUM_RUNS}") 
        run_responses = []
        for message in messages:
            chat_response = client.chat.complete(
                model=ARGS.model,
                messages=[message]
            )
            run_responses.append(chat_response.choices[0].message.content)
        responses.append(run_responses)
    print("Completed the runs.")
    

    ##############################################################################################################
    # Save the answers
    ##############################################################################################################
    print("Saving the results.")
    for r in range(NUM_RUNS):
        results_data = []
        for i in range(1, len_data):
            item = data[i]
            response = responses[r][i - 1]

            idx = item[0]
            img_path = item[1]
            correct_answer = item[2]
            prediction = response.split("The correct answer is: ")[1]
            correct = "True" if prediction == correct_answer else "False"
            # "index", "image_path", "correct_answer", "prediction", "correct", "answer"
            results_data.append([idx, img_path, correct_answer, prediction, correct, response])
        save_results(results_data, OUTPUT_PATH + f"{CONFIG}_run_{r+1}_results.csv")


    
