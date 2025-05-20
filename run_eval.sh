#!/usr/bin/env bash

# Get Path to this script's parent directory
BASE_DIR=$(dirname "$(realpath "$0")")
SESSION="PrivTrace"
SCRIPT="${BASE_DIR}/evaluate.py"
DATASETS=("PORTO" "GEOLIFE")
N_FOLDS=5
EPSILONS=(10.0)
#EPSILONS=(1 2 5)
ARGS="--custom-c"

# Create tmux session if it does not exist
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION"
fi

# Loop over datasets, folds, and epsilons
for dataset in "${DATASETS[@]}"; do
    for fold in $(seq 0 $((N_FOLDS - 1))); do
        for epsilon in "${EPSILONS[@]}"; do
            tmux new-window -t "$SESSION" -n "${dataset}_${fold}_${epsilon}" \
                "python $SCRIPT -m --dataset $dataset --fold $fold --epsilon $epsilon ${ARGS}; read"
        done
    done
done
