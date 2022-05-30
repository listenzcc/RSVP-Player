# %%
from singleInstance.logger import LOGGER
from singleInstance.loop_manager import LOOP_MANAGER

from singleInstance.constants import *

from singleInstance.main_loop import main_loop
from singleInstance.capture_loop import capture_loop

# %%
import singleInstance.debug_suspect_buffer

# %%
LOOP_MANAGER.set('MAIN')

# %%

# %%

while True:
    if LOOP_MANAGER.get() == 'MAIN':
        main_loop()
    if LOOP_MANAGER.get() == 'CAPTURE':
        capture_loop()

# %%
