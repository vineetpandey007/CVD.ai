from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ML_ROOT.parent


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=str(REPO_ROOT), check=True)


def main() -> None:
    run([sys.executable, "ml/scripts/embed.py", "--device", "cuda"])
    run([sys.executable, "ml/scripts/train_embed_clf.py"])
    run([sys.executable, "ml/scripts/finetune.py", "--device", "cuda"])

    artifact_dir = ML_ROOT / "results" / "colab_artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for path in (ML_ROOT / "results").glob("*.json"):
        shutil.copy2(path, artifact_dir / path.name)
    checkpoint_src = ML_ROOT / "checkpoints" / "best_codebert"
    if checkpoint_src.exists():
        shutil.copytree(checkpoint_src, artifact_dir / "best_codebert", dirs_exist_ok=True)
    zip_path = ML_ROOT / "results" / "colab_artifacts.zip"
    if zip_path.exists():
        zip_path.unlink()
    shutil.make_archive(str(zip_path.with_suffix("")), "zip", str(artifact_dir))
    print(f"Artifacts ready at {zip_path}")


if __name__ == "__main__":
    main()
