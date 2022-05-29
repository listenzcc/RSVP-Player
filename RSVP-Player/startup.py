'''
FileName: startup.py
Author: Chuncheng
Version: V0.0
Purpose: The startup stuffs of the project.
'''


# %%
import logging
import configparser
from pathlib import Path

# %%
CONFIG = dict(
    short_name='RP',
    app_name='RSVP Player',
    log_folder=Path(__file__).parent.joinpath('log'),
    asset_folder=Path(__file__).parent.joinpath('asset'),
)

# %%
CFG = configparser.ConfigParser()
CFG.read(CONFIG['asset_folder'].joinpath('config.ini'))


# %%
logger_kwargs = dict(
    level_file=logging.DEBUG,
    level_console=logging.DEBUG,
    format_file='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s:%(module)s:%(funcName)s}}',
    format_console='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s}}'
)


def generate_logger(name, filepath, level_file, level_console, format_file, format_console):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(filepath)
    file_handler.setFormatter(logging.Formatter(format_file))
    file_handler.setLevel(level_file)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_console))
    console_handler.setLevel(level_console)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


LOGGER = generate_logger('RapidDisplayer', CONFIG['log_folder'].joinpath(
    'RapidDisplayer.log'), **logger_kwargs)
LOGGER.info(
    '--------------------------------------------------------------------------------')
LOGGER.info(
    '---- New Session is started ----------------------------------------------------')
LOGGER.debug('Read CFG of {}'.format([e for e in CFG]))

# %%
