import logging
"""
YAVOS default logger

Usage:
    from Config.ylog import yLogger

    yl = yLogger()  # default is a debug level so everything will show
    yl = yLogger(level='info')  # only info and higher will show

    yl.log.debug("wow")
    yl.log.info("wow")
    yl.log.warning("wow")
    yl.log.error("wow")
"""
class yLogger:
    def __init__(self, level='debug'):
        log_level = logging.DEBUG
        if level == 'info':
            log_level = logging.INFO
        elif level == 'warn' or level == 'warning':
            log_level = logging.WARNING
        elif level == 'error':
            log_level = logging.ERROR
        elif level == 'critical':
            log_level = logging.CRITICAL

        logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s] - %(message)s', filename='Config/yavos.log')
        self.log = logging.getLogger(__name__)

