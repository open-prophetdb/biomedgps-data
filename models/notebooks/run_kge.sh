#!/bin/bash

export MODEL_DIR=./models
mkdir -p ${MODEL_DIR}

# Get INDEX based on the number of files in the MODEL_DIR
INDEX=`find ${MODEL_DIR} -name '*.txt' | wc -l`

# You must change the DATASET according to your situation
for DATASET in "raw_drkg" "drkg" "drkg+hsdn"
do
    echo "Start training on ${DATASET} with INDEX ${INDEX}..."
    LOG_FILE=${MODEL_DIR}/${DATASET}_${INDEX}_log.txt

    if [ -f ${LOG_FILE} ]; then
        echo "File ${LOG_FILE} already exists, please delete it first."
        exit 1
    fi

    DGLBACKEND=pytorch dglke_train --dataset ${DATASET} --data_path ${DATASET} --data_files train.tsv valid.tsv test.tsv --format 'raw_udd_hrt' --model_name TransE_l2 --batch_size 2048 --neg_sample_size 256 --hidden_dim 400 --gamma 12.0 --lr 0.1 --max_step 100000 --log_interval 1000 --batch_size_eval 16 -adv --regularization_coef 1.00E-07 --test --valid --gpu 0 --num_proc 7 --neg_sample_size_eval 10000 --async_update --mix_cpu_gpu --save_path ./models --enable-wandb 2>&1 | tee ${LOG_FILE}
done