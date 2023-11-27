## Job Queue & Job


## Sweep

Sweep can be used to run a job on a set of hyperparameters and it can be run independently of the job queue and job.

```bash
# Write a sweep config file and a script to run, such as train.sh and wandb_sweep.yaml
# Run sweep
wandb sweep --project biomedgps-kge-auto wandb_sweep.yaml

# Run sweep agent
wandb agent biomedgps-kge-auto <sweep_id>

# NOTE: The sweep_id is printed when you run wandb sweep
# wandb.init() will be ignored when running a sweep.
```

