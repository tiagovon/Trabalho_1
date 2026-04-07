import logging


def configurar_logger():
    logging.basicConfig(
        filename="monitor.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    return logging.getLogger("monitor")