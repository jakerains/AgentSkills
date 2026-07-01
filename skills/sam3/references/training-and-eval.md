# SAM 3 Training And Evaluation

Use this reference for fine-tuning and benchmark evaluation with `sam3/train/train.py`.

## Install Training Dependencies

From the SAM3 repo root:

```bash
pip install -e ".[train]"
```

## Core Training Commands

Examples from upstream configs:

```bash
python sam3/train/train.py -c configs/roboflow_v100/roboflow_v100_full_ft_100_images.yaml
python sam3/train/train.py -c configs/odinw13/odinw_text_only_train.yaml
```

Force local execution and GPU count:

```bash
python sam3/train/train.py -c configs/roboflow_v100/roboflow_v100_full_ft_100_images.yaml --use-cluster 0 --num-gpus 1
python sam3/train/train.py -c configs/roboflow_v100/roboflow_v100_full_ft_100_images.yaml --use-cluster 0 --num-gpus 4
```

Cluster launch with SLURM options:

```bash
python sam3/train/train.py -c configs/roboflow_v100/roboflow_v100_full_ft_100_images.yaml --use-cluster 1 --partition gpu_partition --account my_account --qos high_priority --num-gpus 8 --num-nodes 2
```

## Config Areas To Update First

- `paths.dataset_root` and other dataset paths
- `paths.experiment_log_dir`
- Checkpoint initialization and resume paths
- Launcher settings (`num_nodes`, `gpus_per_node`)
- Submitit/cluster settings when `--use-cluster 1`

## Monitoring Outputs

Typical output layout:

```text
experiment_log_dir/
  config.yaml
  config_resolved.yaml
  checkpoints/
  tensorboard/
  logs/
  submitit_logs/
```

Inspect progress with:

```bash
tensorboard --logdir /path/to/experiment_log_dir/tensorboard
```

## Evaluation Commands

Run eval configs directly:

```bash
python sam3/train/train.py -c configs/roboflow_v100/roboflow_v100_eval.yaml
python sam3/train/train.py -c configs/odinw13/odinw_text_only.yaml
```

For SA-Co benchmarks, update `sam3/train/configs/eval_base.yaml` paths first, then run the appropriate config under:

- `configs/gold_image_evals/`
- `configs/silver_image_evals/`

Example:

```bash
python sam3/train/train.py -c configs/gold_image_evals/sam3_gold_image_metaclip_nps.yaml --use-cluster 0 --num-gpus 1
```

Offline cgF1 evaluation example:

```bash
python scripts/eval/standalone_cgf1.py --pred_file /path/to/coco_predictions_segm.json --gt_files /path/to/annotations/gold_metaclip_merged_a_release_test.json /path/to/annotations/gold_metaclip_merged_b_release_test.json /path/to/annotations/gold_metaclip_merged_c_release_test.json
```

## SA-Co/VEval Notes

- Follow upstream docs in `scripts/eval/veval/README.md`.
- Keep frame extraction and annotation versions aligned to reduce frame-shift issues.
- Document any dropped videos when using YouTube-sourced data.

## Failure Patterns

- Diverging training jobs:
Lower learning rate or inspect dataset quality and shot selection.
- Empty/weak predictions:
Verify prompt text quality, checkpoint source, and confidence thresholds.
- Non-reproducible evals:
Record exact config, dataset snapshot, and annotation preprocessing steps.
