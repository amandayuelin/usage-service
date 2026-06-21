import logging
import sys


def configure_logging(level: str = "INFO"):
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)
