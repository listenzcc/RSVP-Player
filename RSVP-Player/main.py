# %%
from singleInstance.logger import LOGGER
from singleInstance.loop_manager import LOOP_MANAGER

from singleInstance.constants import *

from singleInstance.main_loop import main_loop

# %%
LOOP_MANAGER.set('MAIN')

# %%

# %%

main_loop()
