from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
from selenium.common.exceptions import NoSuchElementException


class TensorPage:
    def __init__(self, driver, original_window, logger=None):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.original_window = original_window
        self._switch_to_tensor_tab()
        self.logger = logger or logging.getLogger(__name__)

    def _switch_to_tensor_tab(self):
        """Переключение на вкладку Тензора с проверкой загрузки"""
        new_window = [w for w in self.driver.window_handles if w != self.original_window][0]
        self.driver.switch_to.window(new_window)

        # Комбинированное ожидание загрузки
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.wait.until(EC.url_contains("tensor.ru"))
        time.sleep(2)  # Доп. пауза для стабилизации

    def check_people_block(self):
        """Поиск блока 'Сила в людях' с 3-мя стратегиями"""
        locators = [
            (By.XPATH, "//h2[contains(., 'Сила в людях')]"),
            (By.CSS_SELECTOR, ".tensor_ru-Index__block-title"),
            (By.XPATH, "//*[contains(text(), 'Сила в людях')]")
        ]

        for locator in locators:
            try:
                element = self.wait.until(EC.visibility_of_element_located(locator))
                self.logger.info(f"Блок найден по локатору: {locator}")
                return element.is_displayed()
            except TimeoutException:
                continue
        return False

    def go_to_about_page(self):
        """Переход на страницу 'О Тензоре' с автоматическим скроллом"""
        # Сначала находим блок "Сила в людях"
        people_block = self.wait.until(
            EC.presence_of_element_located((By.XPATH,
                                            "//*[contains(text(), 'Сила в людях')]/ancestor::div[contains(@class, 'tensor_ru-Index__block')]"))
        )

        # Скроллим к блоку
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", people_block)
        time.sleep(1)  # Пауза после скролла

        # Ищем кнопку "Подробнее" внутри блока
        about_link = people_block.find_element(By.XPATH, ".//a[contains(@href, '/about')]")
        about_link.click()

        # Ждём загрузки
        self.wait.until(EC.url_contains("tensor.ru/about"))
        self.logger.info("Успешный переход на страницу 'О Тензоре'")

    def check_work_section_images(self):
        """Проверка фотографий команды"""
        try:
            # 1. Ждем загрузки страницы
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

            # 2. Находим раздел "Работаем" через заголовок
            section_title = self.wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//h2[contains(text(), 'Работаем')]")
                )
            )

            # 3. Скроллим к заголовку
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", section_title)
            time.sleep(2)

            # 4. Ищем фотографии команды по уникальному признаку
            team_photos = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH,
                     "//div[contains(@class, 'tensor_ru-About__block3')]//img[contains(@class, 'tensor_ru-About__block3-image')]")
                )
            )

            if not team_photos:
                raise NoSuchElementException("Не найдены фотографии команды")

            # 5. Проверяем размеры только видимых фото
            visible_photos = [img for img in team_photos if img.is_displayed()]
            first_size = (visible_photos[0].size['width'], visible_photos[0].size['height'])

            for photo in visible_photos[1:]:
                current_size = (photo.size['width'], photo.size['height'])
                assert current_size == first_size, f"Размер {current_size} не совпадает с {first_size}"

            self.logger.info(f"Все {len(visible_photos)} фотографий имеют размер {first_size}")

        except Exception as e:
            self.logger.error(f"Критическая ошибка: {str(e)}")
            self.driver.save_screenshot("final_debug.png")
            raise