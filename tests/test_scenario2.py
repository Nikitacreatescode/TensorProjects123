from pages.SbisContactsPage import SbisContactsPage
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from selenium.common.exceptions import NoSuchElementException
import os


# Константы
SBIS_URL = "https://sbis.ru/"
DOWNLOAD_LINK_TEXT = "Скачать локальные версии"
PLUGIN_NAME = "СБИС Плагин"
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
EXPECTED_FILE_PATTERN = "sbisplugin-setup-web.exe"


def get_partners_list(self):
    """Получение списка партнеров"""
    self.wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".sbis_ru-Contacts-List__name")
        )
    )
    return [el.text for el in self.driver.find_elements(
        By.CSS_SELECTOR, ".sbis_ru-Contacts-List__name"
    )]

def get_current_region(self):
    """Получение региона для saby.ru"""
    return self.wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "span.sbis_ru-Region-Chooser__text")
        )
    ).text

def wait_page_loaded(self):
    """Ожидание загрузки"""
    try:
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.wait.until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".preload-overlay, .loader-common")
            )
        )
        time.sleep(0.5)
    except:
        self.driver.save_screenshot("load_error.png")
        raise


def test_region_change_to_kamchatka(browser):
    logger = logging.getLogger(__name__)
    logger.info("=== Начало теста 2 ===")
    """Тест изменения региона"""
    contacts_page = SbisContactsPage(browser)

    try:
        # 1. Переход на страницу
        browser.get("https://sbis.ru/contacts")
        logger.info("Успешный переход по прямому URL")
        # 2. Ожидание полной загрузки
        WebDriverWait(browser, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        WebDriverWait(browser, 30).until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.preload-overlay")
            )
        )
        logger.info("Загрузка прошла успешно")
        # 3. Получение региона
        current_region = contacts_page.get_current_region()
        print(f"Текущий регион: {current_region}")
        logger.info("Текущий регион определен")
        # 4. Смена региона
        target_region = "Камчатский край"
        contacts_page.change_region(target_region)
        logger.info("Смена региона на Камчатский край")
        # 5. Проверка результата
        new_region = contacts_page.get_current_region()
        print(f"Новый регион: {new_region}")
        if target_region not in new_region:
            logger.error("Ошибка: регион не был поменян")
            assert False, "Регион не изменился"
        else:
            logger.info("Регион успешно изменён")
            logger.info("=== Тест 2 успешно завершен ===")
    except Exception as e:
        print(f"Ошибка в тесте: {str(e)}")
        browser.save_screenshot("test_error.png")
        logger.info("Ошибка в тесте 2: {str(e)}")
        raise