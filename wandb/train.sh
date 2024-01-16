#!/bin/bash

echo "All arguments passed to this script: $@"
# Build a new list of arguments, excluding the one we want to replace
ARGS=""

for arg in "$@"
do
    # Split the argument into key and value
    IFS='=' read -r key value <<< "$arg"

    if [ "$key" == "--hidden_dim" ]; then
        DIM=$value
    fi

    if [ "$key" == "--enable_embedding" ]; then
        ENABLE_EMBEDDING=$value
    fi

    if [ "$key" == "--lr" ]; then
        ARGS="$ARGS --lr $value"
    fi

    if [ "$key" == "--batch_size" ]; then
        ARGS="$ARGS --batch_size $value"
    fi

    if [ "$key" == "--wandb_entity" ]; then
        ARGS="$ARGS --wandb-entity $value"
    fi

    if [ "$key" == "--wandb_project" ]; then
        ARGS="$ARGS --wandb-project $value"
    fi

    if [ "$key" == "--dataset" ]; then
        DATASET=$value
        ARGS="$ARGS --dataset $value"
    fi

    if [ "$key" == "--model_name" ]; then
        MODEL_NAME=$value
        ARGS="$ARGS --model_name $value"
    fi

    if [ "$key" == "--gpu" ]; then
        ARGS="$ARGS --gpu $value"
    fi

    if [ "$key" == "--num_proc" ]; then
        ARGS="$ARGS --num_proc $value"
    fi

    if [ "$key" == "--data_path" ]; then
        ARGS="$ARGS --data_path $value"
    fi

    if [ "$key" == "--model_path" ]; then
        MODEL_PATH=$value
    fi

    if [ "$key" == "--neg_sample_size" ]; then
        ARGS="$ARGS --neg_sample_size $value"
    fi

    if [ "$key" == "--max_step" ]; then
        ARGS="$ARGS --max_step $value"
    fi

    if [ "$key" == "--log_interval" ]; then
        ARGS="$ARGS --log_interval $value"
    fi

    if [ "$key" == "--batch_size_eval" ]; then
        ARGS="$ARGS --batch_size_eval $value"
    fi

    if [ "$key" == "--regularization_coef" ]; then
        ARGS="$ARGS --regularization_coef $value"
    fi

    if [ "$key" == "--neg_sample_size_eval" ]; then
        ARGS="$ARGS --neg_sample_size_eval $value"
    fi
done

if [ "$ENABLE_EMBEDDING" == "True" ]; then
    ARGS="$ARGS --hidden_dim $value --entity-emb-file entities_embeddings_${DIM}.tsv --relation-emb-file relation_types_embeddings_${DIM}.tsv"
fi

# Generate a random string
RANDOM_STRING=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
MODEL_PATH="${MODEL_PATH}/${DATASET}_${MODEL_NAME}_${RANDOM_STRING}"
mkdir -p ${MODEL_PATH}

ARGS="$ARGS --save_path ${MODEL_PATH}"

echo "All arguments passed to dglke_train: $ARGS"
# Get all arguments passed to this script.
# More details at https://github.com/yjcyxky/dgl-ke
DGLBACKEND=pytorch dglke_train --data_files train.tsv valid.tsv test.tsv --format 'raw_udd_hrt' --enable-wandb -adv --test --valid --async_update --mix_cpu_gpu "$ARGS"
