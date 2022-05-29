'''
FileName: constants.py
Author: Chuncheng
Version: V0.0
Purpose: Constants for pygame
'''


# %%
import sys
import random
import pygame
from startup import CFG

# %%
MODE = tuple(int(e) for e in [CFG['screen']['width'],
                              CFG['screen']['height']])

CAPTION = CFG['UI']['caption']

TIMEOUT = int(CFG['UI']['timeout'])

WHITE = (255, 255, 255)
BLACK = (0, 30, 20)
GRAY = (100, 100, 100)

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


def set_layout():
    window_size = (1800, 900)
    patch_size = (int(CFG['picture']['width']),
                  int(CFG['picture']['height']))

    center_patch = dict(
        corner=(int(CFG['centerPatch']['cornerLeft']),
                int(CFG['centerPatch']['cornerTop'])),
        size=patch_size
    )

    left_patch = dict(
        corner=(int(CFG['leftPatch']['cornerLeft']),
                int(CFG['leftPatch']['cornerTop'])),
        size=patch_size
    )

    right_patch = dict(
        corner=(int(CFG['rightPatch']['cornerLeft']),
                int(CFG['rightPatch']['cornerTop'])),
        size=patch_size
    )

    return dict(
        window_size=window_size,
        center_patch=center_patch,
        left_patch=left_patch,
        right_patch=right_patch,
    )


LAYOUT = set_layout()
