from .logger import LOGGER

LOGGER.debug('Starting loop manager')


states = dict(
    MAIN='Main loop',
    CAPTURE='Capture loop',
    RSVP='RSVP loop',
    INTER='Interrupt loop',
)

queue_limit = 100


class LoopManager(object):
    def __init__(self):
        self.states = states
        self.current = 'MAIN'
        self.queue = ['MAIN'] * queue_limit
        LOGGER.info('LoopManager initialized')

    def set(self, state):
        if not state in self.states:
            LOGGER.error('Invalid state: {}. Something is going very wrong'.format(state))
            return

        self.queue.insert(0, state)
        self.queue.pop()

        LOGGER.info('LoopManager set state: {} from {}'.format(state, self.queue[1]))

    def get(self):
        return self.queue[0]


LOOP_MANAGER = LoopManager()
