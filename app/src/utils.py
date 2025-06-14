import logging
import os
from pathlib import Path
import filetype


def check_file_type(file_path: str) -> str:

    kind = filetype.guess(file_path)
    if kind is None:
        # Check if it's a PDF by reading first few bytes
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if header.startswith(b'%PDF-'):
                return "pdf"
        return "wrong format"

    if kind.mime.startswith('image/'):
        return "image"
    elif kind.mime == 'application/pdf':
        return "pdf"
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
