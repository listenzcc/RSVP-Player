# %%
import singleInstance.debug_suspect_buffer
from singleInstance.logger import LOGGER
from singleInstance.loop_manager import LOOP_MANAGER

from singleInstance.constants import *

from singleInstance.main_loop import main_loop
from singleInstance.capture_loop import capture_loop
from singleInstance.rsvp_loop import rsvp_loop

from singleInstance.video_flow import VIDEO_FLOW

# %%
# Connect the VIDEO_FLOW and keep it FOREVER
VIDEO_FLOW.connect()

# %%
# Debug session

# %%
LOOP_MANAGER.set('MAIN')

# %%

# %%

while True:
    if LOOP_MANAGER.get() == 'MAIN':
        main_loop()

    if LOOP_MANAGER.get() == 'CAPTURE':
        capture_loop()

    if LOOP_MANAGER.get() == 'RSVP':
        rsvp_loop()

# %%
