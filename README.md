# MolGT

Target-agnostic graph transformer for binary molecular property prediction.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root:

```sh
uv sync                  # CPU
uv sync --extra cuda     # Optional: NVIDIA CUDA
```

**Bundled models:** AmesFormer-Pro has been retrained with the graph and attention fixes: held-out ROC-AUC 0.786 and balanced accuracy 72.8%. See [retraining results](reports/retraining-results.md). AmesFormer-Honma still contains legacy weights and needs revalidation. These checkpoints retain their historical names.

Predict with the bundled AmesFormer-Pro model:

```sh
uv run --no-sync inference --smiles 'CCO' --smiles 'c1ccccc1' --name AmesFormer-Pro
```

Run inference on every row of a dataset:

```sh
uv run --no-sync inference --dataset data/raw/Combined.xlsx --name AmesFormer-Pro
```

- **Model:** inference requires `--name` or `--checkpoint`.
- **Dataset:** a CSV/XLSX file with `smiles` and `target` (0/1) columns.
- **Splits:** inference uses all rows. Training uses benchmark training portions for `Combined`, `Honma_New`, `Hansen_New`, and `tox24_all`; other filenames use a random train/validation split. Pass only held-out rows when evaluating performance.
- **Targets:** the loader validates binary `target` values (`0` or `1`) and does not assume a particular property or target name beyond that column.
- **OGB:** the legacy loader accepts an `ogbg_molpcba` directory, but its multitask labels are not supported by the binary training/inference pipeline.
- **Cache:** graphs are cached automatically in `.amesformer-cache/` beside the dataset.

Train on the bundled dataset:

```sh
uv run --no-sync train --dataset data/raw/Combined.xlsx --name my-model
```

For the standard 10-epoch HERG smoke test, use the repository script instead of
copying the full list of options:

```sh
uv run --no-sync python scripts/train_herg.py
```

It reads `data/raw/HERG_Konda_2019.csv`, uses CUDA, writes the checkpoint to
`pretrained_models/HERG-Konda-2019-test.pt`, and writes TensorBoard logs to
`runs/herg-konda-2019-test/`. Use `--device cpu` for a CPU run or
`uv run --no-sync python scripts/train_herg.py --help` to override the dataset,
run name, epochs, batch size, split, or output paths.

The script is also a starting point for repeatable experiments. Copy it or
extend its argument list when adding a fresh dataset or changing model and
training parameters. New datasets must be CSV/XLSX files with `smiles` and
binary `target` columns. For example:

```sh
uv run --no-sync python scripts/train_herg.py \
  --dataset data/raw/my-target.csv \
  --name my-target-baseline \
  --logdir runs/my-target-baseline \
  --epochs 50 \
  --batch-size 64
```

The wrapper exposes common experiment settings such as dataset, device, split,
epochs, batch size, random state, checkpoint location, and log location. For
model architecture or optimizer changes, add the corresponding `train`
options to the wrapper's `subprocess` command, or run `train --help` and use
the full CLI directly. Keep a distinct `--name` and `--logdir` for each
experiment so checkpoints and TensorBoard results are not overwritten.

Prepare the environment once, then run commands with `--no-sync`:

```sh
# CPU
uv sync

# NVIDIA CUDA
uv sync --extra cuda
uv run --no-sync train --dataset data/raw/Combined.xlsx --name my-model --torch_device cuda
```

`uv sync --extra cuda` installs the CUDA PyTorch variant. The regular `uv run` command may synchronize the project again using the default dependency set and replace that choice with the CPU variant, so use `uv run --no-sync` after selecting CUDA. For CPU runs, `uv run --no-sync` is also safe once the environment has been synchronized. Use a new `--name` for a fresh training run. See `inference --help` or `train --help` via `uv run --no-sync` for options; training defaults are in [default_hparams.toml](default_hparams.toml).

## Preparing data

Input tables must contain:

```text
smiles,target
CCO,0
c1ccccc1,1
```

Targets must be non-missing binary values. Inference evaluates every row; training creates the configured train/validation split.

The historical Ames reconstruction is retained as a source-specific cleaning pipeline. It applies the original Ames label mappings and test-set checks, but writes all generated datasets using the model-facing `smiles,target` schema:

```sh
uv run --no-sync python data_cleaning/reconstruct_combined.py \
  --honma /path/to/Honma_New.xlsx \
  --test-reference /path/to/Honma_Ames_Test.xlsx
```

Generated files are written to `data/reconstructed/`. Use `combined_train_validation.csv` for training and `honma_test.csv` for evaluation. See [dataset reconstruction](reports/dataset-reconstruction.md) for the full output list and provenance details. New target datasets should use the generic `smiles,target` format directly rather than the Ames-specific reconstruction rules.

## Development

```sh
uv run --no-sync pytest
uv run --no-sync tensorboard --logdir runs
```

## Optional Rust acceleration

Python shortest paths are fast enough for typical molecules. For faster preprocessing, install [Rust](https://rustup.rs/) and a C compiler, then:

```sh
uv sync --extra rust                 # CPU
uv sync --extra cuda --extra rust    # CUDA
```

See [gnn-tools](gnn-tools/README.md) for details.

## Citation

This model is forked from AmesFormer, citing the published paper:

 [Paper](https://pubs.acs.org/crtoec/article/38/7/1167/3764632/AmesFormer-State-of-the-Art-Mutagenicity).

```bibtex
@article{thompson2025amesformer,
  author = {Thompson, Luke A. and Evans, Josiah G. and Matthews, Slade T.},
  title = {{AmesFormer}: State-of-the-Art Mutagenicity Prediction with Graph Transformers},
  journal = {Chemical Research in Toxicology},
  year = {2025},
  volume = {38},
  number = {7},
  pages = {1167--1182},
  doi = {10.1021/acs.chemrestox.4c00466},
  url = {https://doi.org/10.1021/acs.chemrestox.4c00466}
}
```
