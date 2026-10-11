"""Run the standard 10-epoch HERG training smoke test."""
import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/raw/HERG_Konda_2019.csv"))
    parser.add_argument("--name", default="HERG-Konda-2019-100-epochs")
    parser.add_argument("--checkpoint-dir", default="pretrained_models")
    parser.add_argument("--logdir", default="runs/herg-konda-2019-test")
    parser.add_argument("--device", default="cuda", help="Training device, such as cuda or cpu")
    parser.add_argument("--epochs", type=int, default=100) #10
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.8) # 0.8 means 0.2
    args = parser.parse_args()

    if not args.dataset.is_file():
        parser.error(f"Dataset does not exist: {args.dataset}")

    command = [
        "train",
        "--dataset", str(args.dataset),
        "--name", args.name,
        "--checkpoint_dir", args.checkpoint_dir,
        "--logdir", args.logdir,
        "--random_state", str(args.random_state),
        "--test_size", str(args.test_size),
        "--epochs", str(args.epochs),
        "--batch_size", str(args.batch_size),
        "--torch_device", args.device,
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
