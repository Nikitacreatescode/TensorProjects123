import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
from pathlib import Path


class SbisContactsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)  # Оптимальный таймаут

    def wait_page_loaded(self, additional_timeout=5):
        """Ожидание полной загрузки страницы с комбинированными проверками"""
        try:
            # 1. Проверка JS readyState
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

            # 2. Проверка исчезновения прелоадера
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loader, .preloader")))

            # 3. Проверка специфичных элементов страницы
            self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1[contains(., 'Контакты')]")))

            self.logger.info("Страница контактов полностью загружена")
            return True
        except TimeoutException as e:
            self.logger.error(f"Timeout при загрузке страницы: {str(e)}")
            self.driver.save_screenshot("page_load_error.png")
            raise
    def get_current_region(self):
        """Получение текущего региона с локатором"""
        return self.wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".sbis_ru-Region-Chooser.ml-16 .sbis_ru-Region-Chooser__text")
            )
        ).text.strip()

    def change_region(self, region_name):
        """Смена региона с обработкой загрузки"""
        try:
            # 1. Ожидаем исчезновения прелоадера
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "div.preload-overlay")
                )
            )

            # 2. Клик через JavaScript (обход overlay)
            chooser = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.sbis_ru-Region-Chooser__text")
                )
            )
            self.driver.execute_script("arguments[0].click();", chooser)
            time.sleep(1)

            # 3. Поиск региона
            region_item = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f"//li[contains(@class, 'sbis_ru-Region-Panel__item')]//*[contains(text(), '{region_name}')]")
                )
            )
            self.driver.execute_script("arguments[0].click();", region_item)
            time.sleep(2)

            # 4. Проверка изменения
            WebDriverWait(self.driver, 20).until(
                lambda d: region_name in d.find_element(
                    By.CSS_SELECTOR, "span.sbis_ru-Region-Chooser__text"
                ).text
            )

        except Exception as e:
            print(f"Ошибка при смене региона: {str(e)}")
            self.driver.save_screenshot("region_error.png")
            raise

    def get_partners_list(self):
        """Получение списка партнеров с локатором"""
        try:
            return [el.text.strip() for el in self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".sbisru-Contacts-List__col--name .sbisru-Contacts-List__name")
                )
            ) if el.text.strip()]
        except:
            return []