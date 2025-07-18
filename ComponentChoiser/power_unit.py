def select_best_psu(psu_list, components_power, weights=None):
    """
    Выбирает лучший блок питания с учетом энергопотребления комплектующих.

    :param psu_list: Список БП в виде словарей с характеристиками
    :param components_power: Словарь с энергопотреблением комплектующих (в ваттах)
    :param weights: Веса характеристик (можно настроить)
    :return: Лучший БП и его оценка
    """
    if not psu_list:
        return None, 0

    # Рассчитываем общее энергопотребление системы
    total_power = sum(components_power.values())

    # Добавляем запас 20% и округляем до 50 Вт вверх
    recommended_power = ((total_power * 1.2) // 50 + 1) * 50

    # Веса характеристик по умолчанию
    default_weights = {
        'power': 1.5,  # Соответствие рекомендованной мощности
        'efficiency': 2.0,  # Сертификат 80 PLUS
        'modular': 1.2,  # Модульность
        'connectors': 1.0,  # Количество и тип коннекторов
        'fan_size': 0.5,  # Размер вентилятора
        'noise_level': -1.0,  # Уровень шума
        'warranty': 0.8,  # Срок гарантии
        'price': -1.5  # Цена
    }

    weights = weights or default_weights

    best_psu = None
    best_score = -float('inf')

    for psu in psu_list:
        score = 0

        # Проверка на достаточную мощность
        if psu['wattage'] < total_power:
            continue  # Пропускаем БП с недостаточной мощностью

        # Оценка соответствия мощности (чем ближе к рекомендованной, тем лучше)
        power_diff = abs(psu['wattage'] - recommended_power)
        power_score = max(0, 100 - power_diff)  # 100 баллов за идеальное соответствие
        score += power_score * weights['power']

        # Оценка эффективности (80 PLUS)
        efficiency_map = {
            '80+ Platinum': 10,
            '80+ Gold': 8,
            '80+ Silver': 6,
            '80+ Bronze': 4,
            '80+': 2,
            None: 0
        }
        efficiency = psu.get('efficiency')
        score += efficiency_map.get(efficiency, 0) * weights['efficiency']

        # Модульность кабелей
        modular_map = {
            'Full': 3,
            'Semi': 2,
            'No': 0
        }
        modular = psu.get('modular', 'No')
        score += modular_map.get(modular, 0) * weights['modular']

        # Проверка коннекторов (должны подходить к комплектующим)
        connectors_ok = True
        if 'connectors' in psu:
            # Проверяем наличие необходимых коннекторов
            if components_power.get('gpu', 0) > 0 and psu['connectors'].get('pcie_8pin', 0) < 1:
                connectors_ok = False
            if components_power.get('cpu', 0) > 0 and psu['connectors'].get('cpu_8pin', 0) < 1:
                connectors_ok = False

        if not connectors_ok:
            continue

        # Дополнительные характеристики
        if 'fan_size' in psu:
            fan_size = int(psu['fan_size'].replace('mm', '')) if isinstance(psu['fan_size'], str) else psu['fan_size']
            score += fan_size * weights['fan_size']

        if 'noise_level' in psu:
            noise = float(psu['noise_level'].replace('dB', '')) if isinstance(psu['noise_level'], str) else psu[
                'noise_level']
            score -= noise * abs(weights['noise_level'])

        if 'warranty' in psu:
            warranty = int(psu['warranty'].replace(' years', '')) if isinstance(psu['warranty'], str) else psu[
                'warranty']
            score += warranty * weights['warranty']

        if 'price' in psu and psu['price'] > 0:
            score -= psu['price'] * abs(weights['price'])

        if score > best_score:
            best_score = score
            best_psu = psu

    return best_psu, best_score


# Пример энергопотребления комплектующих (в ваттах)
components_power = {
    'cpu': 150,  # Процессор
    'gpu': 300,  # Видеокарта
    'ram': 15,  # Память
    'ssd': 10,  # Накопители
    'motherboard': 50,  # Материнская плата
    'fans': 15,  # Вентиляторы
    'other': 30  # Прочее
}

# Пример списка блоков питания
psu_list = [
    {
        'name': 'Seasonic PRIME TX-1000',
        'wattage': 1000,
        'efficiency': '80+ Titanium',
        'modular': 'Full',
        'connectors': {
            'pcie_8pin': 4,
            'cpu_8pin': 2,
            'sata': 12,
            'molex': 4
        },
        'fan_size': '135mm',
        'noise_level': '15dB',
        'warranty': '12 years',
        'price': 25000
    },
    {
        'name': 'Corsair RM850x',
        'wattage': 850,
        'efficiency': '80+ Gold',
        'modular': 'Full',
        'connectors': {
            'pcie_8pin': 3,
            'cpu_8pin': 2,
            'sata': 8,
            'molex': 4
        },
        'fan_size': '140mm',
        'noise_level': '22dB',
        'warranty': '10 years',
        'price': 15000
    },
    {
        'name': 'Be Quiet! Pure Power 11 600W',
        'wattage': 600,
        'efficiency': '80+ Gold',
        'modular': 'Semi',
        'connectors': {
            'pcie_8pin': 2,
            'cpu_8pin': 1,
            'sata': 6,
            'molex': 3
        },
        'fan_size': '120mm',
        'noise_level': '25dB',
        'warranty': '5 years',
        'price': 7000
    },
    {
        'name': 'Aerocool Lux 550W',
        'wattage': 550,
        'efficiency': '80+ Bronze',
        'modular': 'No',
        'connectors': {
            'pcie_8pin': 1,
            'cpu_8pin': 1,
            'sata': 4,
            'molex': 3
        },
        'fan_size': '120mm',
        'noise_level': '28dB',
        'warranty': '3 years',
        'price': 3500
    }
]

# Выбираем лучший БП
best_psu, score = select_best_psu(psu_list, components_power)
print(f"Общее энергопотребление системы: {sum(components_power.values())}W")
print(f"Рекомендуемая мощность БП: {((sum(components_power.values()) * 1.2) // 50 + 1) * 50}W")
print(f"\nЛучший блок питания:")
print(f"{best_psu['name']} (Оценка: {score:.2f})")
print(f"Мощность: {best_psu['wattage']}W")
print(f"Эффективность: {best_psu.get('efficiency', 'не указана')}")
print(f"Цена: {best_psu['price']} руб.")