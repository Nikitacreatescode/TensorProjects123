from pages.SbisPage import SbisPage
from pages.TensorPage import TensorPage
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os


# Константы
SBIS_URL = "https://sbis.ru/"
DOWNLOAD_LINK_TEXT = "Скачать локальные версии"
PLUGIN_NAME = "СБИС Плагин"
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
EXPECTED_FILE_PATTERN = "sbisplugin-setup-web.exe"


def test_tensor_workflow(browser):
    logger = logging.getLogger(__name__)
    logger.info("=== Начало теста 1 ===")

    try:
        # Шаг 1-2: Переход на SBIS -> Контакты -> Тензор
        sbis_page = SbisPage(browser)
        time.sleep(5)  # Пауза для стабилизации
        sbis_page.go_to_contacts()
        time.sleep(5)  # Пауза для стабилизации
        original_window = sbis_page.click_tensor_banner()
        logger.info("Шаг 1-2 выполнен успешно")

        # Шаг 3-5: Проверки на Tensor.ru
        tensor_page = TensorPage(browser, original_window)
        assert tensor_page.check_people_block(), "Блок 'Сила в людях' не найден"
        tensor_page.go_to_about_page()
        assert "tensor.ru/about" in browser.current_url
        logger.info("Шаг 3-5 выполнен успешно")

        # Шаг 6: Проверка изображений
        tensor_page.check_work_section_images()
        logger.info("Шаг 6 выполнен успешно")

        # Возврат на SBIS
        tensor_page.driver.close()
        browser.switch_to.window(original_window)
        logger.info("=== Тест 1 успешно завершен ===")
    except Exception as e:
        logger.error(f"Тест 1 упал с ошибкой: {str(e)}")
        raise