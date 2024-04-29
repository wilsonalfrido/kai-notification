import logging


def create_logger(logger_name: str):

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
        datefmt='%d %B %Y %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                filename='./logs/history_access.log',
                mode='a'
            )
        ],
    )

    logger = logging.getLogger(logger_name)
    return logger