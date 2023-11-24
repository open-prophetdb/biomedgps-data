#!/bin/bash

export MODEL_DIR=./models
mkdir -p ${MODEL_DIR}

MODEL_NAME=TransE_l2

# You must change the DATASET according to your situation
for DATASET in "raw_drkg" "drkg" "drkg+hsdn"
do
    # Get INDEX based on the number of files in the MODEL_DIR
    INDEX=`find ${MODEL_DIR} -name "${MODEL_NAME}_${DATASET}_*.txt" | wc -l`
    echo "Start training on ${DATASET} with INDEX ${INDEX} & MODEL ${MODEL_NAME}..."
    LOG_FILE=${MODEL_DIR}/${MODEL_NAME}_${DATASET}_${INDEX}_log.txt

    if [ ${INDEX} -gt 0 ]; then
        # Check whether the user wants to continue training
        read -p "Continue training on ${DATASET} with INDEX ${INDEX} & MODEL ${MODEL_NAME}? [y/n] " yn
        case $yn in
            [Yy]* ) echo "Continue training...";;
            [Nn]* ) echo "Exit training..."; exit;;
            * ) echo "Please answer yes or no.";;
        esac
    fi

    if [ -f ${LOG_FILE} ]; then
        echo "File ${LOG_FILE} already exists, please delete it first."
        exit 1
    fi

    DGLBACKEND=pytorch dglke_train --dataset ${DATASET} --data_path ${DATASET} --data_files train.tsv valid.tsv test.tsv --format 'raw_udd_hrt' --model_name ${MODEL_NAME} --batch_size 2048 --neg_sample_size 256 --hidden_dim 400 --gamma 12.0 --lr 0.1 --max_step 100000 --log_interval 1000 --batch_size_eval 16 -adv --regularization_coef 1.00E-07 --test --valid --gpu 0 --num_proc 7 --neg_sample_size_eval 10000 --async_update --mix_cpu_gpu --save_path ./models --enable-wandb 2>&1 | tee ${LOG_FILE}
done