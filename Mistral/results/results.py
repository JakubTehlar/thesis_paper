import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import globvars as gv 
import csv
import regex as re
import textwrap
from matplotlib import colors as mcolors

MODEL="pixtral-12b-2409"
PROMPT="default_prompt"
DATASET="3_comp"
NUM_RUNS=10

def df_read_csv(input_filename) -> pd.DataFrame:
    df = pd.read_csv(input_filename)
    return df

def read_csv(input_filename):
    reader = csv.reader(open(input_filename, "r"), delimiter=",")
    data = []
    for row in reader:
        data.append(row)
    return data

def apply_regex(df: pd.DataFrame, regex):
    pass

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


if __name__ == "__main__":
    DEFAULT_PATH = f"../output/{MODEL}/{PROMPT}"

    color_3_comp_ag = "limegreen"
    color_4_comp_ag = "royalblue"
    color_3_comp_cp = "darkorange"
    color_4_comp_cp = "orchid"

    # answer rate graphs
    NUM_QUESTIONS = 13
    QUESTIONS_TOTAL = NUM_QUESTIONS * NUM_RUNS
    legend = ["3 components\ndataset", "4 components\ndataset"]

    # correct prediction graph

    for prompt in gv.PROMPTS:
        x_labels_ag = []
        y_values_ag = []
        colors_ag = []

        x_labels_cp = []
        y_values_cp = []
        colors_cp = []
        for dataset in gv.DATASETS:
            for config in gv.CONFIGS:
                path = f"../output/pixtral-12b-2409/{prompt}/{dataset}/{config}"
                predictions_correct_format = 0
                correctly_predicted = 0

                for run in range(1, NUM_RUNS+1, 1):
                    input_filename = f"{path}/{config}_run_{run}_results.csv"
                    # Load data
                    data = df_read_csv(input_filename)


                    for index, row in data.iterrows():
                        prediction = row["prediction"].replace(".", "").strip()
                        if prediction in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                            predictions_correct_format += 1
                        # else:
                        #     print(f"Incorrect prediction in : {prompt}, {dataset}, {config}, {run}, {index}, {prediction}, {len(prediction)}")

                        if row["correct"] == 1:
                            correctly_predicted += 1
                        

                if dataset == "3_comp":
                    colors_ag.append(color_3_comp_ag)
                    colors_cp.append(color_3_comp_cp)
                else:
                    colors_ag.append(color_4_comp_ag)
                    colors_cp.append(color_4_comp_cp)
                x_labels_ag.append(f"{config} ({dataset})")
                y_values_ag.append(predictions_correct_format/QUESTIONS_TOTAL*100)

                x_labels_cp.append(f"{config} ({dataset})")
                y_values_cp.append(correctly_predicted/QUESTIONS_TOTAL*100)
                # print(f"Prompt: {prompt}, Dataset: {dataset}, Config: {config}, Correct Format Answer Rate: {predictions_correct_format/QUESTIONS_TOTAL*100}%")
        ag_save_path = f"./{MODEL}_{prompt}_answer_rate.png"
        plot_data(x_labels_ag, y_values_ag, f"Correct Format Answer Rate", "Config", "Percentage", 100, colors_ag, [color_3_comp_ag, color_4_comp_ag], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=ag_save_path)

        cp_save_path = f"./{MODEL}_{prompt}_correct_prediction.png"
        plot_data(x_labels_cp, y_values_cp, f"Correct Prediction Rate", "Config", "Percentage", 100, colors_cp, [color_3_comp_cp, color_4_comp_cp], legend, note=f"Prompt: {prompt}\nModel: {MODEL}", save_path=cp_save_path)
        print(f"Saved {ag_save_path} and {cp_save_path}")

