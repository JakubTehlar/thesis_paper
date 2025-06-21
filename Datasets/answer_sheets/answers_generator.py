import csv
import os

datasets = ["oa_os_oc", "oa_os_nc", "oa_ns_oc", "oa_ns_nc", "na_os_oc", "na_os_nc", "na_ns_oc", "na_ns_nc"]
configs = ["center_single", "distribute_four", "distribute_nine",
           "in_center_single_out_center_single", "in_distribute_four_out_center_single",
           "left_center_single_right_center_single", "up_center_single_down_center_single"]
dataset_types = ["3_comp", "4_comp"]

def save_csv(data, filename):
    with open(filename, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["index", "image_path", "answer"]) 
        for row in data:
            writer.writerow(row)

def create_data(images_path_local: str, config: str, img_dir_in_csv: str):
    data = []
    index = 0

    for dataset in datasets:
        for config in configs:
            img_dir = os.path.join(images_path_local,  dataset, config)
            img_path = ""
            question_answer_path = ""
            answer = ""
            for filename in os.listdir(img_dir):
                if filename.endswith(".png"):
                    question = filename.split(".")[0]
                    img_path = os.path.join(img_dir, question + ".png")
                    question_answer_path = f"{images_path_local}{dataset}_{config}_{question}.txt"
                    with open(question_answer_path, "r") as f:
                        answer = f.read().replace("\n", "")
                    img_path_in_csv = os.path.join(img_dir_in_csv, dataset, config, question + ".png")
                    print(f"{index}, {img_path_in_csv}, {answer}")
                    data.append([index, img_path_in_csv, answer])
                    index += 1
    return data

if __name__ == "__main__":
    DATASET_TYPE = "3_comp"
    # local paths
    local_dataset_path = f"../{DATASET_TYPE}/output_data/"
    local_answers_path = f"../{DATASET_TYPE}/output_data/answers/"
    local_answer_sheet_path = f"answers/{DATASET_TYPE}/answers.csv"
    
    # This path will be the image path in the answers.csv file
    img_path_in_csv = f"Datasets/{DATASET_TYPE}/output_data"
    # This path will be the path where the answers will be saved
    save_answers_path = f"data/{DATASET_TYPE}/"

    # create directories if they don't exist
    for config in datasets:
        path = os.path.join(img_path_in_csv, config)
        if not os.path.exists(path):
            os.makedirs(path)

        answers = create_data(local_dataset_path, config, img_path_in_csv)
        save_path = f"./answers/{DATASET_TYPE}/answers.csv" 
        print("Saving answers to: ", save_path)
        save_csv(answers, save_path)

