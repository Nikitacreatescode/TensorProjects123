from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pytest
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Константы
SBIS_URL = "https://sbis.ru/"
DOWNLOAD_LINK_TEXT = "Скачать локальные версии"
PLUGIN_NAME = "СБИС Плагин"
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
EXPECTED_FILE_PATTERN = "sbisplugin-setup-web.exe"


@pytest.fixture(autouse=True)
def browser():
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    options.add_argument("--disable-extensions")
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", DOWNLOAD_DIR)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
    # Инициализируем драйвер
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    """Надежная настройка логирования для всех тестов"""
    log_file = Path("tensor_test.log")
    log_file.parent.mkdir(exist_ok=True)

    # Полностью очищаем конфигурацию логгера
    logging.root.handlers = []

    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Настраиваем файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        log_file,
        mode='a',
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Настраиваем консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Дополнительно настраиваем логгер для Selenium
    selenium_logger = logging.getLogger('selenium')
    selenium_logger.setLevel(logging.WARNING)