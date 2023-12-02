#!/bin/bash

if [ -z "$WANDB_ENTITY" ]; then
    echo "WANDB_ENTITY is not set"
    exit 1
fi

if [ -z "$WANDB_PROJECT" ]; then
    echo "WANDB_PROJECT is not set"
    exit 1
fi

if [ -z "$DATASET" ]; then
    echo "DATASET is not set"
    exit 1
fi

if [ -z "$MODEL_NAME" ]; then
    echo "MODEL_NAME is not set"
    exit 1
fi

if [ -z "$GPU_SEQ" ]; then
    echo "GPU_SEQ is not set"
    exit 1
fi

if [ -z "$NUM_PROC" ]; then
    echo "NUM_PROC is not set"
    exit 1
fi

# Generate a random string
RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
MODEL_PATH=${DATASET}_${MODEL_NAME}_${RANDOM_STRING}

# Get all arguments passed to this script.
DGLBACKEND=pytorch dglke_train --dataset ${DATASET} --data_path /data/biomedgps-data/wandb/data --data_files train.tsv valid.tsv test.tsv --format 'raw_udd_hrt' --enable-wandb --wandb-entity $WANDB_ENTITY --wandb-project $WANDB_PROJECT --neg_sample_size 256 --max_step 100000 --log_interval 1000 --batch_size_eval 16 -adv --regularization_coef 1.00E-07 --test --valid --gpu ${GPU_SEQ} --num_proc ${NUM_PROC} --neg_sample_size_eval 10000 --async_update --mix_cpu_gpu --save_path /data/biomedgps-data/wandb/models/${MODEL_PATH} --batch_size 2048 --model_name ${MODEL_NAME} "$@"
