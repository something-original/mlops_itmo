import magic
import logging
import os
from pathlib import Path


def check_file_type(file_path) -> str:

    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    if file_type == "application/pdf":
        return "pdf"
    elif file_type.startswith("image/"):
        return "image"
    else:
        return "wrong format"


def setup_logging(mode: str, file_name: str):
    """Функция для настройки логгирования

    Args:
        mode (str): w - перезаписывать файл, a - записывать в тот же файл
        file_name (str): имя файла с логами
    """

    logger = logging.getLogger('main_logger')
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        root_dir = Path(__file__).resolve().parent.parent

        logpath = os.path.join(root_dir, 'logs')
        if 'logs' not in os.listdir(root_dir):
            os.mkdir(logpath)

        fh = logging.FileHandler(f'{logpath}/{file_name}', mode=mode, encoding='utf-8-sig')
        file_formatter = logging.Formatter('%(asctime)s  %(levelname)s  %(message)s', "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s  %(levelname)s  %(message)s', "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)
