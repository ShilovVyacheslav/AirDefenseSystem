import numpy as np
from scipy.special import ellipeinc
from tqdm import tqdm

from src.core.constants import STEP

vals = np.arange(0.0, 1.0, STEP, dtype=np.float64)

with tqdm(total=1, desc="Computing ellipeinc") as pbar:
    ellipe_values = ellipeinc(np.pi / 2, vals)
    pbar.update(1)

np.save('ellipe_lut.npy', ellipe_values)
