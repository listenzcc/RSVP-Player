# %%
import sys
import pygame
import configparser
from pathlib import Path

# %%
CFG = configparser.ConfigParser()
CFG.read(Path(__file__).parent.parent.joinpath('asset/config.ini'))

# %%
RATE = int(CFG['RSVP']['rate'])

# %%
MODE = tuple(int(e) for e in [CFG['screen']['width'],
                              CFG['screen']['height']])

CAPTION = CFG['UI']['caption']

TIMEOUT = int(CFG['UI']['timeout'])

RED = (200, 0, 0)
WHITE = (200, 200, 200)
BLACK = (0, 50, 10)
GRAY = (100, 100, 100)

# %%
pygame.init()

# pygame.font.get_fonts()
# pygame.font.Font('simhei.ttf', 50)
# pygame.font.Font('C:/Windows/Fonts/simhei.ttf', 50)

FONT = pygame.font.Font(
    CFG['UI']['fontName'],
    int(CFG['UI']['fontSize'])
)


# %%
def QUIT_PYGAME(msg='Quit'):
    pygame.quit()
    sys.exit(msg)


# %%
SCREEN = pygame.display.set_mode(MODE)
pygame.display.set_caption(CAPTION)

# %%
