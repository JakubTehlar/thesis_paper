import csv
import os

configs = ["oa_os_oc", "oa_os_nc", "oa_ns_oc", "oa_ns_nc", "na_os_oc", "na_os_nc", "na_ns_oc", "na_ns_nc"]
dataset_types = ["3_comp", "4_comp"]

def save_csv(data, filename):
    with open(filename, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["index", "image_path", "answer"]) 
        for row in data:
            writer.writerow(row)

def create_data(images_path_local: str, answers_path_local: str, destination_path_images: str, config: str):
    # need to go through every .png file in the images_path_local directory
    # then, based on the "filename.png", we need to find the corresponding answer label in the answers_path_local
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
    DATASET_TYPE = "4_comp"
    # local paths
    local_dataset_path = f"../{DATASET_TYPE}/output_data/"
    local_answers_path = f"../{DATASET_TYPE}/output_data/answers/"
    local_answer_sheet_path = f"answers/{DATASET_TYPE}/answers.csv"
    
    # This path will be the image path in the answers.csv file
    destination_path_images = f"Datasets/{DATASET_TYPE}/output_data"
    # This path will be the path where the answers will be saved
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

