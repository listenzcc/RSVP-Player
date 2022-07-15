# %%
import sys
import pygame
import configparser

from pathlib import Path

from .parallel.parallel import Parallel

# %%
CFG = configparser.ConfigParser()
CFG.read(Path(__file__).parent.parent.joinpath('asset/config.ini'))

# %%
PARALLEL = Parallel()
PARALLEL.reset(CFG['Parallel']['address'])

# %%
RATE = int(CFG['RSVP']['rate'])

# %%
MODE = tuple(int(e) for e in [CFG['screen']['width'],
                              CFG['screen']['height']])

CAPTION = CFG['UI']['caption']

TIMEOUT = int(CFG['UI']['timeout'])

YELLOW = (200, 200, 0)
GREEN = (0, 200, 100)
CYAN = (0, 200, 255)
RED = (200, 0, 0)
WHITE = (200, 200, 200)
BLACK = (0, 50, 10)
REAL_BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# %%
pygame.init()

# pygame.font.get_fonts()
# pygame.font.Font('simhei.ttf', 50)
# pygame.font.Font('C:/Windows/Fonts/simhei.ttf', 50)

FONT_SIZE = int(CFG['UI']['fontSize'])

FONT = pygame.font.Font(
    CFG['UI']['fontName'],
    FONT_SIZE
)


# %%
def QUIT_PYGAME(msg='Quit'):
    pygame.quit()
    sys.exit(msg)


# %%
SCREEN = pygame.display.set_mode(MODE)
pygame.display.set_caption(CAPTION)

# %%