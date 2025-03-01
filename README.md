# README

## Overview
This project runs a MistralAI model to evaluate its reasoning skills on I-RAVEN datasets. The script allows you to specify dataset type, configuration, and output path as command-line arguments.

## Requirements
- Python 3.8+
- `requests` library (install using `pip install -r requirements.txt`)
- MistralAI API key (store in `../../mistral_api_key.txt` or set as an environment variable using ```sh export MISTRAL_API_KEY='YOUR_KEY' ```)

## Usage
Run the script using the following command, using an `oa_os_oc` configuration of the `3_comp` dataset.
```sh
python3 main.py --dataset_type 3_comp --config oa_os_oc --output_path output/3_comp/
```

## Arguments
- `--dataset_type`: Specifies the type of dataset (e.g., `3_comp`, `4_comp`).
- `--config`: Defines the model configuration (e.g., `oa_os_oc`). 
- `--output_path`: Sets the output directory for the results.
- `--api_key`: Specifies the API KEY for MistralAI 
- `--model`: Specifies the model to be used. If you are going to use a fine-tuned model, it is necessary to add it. 
- `--num_runs`: Specifies the number of runs of the current setting. Default is set to `3`. 

## Output
Results will be saved in the specified `output_path` directory.

## License

