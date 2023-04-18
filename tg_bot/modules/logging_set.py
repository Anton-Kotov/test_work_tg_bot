import logging


# Создание кастомного фильтра
class InfoDebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)


# Создание логгера
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)

# Создание обработчиков файлов

info_debug_handler = logging.FileHandler("info_debug.log")
info_debug_handler.setLevel(logging.DEBUG)
info_debug_handler.addFilter(InfoDebugFilter())

other_handler = logging.FileHandler("warning.log")
other_handler.setLevel(logging.WARNING)

# Создание обработчика потока
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создание и добавление форматтера для обработчиков
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
info_debug_handler.setFormatter(formatter)
other_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавление обработчиков к логгеру
logger.addHandler(info_debug_handler)
logger.addHandler(other_handler)
logger.addHandler(console_handler)


