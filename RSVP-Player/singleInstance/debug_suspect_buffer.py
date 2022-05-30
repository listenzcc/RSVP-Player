# %%
import cv2
from pathlib import Path
from tqdm.auto import tqdm

from .toolbox import Pair
from .buffer import SUSPECT_BUFFER
from .constants import *

# %%
folder = Path(__file__).parent.parent.joinpath('asset/debugPictures')

print([e for e in folder.iterdir()])

# %%
for j, e in tqdm(enumerate(folder.iterdir())):
    frame = cv2.imread(e.as_posix())
    cv2.flip(frame, 1, frame)
    frame = frame.transpose([1, 0, 2])

    pair = Pair(frame, idx=100+j)
    pair.compute()
    SUSPECT_BUFFER.append(pair)


# %%
