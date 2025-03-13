import logging

def logger_setup():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logging.getLogger('pika').setLevel(logging.ERROR)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

log = logger_setup()