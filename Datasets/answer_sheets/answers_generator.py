import csv
import os

# "ml-rpm-bech/src/main.py"
# "ml-rpm-bench/data/"

# "." is the directory where the main.py is located and will be run from on RCI cluster
# RPM images will be saved in "../data/3_comp" and "../data/4_comp"
# The answers will be saved in "../data/answers/3_comp/answers.csv" and "../data/answers/4_comp/answers.csv"

# the answer csv file has the following structure:
# index, image_path, question, answer, type, A, B, C, D, E, F, G, H 

configs = ["oa_os_oc", "oa_os_nc", "oa_ns_oc", "oa_ns_nc", "na_os_oc", "na_os_nc", "na_ns_oc", "na_ns_nc"]

def save_csv(data, filename):
    with open(filename, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["index", "image_path", "answer"]) 
        for row in data:
            writer.writerow(row)

def create_data(images_path_local: str, answers_path_local: str, destination_path_images: str, config: str):
    # need to go through every .png file in the images_path_local directory
    # then, based on the "filename.png", we need to find the corresponding answer in the answers_path_local
    # as the answer will be saved under "answers/filename.txt" and containing the correct answer

    data = []
    index = 0
    for filename in os.listdir(images_path_local):
        if filename.endswith(".png"):
            question = filename.split(".")[0]
            if (question.startswith(config) == False):
                continue
            image_path = os.path.join(destination_path_images, filename)
            answer_path = os.path.join(answers_path_local, question + ".txt")
            # print("Image path: ", image_path)
            # print("Question: ", question)
            with open(answer_path, "r") as file:
                answer = file.read().replace("\n", "")
            # print("Answer path: ", answer_path + " Answer: " + answer)

            final_image_path = os.path.join(destination_path_images, question + ".png")
            data.append([index, final_image_path, answer]) 
            index += 1
    return data

if __name__ == "__main__":
    DATASET_TYPE = "3_comp"
    local_dataset_path = f"../{DATASET_TYPE}/output_data/"
    local_answers_path = f"../{DATASET_TYPE}/output_data/answers/"
    destination_path_images = f"Dataset/{DATASET_TYPE}/output_data"
    local_answer_sheet_path = f"answers/{DATASET_TYPE}/answers.csv"
    save_answers_path = f"data/{DATASET_TYPE}/"

    # create directories if they don't exist
    for config in configs:
        path = os.path.join(destination_path_images, config)
        if not os.path.exists(path):
            os.makedirs(path)
    # create the answers
        answers = create_data(local_dataset_path, local_answers_path, destination_path_images, config)
        
        save_path = os.path.join(save_answers_path, config, config + "_answers.csv")
        

        # create the file if it doesn't exist

        print("Saving answers to: ", save_path)
        save_csv(answers, save_path)

