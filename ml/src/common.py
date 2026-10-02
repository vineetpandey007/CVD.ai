import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

SEED = 42


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load_config(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)
