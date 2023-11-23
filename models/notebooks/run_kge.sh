#!/bin/bash

# You must change the DATASET_NAME according to your situation
export INDEX=0
export MODEL_DIR=./models
mkdir -p ${MODEL_DIR}

LOG_FILE=${MODEL_DIR}/biomedgps_${INDEX}_log.txt

if [ -f ${LOG_FILE} ]; then
    echo "File ${LOG_FILE} already exists, please delete it first."
    exit 1
fi

DGLBACKEND=pytorch dglke_train --dataset biomedgps --data_path ./data/train --data_files train.tsv valid.tsv test.tsv --format 'raw_udd_hrt' --model_name TransE_l2 --batch_size 2048 --neg_sample_size 256 --hidden_dim 400 --gamma 12.0 --lr 0.1 --max_step 100000 --log_interval 1000 --batch_size_eval 16 -adv --regularization_coef 1.00E-07 --test --valid --gpu 0 --num_proc 7 --neg_sample_size_eval 10000 --async_update --mix_cpu_gpu --save_path ./models 2>&1 | tee ${LOG_FILE}