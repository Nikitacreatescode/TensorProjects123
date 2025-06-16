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


def test_sbis_plugin_download(browser):
    logger = logging.getLogger(__name__)
    logger.info("=== Начало теста 3 ===")
    try:
        # 1. Настройка папки для загрузок
        downloads_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        logger.info("Папка для сохранения скаченного файла создана")
        # 2. Переход на сайт sbis.ru
        browser.get("https://sbis.ru/")
        browser.maximize_window()

        # 3. Ожидание загрузки страницы
        WebDriverWait(browser, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("Браузер открыт и загружен")
        # 4. Поиск футера и прокрутка к нему
        try:
            footer = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sbisru-Footer"))
            )
            browser.execute_script("arguments[0].scrollIntoView();", footer)
            logger.info("Футер обнаружен и прокручен")
        except:
            # Альтернативный способ прокрутки
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            logger.info("Искользован альтернативный метод прокрутки футера")

        time.sleep(5)  # Пауза для стабилизации

        # 5. Поиск ссылки "Скачать локальные версии"
        download_link = WebDriverWait(browser, 20).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Скачать локальные версии"))
            )
        logger.info("Обнаружена ссылка: Скачать локальные версии")
        # 6. Клик по ссылке с обработкой возможных перекрытий
        try:
            download_link.click()
        except:
            browser.execute_script("arguments[0].click();", download_link)
        logger.info("Успешный клик по ссылке")
        # 7. Ожидание загрузки страницы скачивания
        WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Скачать (Exe 10.40 МБ)')]")))
        logger.info("Загрузка страницы завершена")
        # 8. Извлечем вес файл .exe из текста ссылки
        size_element = WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Скачать (Exe 10.40 МБ)')]"))
        )
        site_size_text = size_element.text  # "Скачать (Exe 10.40 МБ)"

        # 9. Извлекаем числовое значение размера
        parts = site_size_text.split()  # ["Скачать", "(Exe", "10.40", "МБ)"]
        site_size_mb = round(float(parts[2].replace(',', '.')), 2)  # Получаем 10.40 как число
        logger.info("Шаги 8 и 9 выполнены успешно")
        # 10. Клик по ссылке "скачать"
        plugin_tab = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Скачать (Exe 10.40 МБ)')]"))
        )
        plugin_tab.click()
        logger.info("Успешный клик по ссылке")
        # 11. Заморозим программу на время скачивания файла. Предположим, что 40 секунд хватит для полной загрузки
        time.sleep(40)

        # 12. Проверяем что файл скачался
        downloaded_files = [f for f in os.listdir(downloads_dir) if f.startswith('saby-setup-web.exe')]
        assert downloaded_files, "Файл плагина не найден в папке downloads"
        check_file_here = f"Файл {downloaded_files[0]} успешно скачан"
        logger.info("Проверка скачивания прошла успешно")

        # 13. Получаем размер скачанного файла
        file_path = os.path.join(downloads_dir, downloaded_files[0])
        downloaded_size_bytes = os.path.getsize(file_path)
        downloaded_size_mb = round(downloaded_size_bytes / (1024 * 1024), 2)  # Конвертируем в МБ
        logger.info("Размер скачанного файла получен")

        # 14. Сравниваем размеры с допуском 0.1 МБ
        size_diff = abs(downloaded_size_mb - site_size_mb)
        if size_diff > 0.1:
            print(f"Размер не совпадает! Ожидалось: {site_size_mb:.2f} МБ, "
                  f"фактический размер: {downloaded_size_mb:.2f} МБ")
        else:
            print(check_file_here, f"Размер совпадает: сайт {site_size_mb:.2f} МБ, файл {downloaded_size_mb:.2f} МБ")
        logger.info("Размеры файла на сайте и в папке downloads были сравнены между собой")
        logger.info("=== Тест 3 успешно завершен ===")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        logger.info("Тест 3 упал с ошибкой {str(e)}")
        raise