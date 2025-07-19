from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import undetected_chromedriver as uc
import pandas as pd
import random
import os
import platform
import subprocess

# 2. Расширенные настройки Chrome
options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--guest')  # Критически важный параметр
options.add_argument('--no-first-run')
options.add_argument('--disable-web-security')
options.add_argument('--allow-running-insecure-content')
options.add_argument('--disable-extensions')
options.add_argument('--disable-popup-blocking')
options.add_argument('--disable-notifications')
options.add_argument('--disable-geolocation')

# 3. Ротация User-Agent
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Vivaldi/6.2.3105.58'
]
options.add_argument(f'user-agent={random.choice(user_agents)}')

# 4. Запуск браузера с улучшенной маскировкой
driver = uc.Chrome(
    options=options,
    headless=False,
    use_subprocess=True,
    version_main=138,
)

# 5. Кастомные заголовки
# Правильный формат для CDP команды
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
    'headers': {
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-CH-UA': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Referer': 'https://www.dns-shop.ru/',
        'DNT': '1'
    }
})

# Эмулируем человеческое поведение
def human_like_actions():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.2);")
    sleep(random.uniform(0.5, 1.5))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5);")
    sleep(random.uniform(0.7, 2))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(random.uniform(1, 3))

def open_file(file_path):
    """Открывает файл в программе по умолчанию для текущей ОС."""
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)  # Работает только в Windows
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path], check=True)
        else:  # Linux и другие UNIX-подобные
            subprocess.run(['xdg-open', file_path], check=True)
    except Exception as e:
        print(f"❌ Ошибка при открытии файла: {e}")

def save_to_excel(params_dict):
    # Создаем DataFrame
    df = pd.DataFrame(params_dict)

    # Сохраняем в Excel
    df.to_excel("processors.xlsx", index=False)
    print("Данные успешно сохранены в processors.xlsx")

import re

def cpu_data_dict_creator(cpu_string, price, href):
    # Универсальный шаблон для всех типов процессоров
    pattern = r"""
        ^(.*?)\s*                # Название процессора
        (?:\[.*?)?               # Опциональное начало характеристик
        (LGA\s\d+|AM\d|FM\d\+?|Socket\s*\d+),?\s*  # Сокет (LGA 1200, AM4, FM2+, Socket AM4)
        (?:.*?)?                 # Пропускаем возможные дополнительные символы
        (\d+)\s*(?:ядер[а]?|x|х)\s*  # Количество ядер
        (?:.*?)?                 # Пропускаем возможные дополнительные символы
        ([\d.]+)\s*ГГц,?\s*      # Частота
        (?:L2\s*[-—]?\s*([\d.]+)\s*МБ,?\s*)?  # Опциональный L2
        (?:L3\s*[-—]?\s*([\d.]+)\s*МБ,?\s*)?  # Опциональный L3
        (?:.*?)?                 # Пропускаем возможные дополнительные характеристики
        (\d+)\s*(?:x|х|канал[а]?|каналов)\s*(?:DDR\d[L]?)\s*,?\s*  # Память
        (?:.*?)?                 # Пропускаем возможные дополнительные символы
        (?:([^,]+?),?\s*)?       # Графика (опционально)
        (?:.*?)?                 # Пропускаем возможные дополнительные символы
        TDP\s*[-—]?\s*([\d.]+)\s*Вт  # TDP
        .*?$                    # Конец строки
    """

    match = re.search(pattern, cpu_string, re.VERBOSE | re.IGNORECASE)
    if not match:
        print(f"Не удалось распарсить строку: {cpu_string}")
        return None

    try:
        return {
            "Название": match.group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Сокет": match.group(2).strip(),
            "Количество ядер": int(match.group(3)),
            "Частота (ГГц)": float(match.group(4).replace(',', '.')),
            "Кэш L2 (МБ)": float(match.group(5).replace(',', '.')) if match.group(5) else "N/A",
            "Кэш L3 (МБ)": float(match.group(6).replace(',', '.')) if match.group(6) else "N/A",
            "Количество каналов памяти": int(match.group(7)),
            "Графика": match.group(8).strip() if match.group(8) else "Нет",
            "TDP (Вт)": int(float(match.group(9).replace(',', '.')))
        }
    except (ValueError, IndexError, AttributeError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {cpu_string}")
        return None

def gpu_data_dict_creator(gpu_string, price, href):
    # Дополнительные поиски для параметров, которые могут быть в разных местах
    memory_bus_match = re.search(r'([\d.]+)\s*бит', gpu_string)
    memory_type_match = re.search(r'(DDR\d|GDDR\d)', gpu_string, re.IGNORECASE)
    memory_size_match = re.search(r'([\d.]+)\s*Г?Б', gpu_string, re.IGNORECASE)
    gpu_clock_match = re.search(r'(?:GPU\s*:?\s*)?([\d.]+)\s*М?Гц', gpu_string, re.IGNORECASE)
    memory_clock_match = re.search(r'(?:память\s*:?\s*)?([\d.]+)\s*М?Гц', gpu_string, re.IGNORECASE)
    pcie_match = re.search(r'PCI[Ee]\s*([\d.]+)', gpu_string, re.IGNORECASE)

    try:
        result = {
            "Название": re.match(r'^(.*?)(?:\s*\[|$)', gpu_string).group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Объем памяти (ГБ)": float(memory_size_match.group(1).replace(',', '.')) if memory_size_match else "N/A",
            "Тип памяти": memory_type_match.group().upper() if memory_type_match else "N/A",
            "Шина памяти (бит)": int(memory_bus_match.group(1)) if memory_bus_match else "N/A",
            "Частота GPU (МГц)": int(float(gpu_clock_match.group(1).replace(',', '.'))) if gpu_clock_match else "N/A",
            "Частота памяти (МГц)": int(float(memory_clock_match.group(1).replace(',', '.'))) if memory_clock_match else "N/A",
            "Версия PCIe": pcie_match.group(1) if pcie_match else "N/A",
            "Разъемы": extract_connectors(gpu_string)
        }
        return result
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {gpu_string}")
        return None

def extract_connectors(gpu_string):
    connectors = []
    connector_patterns = {
        "DVI": r"DVI[- ]?[ID]?",
        "HDMI": r"HDMI",
        "VGA": r"VGA|D-Sub",
        "DisplayPort": r"DisplayPort|DP"
    }

    for name, pattern in connector_patterns.items():
        if re.search(pattern, gpu_string, re.IGNORECASE):
            connectors.append(name)

    return ", ".join(connectors) if connectors else "N/A"

def ram_data_dict_creator(ram_string, price, href):
    # Дополнительные поиски для параметров
    capacity_match = re.search(r'([\d.]+)\s*Г?Б', ram_string, re.IGNORECASE)
    type_match = re.search(r'(DDR\d+)', ram_string, re.IGNORECASE)
    speed_match = re.search(r'([\d.]+)\s*М?Гц', ram_string, re.IGNORECASE)
    timings_match = re.search(r'(\d+)\(CL\)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string) or \
                   re.search(r'CL(\d+)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string) or \
                   re.search(r'(\d+)[\s-]*(\d+)[\s-]*(\d+)[\s-]*(\d+)', ram_string)
    modules_match = re.search(r'([\d.]+)\s*Г?Б?x?\s*([\d.]+)\s*шт', ram_string, re.IGNORECASE)

    try:
        # Формируем строку таймингов
        if timings_match:
            if ram_string.count('(CL)') > 0:
                # Формат с (CL): 11(CL)-11-11-28
                timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                cl = timings_match.group(1)
            elif 'CL' in ram_string:
                # Формат с CL: CL11-11-11-28
                timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                cl = timings_match.group(1)
            else:
                # Простой формат: 11-11-11-28
                timings_str = f"{timings_match.group(1)}-{timings_match.group(2)}-{timings_match.group(3)}-{timings_match.group(4)}"
                cl = timings_match.group(1)
        else:
            timings_str = "N/A"
            cl = "N/A"

        result = {
            "Название": re.match(r'^(.*?)(?:\s*\[|$)', ram_string).group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Общий объем (ГБ)": float(capacity_match.group(1).replace(',', '.')) if capacity_match else "N/A",
            "Тип памяти": type_match.group(1).upper() if type_match else "N/A",
            "Размер модуля (ГБ)": float(modules_match.group(1).replace(',', '.')) if modules_match else "N/A",
            "Количество модулей": int(modules_match.group(2)) if modules_match else "N/A",
            "Частота (МГц)": int(float(speed_match.group(1).replace(',', '.'))) if speed_match else "N/A",
            "Тайминги": timings_str,
            "Латентность (CL)": cl
        }
        return result
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {ram_string}")
        return None


def motherboard_data_dict_creator(mb_string, price, href):
    # Основные параметры для поиска
    socket_match = re.search(r'(LGA\s\d+|BGA\d+|Socket\s*\d+|s?\d+)', mb_string, re.IGNORECASE)
    chipset_match = re.search(r'(Intel|AMD)\s*([A-Z0-9]+)', mb_string, re.IGNORECASE)
    ram_slots_match = re.search(r'(\d+)x(DDR\d[L]?)[-\s]*(\d+)?\s*МГц', mb_string, re.IGNORECASE)
    form_factor_match = re.search(r'(Micro-ATX|Mini-ITX|Mini-DTX|ATX|E-ATX|XL-ATX|Thin Mini-ITX)', mb_string,
                                  re.IGNORECASE)
    pcie_match = re.search(r'(\d+)xPCI-Ex(\d+)', mb_string, re.IGNORECASE)
    cpu_support_match = re.search(r'(Intel|AMD)\s*(.*?)\s*\(', mb_string)

    try:
        result = {
            "Название": re.match(r'^(.*?)(?:\s*\[|$)', mb_string).group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Сокет": socket_match.group() if socket_match else "N/A",
            "Чипсет": f"{chipset_match.group(1)} {chipset_match.group(2)}" if chipset_match else "N/A",
            "Количество слотов памяти": int(ram_slots_match.group(1)) if ram_slots_match else "N/A",
            "Тип слотов памяти": ram_slots_match.group(2).upper() if ram_slots_match else "N/A",
            "Частота слотов памяти": f"{ram_slots_match.group(3)} МГц" if ram_slots_match and ram_slots_match.group(3) else "N/A",
            "Форм-фактор": form_factor_match.group() if form_factor_match else "Нестандартный",
            "Количество слотов PCI-E": int(pcie_match.group(1)) if pcie_match else "N/A",
            "Версия слотов PCI-E": f"x{pcie_match.group(2)}" if pcie_match else "N/A",
            "Поддержка CPU": cpu_support_match.group().strip() if cpu_support_match else "N/A"
        }

        # Дополнительно проверяем поддержку CPU в другом формате
        if result["Поддержка CPU"] == "N/A":
            cpu_alt_match = re.search(r'\b(?:Intel|AMD)\b.*?(?:Celeron|Core|Ryzen|Athlon)\s*\w*', mb_string,
                                      re.IGNORECASE)
            if cpu_alt_match:
                result["Поддержка CPU"] = cpu_alt_match.group().strip()

        return result
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {mb_string}")
        return None


def cpu_cooler_data_dict_creator(cooler_string, price, href):
    # Основные параметры для поиска
    base_match = re.search(r'основание\s*-\s*([а-яА-Яa-zA-Z]+)', cooler_string, re.IGNORECASE)
    rpm_match = re.search(r'(\d+)\s*об/\s*мин', cooler_string)
    noise_match = re.search(r'(\d+\.?\d*)\s*дБ', cooler_string)
    pin_match = re.search(r'(\d+)\s*pin', cooler_string, re.IGNORECASE)
    tdp_match = re.search(r'(\d+)\s*Вт', cooler_string)
    fan_size_match = re.search(r'(\d+)\s*мм', cooler_string)

    try:
        result = {
            "Название": re.match(r'^(.*?)(?:\s*\[|$)', cooler_string).group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Материал основания": base_match.group(1).capitalize() if base_match else "N/A",
            "Скорость вращения": f"{rpm_match.group(1)} об/мин" if rpm_match else "N/A",
            "Уровень шума": f"{noise_match.group(1)} дБ" if noise_match else "N/A",
            "Разъем питания": f"{pin_match.group(1)} pin" if pin_match else "N/A",
            "Макс. TDP": f"{tdp_match.group(1)} Вт" if tdp_match else "N/A",
            "Размер вентилятора": f"{fan_size_match.group(1)} мм" if fan_size_match else "N/A"
        }

        # Дополнительно проверяем размер вентилятора по названию (например, R94 может означать 94мм)
        if result["Размер вентилятора"] == "N/A":
            size_from_name = re.search(r'(\d{2,3})(?:mm|мм|\s*мм)?', result["Название"])
            if size_from_name:
                result["Размер вентилятора"] = f"{size_from_name.group(1)} мм"

        return result
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {cooler_string}")
        return None

import re

def cooling_system_data_dict_creator(cooling_string, price, href):
    # Основные параметры для поиска
    fan_size_match = re.search(r'(\d+)\s*мм', cooling_string)
    sections_match = re.search(r'(\d+)\s*секци[ияей]', cooling_string)
    power_match = re.search(r'(SATA Power|3 pin|4 pin|15 pin)', cooling_string, re.IGNORECASE)
    radiator_match = re.search(r'радиатор\s*-\s*([а-яА-Яa-zA-Z]+)', cooling_string, re.IGNORECASE)
    tdp_match = re.search(r'TDP\s*(\d+)\s*Вт', cooling_string, re.IGNORECASE)
    fan_count_match = re.search(r'(\d+)\s*вентилятор', cooling_string)
    type_match = re.search(r'(воздушное|жидкостное)\s*охлаждение', cooling_string, re.IGNORECASE)

    try:
        result = {
            "Название": re.match(r'^(.*?)(?:\s*\[|$)', cooling_string).group(1).strip(),
            "Цена": price,
            "Ссылка": href,
            "Тип охлаждения": type_match.group(1).capitalize() if type_match else "N/A",
            "Размер вентилятора(ов)": f"{fan_size_match.group(1)} мм" if fan_size_match else "N/A",
            "Количество секций": sections_match.group(1) if sections_match else "1",  # По умолчанию 1 секция
            "Количество вентиляторов": fan_count_match.group(1) if fan_count_match else
                                     sections_match.group(1) if sections_match else "1",  # Обычно равно количеству секций
            "Питание": power_match.group(1) if power_match else "N/A",
            "Материал радиатора": radiator_match.group(1).capitalize() if radiator_match else "N/A",
            "TDP": f"{tdp_match.group(1)} Вт" if tdp_match else "N/A"
        }

        # Автоматическое определение типа охлаждения по названию
        if result["Тип охлаждения"] == "N/A":
            if any(word in cooling_string.lower() for word in ['liquid', 'water', 'сжо', 'жидкост']):
                result["Тип охлаждения"] = "Жидкостное"
            else:
                result["Тип охлаждения"] = "Воздушное"

        # Уточнение количества вентиляторов для СЖО
        if result["Тип охлаждения"] == "Жидкостное":
            if "360" in result["Название"]:
                result["Количество вентиляторов"] = "3"
            elif "240" in result["Название"]:
                result["Количество вентиляторов"] = "2"
            elif "120" in result["Название"]:
                result["Количество вентиляторов"] = "1"

        return result
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Ошибка обработки данных: {e} в строке: {cooling_string}")
        return None

# Обновленные XPath
xpathes = {
    "name": "//div[@class='catalog-product__name-wrapper']//span",  # Название товара
    "price": "//div[@class='product-buy__price']",  # Цена
    "href": "//a[@class='catalog-product__name ui-link ui-link_black']",  # Ссылка на товар
    "next-page": "//button[contains(text(), 'Показать ещё')]"
    # следующая страница
}

try:
    driver.get("https://www.dns-shop.ru/catalog/17a9cc2d16404e77/kulery-dlya-processorov/")
    sleep(random.uniform(5, 10))  # Случайная задержка

    while driver.find_element(By.XPATH, xpathes["next-page"]):  
        human_like_actions()  # Имитируем поведение человека
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, xpathes["next-page"]))
        )
        button.click()
        sleep(random.uniform(0.5, 1.5))

    # Ожидаем загрузки элементов
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, xpathes['name'])))

    # Получаем элементы с обработкой ошибок
    names = []
    prices = []
    hrefs = []

    # Поиск элементов
    for name in driver.find_elements(By.XPATH, xpathes['name']):
        # Извлекаем имя
        names.append(name.text)

    for price in driver.find_elements(By.XPATH, xpathes['price']):
        # Извлекаем цену
        prices.append(price.text.replace('\u202f', '').replace('P', '₽').replace('\u2009', ''))

    for href in driver.find_elements(By.XPATH, xpathes['href']):
        # Извлекаем ссылку
        hrefs.append(href.get_attribute('href'))

    # Сохранение данных в словарь
    data = []
    for name, price, href in zip(names, prices, hrefs):
        data.append(cpu_cooler_data_dict_creator(name, price, href))

    # Создание excel таблицы
    save_to_excel(data)

except Exception as e:
    print(f"Произошла ошибка: {str(e)}")

finally:
    driver.quit()

    # Запуск Excel
    file_path = 'processors.xlsx'  # путь к вашему файлу
    if os.path.exists(file_path):
        open_file(file_path)
    else:
        print("Файл не найден!")




