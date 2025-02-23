import csv
import os

# "." is the directory where the main.py is located and will be run from on RCI cluster
# RPM images will be saved in "../data/3_comp" and "../data/4_comp"
# The answers will be saved in "../data/answers/3_comp/answers.csv" and "../data/answers/answers.csv"

# the answer csv file has the following structure:
# index, image_path, question, answer, type, A, B, C, D, E, F, G, H 

def save_csv(data, filename):
    with open(filename, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["index", "image_path", "question", "answer", 0, "A", "B", "C", "D", "E", "F", "G", "H"])
        for row in data:
            writer.writerow(row)

def create_data(images_path_local: str, answers_path_local: str, destination_path_images: str):
    # need to go through every .png file in the images_path_local directory
    # then, based on the "filename.png", we need to find the corresponding answer in the answers_path_local
    # as the answer will be saved under "answers/filename.txt" and containing the correct answer

    data = []
    index = 0
    for filename in os.listdir(images_path_local):
        if filename.endswith(".png"):
            image_path = os.path.join(destination_path_images, filename)
            question = filename.split(".")[0]
            answer_path = os.path.join(answers_path_local, question + ".txt")
            # print("Image path: ", image_path)
            # print("Question: ", question)
            with open(answer_path, "r") as file:
                answer = file.read().replace("\n", "")
            # print("Answer path: ", answer_path + " Answer: " + answer)

            final_image_path = os.path.join(destination_path_images, question + ".png")
            data.append([index, final_image_path, "holder", answer, "A", "B", "C", "D", "E", "F", "G", "H"])
            index += 1
    return data

if __name__ == "__main__":
    local_images_path = "../3_comp/output_data/"
    local_answers_path = "../3_comp/output_data/answers/"
    destination_path_images = "data/3_comp"
    local_answer_sheet_path = "answers/3_comp/answers.csv"
    answers = create_data(local_images_path, local_answers_path, destination_path_images)
    save_csv(answers, local_answer_sheet_path)
    print("Answers saved to: ", local_answer_sheet_path) 