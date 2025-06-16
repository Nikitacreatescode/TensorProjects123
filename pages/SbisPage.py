# Главная страница SBIS

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging


class SbisPage:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.driver.maximize_window()
        self.logger = logger or logging.getLogger(__name__)

    def go_to_contacts(self):
        """Переход в контакты с 3-мя сценариями"""
        try:
            # Попытка 1: Прямой переход по URL
            self.driver.get("https://sbis.ru/contacts")
            self.wait.until(EC.url_contains("/contacts"))
            self.logger.info("Успешный переход по прямому URL")
            return
        except TimeoutException:
            self.logger.warning("Прямой переход не сработал, пробуем через меню")

        try:
            # Попытка 2: Через кнопку меню
            self.driver.get("https://sbis.ru/")
            menu_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".sbisru-Header__menu-button"))
            )
            menu_button.click()

            contacts_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(@href, '/contacts') and .//text()[contains(., 'Контакты')]]"))
            )
            contacts_link.click()
            self.wait.until(EC.url_contains("/contacts"))
            self.logger.info("Успешный переход через меню")
        except TimeoutException:
            self.logger.error("Оба метода перехода не сработали")
            raise

    def click_tensor_banner(self):
        """Клик по баннеру Тензор с 4-мя вариантами локаторов"""
        locators = [
            (By.CSS_SELECTOR, '[title="tensor.ru"]'),  # Основной
            (By.XPATH, "//a[contains(@href, 'tensor.ru')]"),  # Альтернативный 1
            (By.CSS_SELECTOR, 'img[alt*="Тензор"]'),  # Альтернативный 2
            (By.XPATH, "//div[contains(@class, 'sbisru-Contacts__logo')]//a")  # Альтернативный 3
        ]

        for locator in locators:
            try:
                banner = self.wait.until(EC.element_to_be_clickable(locator))
                original_window = self.driver.current_window_handle
                banner.click()
                self.wait.until(lambda d: len(d.window_handles) > 1)
                self.logger.info(f"Баннер найден по локатору: {locator}")
                return original_window
            except TimeoutException:
                continue

        raise TimeoutException("Не удалось найти кликабельный баннер Тензор")