import os

import numpy as np
from scipy.special import ellipeinc
from tqdm import tqdm

from src.config import STEP

_LUT_PATH = os.path.join(os.path.dirname(__file__), 'ellipe_lut.npy')
ellipe_lut = np.load(_LUT_PATH)


def _generate(path=_LUT_PATH):
    vals = np.arange(0.0, 1.0, STEP, dtype=np.float64)
    with tqdm(total=1, desc="Computing ellipeinc") as pbar:
        values = ellipeinc(np.pi / 2, vals)
        pbar.update(1)
    np.save(path, values)


if __name__ == "__main__":
    _generate()
