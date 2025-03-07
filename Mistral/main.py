import base64
import requests
import os
from mistralai import Mistral
from utils import *
import argparse
import time
from tqdm import tqdm

API_KEY_PATH="../../mistral_api_key.txt"
API_KEY=os.environ["MISTRAL_API_KEY"]
MODELS_URL = "https://api.mistral.ai/v1/models"
DEFAULT_MODEL="pixtral-12b-2409"
FINE_TUNED_MODELS = []
ALL_MODELS = [] + FINE_TUNED_MODELS

PROMPT="mistral_prompt"

task_prompt: str = "The image displays an intelligence test question featuring a 3x3 grid with nine boxes, one of which is empty and marked with a question mark (?). Your task is to select the correct shape from six options (labeled A to H) to fill the empty box, completing the pattern that links all the shapes together. You must first give your explanation and then provide your answer at the end of your response in the format: 'The correct answer is: _'."

mistral_prompt: str = "You are an IQ test solver. You are presented with an image of an IQ test question. The IQ test question is a\
    3x3 grid with nine boxes. The bottom-right box is empty and marked with a symbol 'x'. Following the instructions, you are to\
    deduce the pattern that links the shapes in the matrix and select the correct answer from the options provided under the matrix,\
    separated by a thick horizontal line, labeled A to H.\
    ### Instructions:\
    #1. Carefully observe the changes across each row, column, and diagonals, noting any consistent transformations (e.g., shape changes, rotations, or color shifts) that might follow a sequence or logical rule.\
    # 2. Look for common pattern types like rotation, mirroring, color shades, or element counting, explaining briefly why each might apply.\
    # 3. Identify any unique features in the shapes.\
    # 4. Eliminate options (A to H) that clearly do not match the observed patterns.\
    # 5. Select the correct shape that completes the pattern.\
    # Take your time with each step and be thorough in your reasoning. Describe the thinking process.\
    # Conclude with:\
    'The correct answer is: _'." 

# 1-shot prompt
mistral_prompt_1shot: str = "" 


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
    parser.add_argument("--num_runs", type=int, help="The number of runs to be executed.", required=False, default=3)

    ARGS = parser.parse_args()
    CONFIG = ARGS.config
    DATASET_TYPE = ARGS.dataset_type
    OUTPUT_PATH = ARGS.output_path
    MODEL = ARGS.model
    NUM_RUNS = ARGS.num_runs

    configs = ["na_ns_nc", "na_ns_oc", "na_os_nc", "na_os_oc", "oa_ns_nc", "oa_ns_oc", "oa_os_nc", "oa_os_oc"]
    dataset_types = ["3_comp", "4_comp"]

    assert CONFIG in configs, f"Invalid configuration: '{CONFIG}'."
    assert DATASET_TYPE in dataset_types, f"Invalid dataset type: '{DATASET_TYPE}'."
    assert OUTPUT_PATH is not None, "Output path not specified."

    print("Running the experiments with the following configurations:")
    print(f"Dataset type: {DATASET_TYPE}")
    print(f"Configuration: {CONFIG}")
    print(f"Output path: {OUTPUT_PATH}")
    print(f"Model: {MODEL}")
    print(f"Number of runs: {NUM_RUNS}")
    print("")

    ############################################################################################################
    # Mistral API
    ##############################################################################################################
    client = Mistral(api_key=ARGS.api_key)
    
    response = requests.get(MODELS_URL, headers = {"Authorization": f"Bearer {ARGS.api_key}"})
    if response.status_code == 200:
        models = response.json()
        for model in models["data"]:
            ALL_MODELS.append(model["id"])
    else:
        print(f"Failed to get the list of models. Status code: {response.status_code}")
    assert ARGS.model in ALL_MODELS, f"Model '{ARGS.model}' not found in the list of models. If the model is a fine-tuned one, add it separately."# Available models: {ALL_MODELS}."

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
                        "text": mistral_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }
        )
    
    ##############################################################################################################
    # Generate the answers; run the model
    ##############################################################################################################
    print("Starting the runs.")
    responses = []
    for i in tqdm(range(NUM_RUNS), desc="Running experiments", unit="run"):
        run_responses = []
        for message in tqdm(messages, desc=f"   Run {i + 1}/{NUM_RUNS}", unit="msg", leave=False):
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

    FINAL_PATH = os.path.join(OUTPUT_PATH, MODEL, PROMPT, CONFIG)
    os.makedirs(FINAL_PATH, exist_ok=True)

    for r in range(NUM_RUNS):
        results_data = []
        for i in range(1, len_data):
            item = data[i]
            response = responses[r][i - 1]

            idx = item[0]
            img_path = item[1]
            correct_answer = item[2]
            try:
                prediction = response.split("The correct answer is: ")[1]
            except:
                prediction = "-"
                print(f"Error: Could not extract the answer from the response: {response}")
            correct = "True" if prediction == correct_answer else "False"
            # "index", "image_path", "correct_answer", "prediction", "correct", "answer"
            results_data.append([idx, img_path, correct_answer, prediction, correct, response])
        save_results(results_data, FINAL_PATH + f"_run_{r+1}_results.csv")

    print(f"Experiment completed. Results saved to {FINAL_PATH}.")
    print()

    
