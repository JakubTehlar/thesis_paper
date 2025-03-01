#!/bin/bash

# Datasets
datasets=("3_comp" "4_comp")

# Configurations
configs=("oa_os_oc" "oa_os_nc" "oa_ns_oc" "oa_ns_nc" "na_os_oc" "na_os_nc" "na_ns_oc" "na_ns_nc")

for dataset in "${datasets[@]}"; do
  for config in "${configs[@]}"; do
    python3 main.py --dataset_type "$dataset" --config "$config" --output_path "output/$dataset/$config" --num_runs 10
  done
done
