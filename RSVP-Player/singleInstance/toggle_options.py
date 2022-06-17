# %%
from .logger import LOGGER
from .constants import *

# %%

options = dict(
    OSD=['OSD', -1, True],  # Draw on screen display
    UNT=['UNT', -1, True],  # Use non target pictures
    SUM=['SUM', -1, True],  # Draw summary
    INT=['INT', -1, True],  # Allow interrupt
    OPT1=['OPT1', -1, False],
    OPT2=['OPT2', -1, False],
)


class ToggleOption(object):
    def __init__(self, options=options):
        self.options = options
        self.mouse_over = ''
        pass

    def check(self, event):
        '''
        Check the clicked controller
        '''
        # Deal with mouse_over events
        if event.type == pygame.MOUSEMOTION:
            self.mouse_over = ''
            options = self.options
            for opt in options:
                if options[opt][1].contains(event.pos, (1, 1)):
                    self.mouse_over = opt
                    break

        # Only accept MOUSEBUTTONUP
        if not event.type == pygame.MOUSEBUTTONUP:
            return

        options = self.options
        for opt in options:
            if options[opt][1].contains(event.pos, (1, 1)):
                LOGGER.debug('Detect click event on option: {}'.format(opt))
                options[opt][2] = not options[opt][2]
                LOGGER.debug('Toggle option: {}: {}'.format(
                    opt, options[opt][2]))
                return opt

        return

    def draw(self):
        '''
        Draw options into the pygame window

        The example is options

        options = dict(
            OSD=['OSD', -1, True],
            UNT=['UNT', -1, True],
            OPT1=['OPT1', -1, False],
            OPT2=['OPT2', -1, False],
        )

        They are drawn in the top of the window from left to right.

        -------------------------
        |                       |
        |                   opt |
        |                   opt |
        |                   opt |
        |                       |
        -------------------------

        '''
        options = self.options

        # Draw controllers
        width = 1
        background = None
        antialias = True

        left = int(CFG['toggleRect']['left'])
        top = int(CFG['toggleRect']['top'])
        _top = 10

        for j, option in enumerate(options):
            if option == self.mouse_over:
                color = YELLOW
            else:
                color = WHITE

            string = options[option][0]
            v1 = options[option][0]
            if options[option][2]:
                v2 = '| ON  --- |'
            else:
                v2 = '| --- OFF |'
            string = '| {:6s} {}'.format(v1, v2)

            text = FONT.render(string, antialias, color, background)
            rect = text.get_rect()
            rect.height *= 1.1
            top += _top + rect.height
            rect.center = (left + rect.width / 2, top - rect.height / 2)

            SCREEN.fill(BLACK, rect)
            SCREEN.blit(text, rect)

            pygame.draw.rect(SCREEN, color, rect, width=width)

            options[option][1] = rect

        return options


TOGGLE_OPTION = ToggleOption()


# %%

# def draw_summary():
#     width = 1
#     color = WHITE
#     background = None
#     antialias = True

#     summary = summary_buffers()

#     top = int(CFG['screen']['height']) / 2
#     _top = 10
#     w = int(CFG['screen']['width'])

#     for string in summary:
#         text = FONT.render(string, antialias, color, background)
#         rect = text.get_rect()
#         rect.height *= 1.1
#         rect.center = (w - rect.width/2, top)
#         top += _top + rect.height

#         # SCREEN.fill(BLACK, rect)
#         SCREEN.blit(text, rect)
#         pygame.draw.rect(SCREEN, color, rect, width=width)

#         pass

#     return

# %%
