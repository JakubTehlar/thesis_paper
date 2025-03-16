import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import globvars as gv 
import csv
import regex as re
from matplotlib import colors as mcolors
import os

MODEL="pixtral-12b-2409"
PROMPT="default_prompt"
DATASET="3_comp"
NUM_RUNS=10

re_patterns = [
    r'[Aa]nswer is[:]* [\*]*([A-Z])[\*]*',
    r'is likely[:]* [\*]*([A-Z])[\*]*',
    r'[Aa]nswer is[:]* ["]*([A-Z])["]*',
    r'is likely[:]* ["]*(A-Z)["]*',
    r'[Aa]nswe[a]*r[:]* [\*]*([A-Z][\*]*)',
    r'[Oo]ption[:]* [\*]*([A-Z][\*]*)',
    r'[Aa]nswe[a]*r[:]* ["]*([A-Z])["]*',
    r'[Oo]ption[:]* ["]*([A-Z])["]*',
    r'[Cc]orrect choice[:]* [\*]*([A-Z])[\*]*',
    r'[Cc]orrect option[:]* ["]*([A-Z])["]*',
]

def df_read_csv(input_filename) -> pd.DataFrame:
    df = pd.read_csv(input_filename)
    return df

def read_csv(input_filename):
    reader = csv.reader(open(input_filename, "r"), delimiter=",")
    data = []
    for row in reader:
        data.append(row)
    return data


def process_data(data) -> pd.DataFrame:
    df = pd.DataFrame(data)
    return df

def save_csv(df: pd.DataFrame, output_filename):
    try:
        df.to_csv(output_filename, index=False)
    except Exception as e:
        print(f"Could not save as csv: {e}")

def plot_data(x: list, y: list, title: str, xlabel: str, ylabel: str, y_limit: int = 100, colors: list = None, unique_colors: list=None, legend: list = None, note: str = None, save_path: str = None):
    assert len(x) == len(y), "Length of x and y must be equal"
    if colors is not None:
        assert len(x) == len(colors), "Length of x and colors must be equal"
    else:
        colors = ['skyblue'] * len(x)

    plt.figure(figsize=(12, 7))  
    bars = plt.bar(range(len(x)), y, color=colors, edgecolor='black')  
    plt.title(title)
    plt.xlabel(xlabel, loc="left", fontweight='bold', fontsize=10)
    plt.ylabel(ylabel, fontsize=10, fontweight='bold')
    plt.xticks([])  

    for bar, label in zip(bars, x):
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Center horizontally
            bar.get_height() + 13,  # Position in the middle of the bar
            label,  # The label text
            ha='center', va='center',  # Center alignment
            fontsize=10, color='black',
            rotation=90  
        )
    for bar, label in zip(bars, y):
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # Center horizontally
            bar.get_height() - 5,  # Position in the middle of the bar
            f"{label:.2f}%",  # The label text
            ha='center', va='center',  # Center alignment
            fontsize=9, color='black',
            rotation=45
        )


    # 50% line
    # plt.axhline(y=50, color='firebrick', linestyle='--', alpha=0.7)
    plt.axhline(y=50, color='firebrick', lw=2) 

    plt.grid(axis='y', linestyle='--', alpha=0.7)  
    plt.ylim(0, y_limit) 
    
    # legend
    legend_handles = [plt.Line2D([0], [0], color=color, lw=4) for color in unique_colors]
    plt.legend(legend_handles, legend, loc='upper right', bbox_to_anchor=(1.05,1.16))

    if note is not None:
        plt.text(
            0.5, 104,  
            note, 
            fontsize=10,
            color='black', 
            ha='center', va='center',
            wrap=True
        )

    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    else:
        plt.show()

def apply_regex(df: pd.DataFrame, regex: list = None) -> pd.DataFrame:
    patterns = regex if regex is not None else [r'[\*]*([A-Za-z])[\*]*']
    
    # Ensure a copy is used to avoid modifying the original dataframe
    new_df = df.copy()

    def process_row(row):
        for pattern in patterns:
            match = re.search(pattern, row["prediction"])
            if match:
                return match.group(1)
        return "No prediction"

    new_df["prediction"] = new_df["prediction"].astype(str).apply(process_row)
    new_df["correct"] = new_df["prediction"] == new_df["correct_answer"]

    return new_df


# Pass the dataframe to this function
# returns the number predictions in the correct format 
def process_correct_format(data: pd.DataFrame) -> int: 
    predictions_correct_format = 0
    for index, row in data.iterrows():
        prediction = row["prediction"].replace(".", "").strip()
        if prediction in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            predictions_correct_format += 1
    return predictions_correct_format

def process_correct_prediction(data: pd.DataFrame) -> int:
    correctly_predicted = 0
    for index, row in data.iterrows():
        if row["correct"]:
            correctly_predicted += 1
    return correctly_predicted

def correct_raw_data():
    for prompt in gv.PROMPTS:
        for dataset in gv.DATASETS:
            for config in gv.CONFIGS:
                path = f"../output/{MODEL}/{prompt}/{dataset}/{config}"
                regexed_path = f"../output/{MODEL}/{prompt}/{dataset}/{config}/regexed"
                if not os.path.exists(regexed_path): 
                    os.makedirs(regexed_path)

                for run in range(1, NUM_RUNS+1, 1):
                    input_filename = f"{path}/{config}_run_{run}_results.csv"
                    # Load data
                    data = df_read_csv(input_filename)

                    # Apply regex
                    regexed_df = apply_regex(data)

                    # Save regexed data
                    save_csv(regexed_df, f"{regexed_path}/{config}_run_{run}_results.csv")
                    print(f"Saved regexed data to {regexed_path}/{config}_run_{run}_results.csv")


if __name__ == "__main__":
    DEFAULT_PATH = f"../output/{MODEL}/{PROMPT}"

    # Apply regex to the data
    # Comment out the following code if already applied regex to the data
    correct_raw_data()
    

    color_3_comp_cf_raw = "limegreen"
    color_4_comp_cf_raw = "royalblue"
    color_3_comp_cp_raw = "darkorange"
    color_4_comp_cp_raw = "orchid"

    color_3_comp_cf_reg = "lime"
    color_4_comp_cf_reg = "cornflowerblue"
    color_3_comp_cp_reg = "orange"
    color_4_comp_cp_reg = "plum"

    # answer rate graphs
    NUM_QUESTIONS = 13
    QUESTIONS_TOTAL = NUM_QUESTIONS * NUM_RUNS
    legend = ["3 components\ndataset", "4 components\ndataset"]

    for prompt in gv.PROMPTS:
        x_labels = []
        y_values_correct_format_raw = []
        y_values_correct_format_regexed = []
        y_values_correct_predictions_raw = []
        y_values_correct_predictions_regexed = []
        colors_correct_format_raw = []
        colors_correct_format_regexed = []
        colors_correct_predictions_raw = []
        colors_correct_predictions_regexed = []

        for dataset in gv.DATASETS:
            for config in gv.CONFIGS:
                path = f"../output/{MODEL}/{prompt}/{dataset}/{config}"
                regexed_path = f"../output/{MODEL}/{prompt}/{dataset}/{config}/regexed"
                
                correct_prediction_format_raw = 0
                correct_prediction_format_regexed = 0
                correct_predictions_raw = 0
                correct_predictions_regexed = 0
                for run in range(NUM_RUNS):
                    raw_data = df_read_csv(f"{path}/{config}_run_{run + 1}_results.csv")
                    regexed_data = df_read_csv(f"{regexed_path}/{config}_run_{run + 1}_results.csv")
                    # Process each run
                    correct_prediction_format_raw += process_correct_format(raw_data)
                    correct_prediction_format_regexed += process_correct_format(regexed_data)
                    correct_predictions_raw += process_correct_prediction(raw_data)
                    correct_predictions_regexed += process_correct_prediction(regexed_data)
                
                x_labels.append(f"{config} ({dataset})")
                y_values_correct_format_raw.append(correct_prediction_format_raw/QUESTIONS_TOTAL*100)
                y_values_correct_format_regexed.append(correct_prediction_format_regexed/QUESTIONS_TOTAL*100)
                y_values_correct_predictions_raw.append(correct_predictions_raw/QUESTIONS_TOTAL*100)
                y_values_correct_predictions_regexed.append(correct_predictions_regexed/QUESTIONS_TOTAL*100)

                if dataset == "3_comp":
                    colors_correct_format_raw.append(color_3_comp_cf_raw)
                    colors_correct_format_regexed.append(color_3_comp_cf_reg)
                    colors_correct_predictions_raw.append(color_3_comp_cp_raw)
                    colors_correct_predictions_regexed.append(color_3_comp_cp_reg)
                else:
                    colors_correct_format_raw.append(color_4_comp_cf_raw)
                    colors_correct_format_regexed.append(color_4_comp_cf_reg)
                    colors_correct_predictions_raw.append(color_4_comp_cp_raw)
                    colors_correct_predictions_regexed.append(color_4_comp_cp_reg)
        # Correct format answer rate graph
        correct_format_raw_save_path = f"./{MODEL}_{prompt}_correct_format_raw.png"
        plot_data(x_labels, y_values_correct_format_raw, f"Correct Format Answer Rate", "Config", "Percentage", 100, colors_correct_format_raw, [color_3_comp_cf_raw, color_4_comp_cf_raw], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=correct_format_raw_save_path)

        correct_format_regexed_save_path = f"./{MODEL}_{prompt}_correct_format_regexed.png"
        plot_data(x_labels, y_values_correct_format_regexed, f"Correct Format Answer Rate\nAfter Applying\nRegex", "Config", "Percentage", 100, colors_correct_format_regexed, [color_3_comp_cf_reg, color_4_comp_cf_reg], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=correct_format_regexed_save_path)

        # Correct prediction graph
        correct_prediction_raw_save_path = f"./{MODEL}_{prompt}_correct_prediction_raw.png"
        plot_data(x_labels, y_values_correct_predictions_raw, f"Correct Prediction Rate", "Config", "Percentage", 100, colors_correct_predictions_raw, [color_3_comp_cp_raw, color_4_comp_cp_raw], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=correct_prediction_raw_save_path)

        correct_prediction_regexed_save_path = f"./{MODEL}_{prompt}_correct_prediction_regexed.png"
        plot_data(x_labels, y_values_correct_predictions_regexed, f"Correct Prediction Rate\nAfter Applying\nRegex", "Config", "Percentage", 100, colors_correct_predictions_regexed, [color_3_comp_cp_reg, color_4_comp_cp_reg], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=correct_prediction_regexed_save_path)
