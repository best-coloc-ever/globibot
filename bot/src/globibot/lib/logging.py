import logging
import sys

formatter = logging.Formatter('[%(asctime)s -- %(levelname)s -- %(plugin_name)s]\t%(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

__all__ = ['logger']
