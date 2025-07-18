def select_best_cooler(coolers_list, cpu_socket=None, tdp=None, weights=None):
    """
    Выбирает лучшую систему охлаждения с учётом сокета и TDP процессора.

    :param coolers_list: Список словарей с характеристиками кулеров
    :param cpu_socket: Сокет процессора (если None - игнорируется совместимость)
    :param tdp: TDP процессора (в ваттах) для проверки достаточности охлаждения
    :param weights: Веса характеристик (можно настроить)
    :return: Лучший кулер и его оценка
    """
    if not coolers_list:
        return None, 0

    # Веса характеристик по умолчанию
    default_weights = {
        'cooling_type': 1.5,  # Тип охлаждения (воздух/вода)
        'tdp_rating': 2.0,  # Заявленный TDP охлаждения
        'noise_level': -1.2,  # Уровень шума (чем меньше, тем лучше)
        'fan_size': 0.8,  # Размер вентилятора (мм)
        'radiator_size': 1.5,  # Размер радиатора (для СЖО)
        'heat_pipes': 1.0,  # Количество тепловых трубок
        'price': -1.0,  # Цена
        'rgb': 0.3,  # Наличие подсветки
        'warranty': 0.5  # Срок гарантии
    }

    weights = weights or default_weights

    best_cooler = None
    best_score = -float('inf')

    for cooler in coolers_list:
        # Проверка совместимости с сокетом
        if cpu_socket and cpu_socket not in cooler.get('sockets', []):
            continue

        # Проверка на достаточность охлаждения (если указан TDP процессора)
        if tdp and cooler.get('tdp_rating', 0) < tdp:
            continue

        score = 0

        # Тип охлаждения (СЖО получает больше баллов)
        if 'cooling_type' in cooler:
            type_score = 2 if cooler['cooling_type'].lower() in ['liquid', 'aio'] else 1
            score += type_score * weights['cooling_type']

        # Основные характеристики
        if 'tdp_rating' in cooler:
            score += cooler['tdp_rating'] * weights['tdp_rating']

        if 'noise_level' in cooler:
            noise = float(cooler['noise_level'].replace('dB', '')) if isinstance(cooler['noise_level'], str) else \
            cooler['noise_level']
            score -= noise * abs(weights['noise_level'])  # Чем тише, тем лучше

        if 'fan_size' in cooler:
            size = int(cooler['fan_size'].replace('mm', '')) if isinstance(cooler['fan_size'], str) else cooler[
                'fan_size']
            score += size * weights['fan_size'] / 10  # Нормализуем

        if 'radiator_size' in cooler:
            rad_size = int(cooler['radiator_size'].replace('mm', '')) if isinstance(cooler['radiator_size'], str) else \
            cooler['radiator_size']
            score += rad_size * weights['radiator_size'] / 10  # Нормализуем

        if 'heat_pipes' in cooler:
            score += cooler['heat_pipes'] * weights['heat_pipes']

        if 'rgb' in cooler and cooler['rgb']:
            score += weights['rgb']

        if 'warranty' in cooler:
            warranty_years = int(cooler['warranty'].replace(' years', '')) if isinstance(cooler['warranty'], str) else \
            cooler['warranty']
            score += warranty_years * weights['warranty']

        if 'price' in cooler and cooler['price'] > 0:
            score -= cooler['price'] * abs(weights['price'])

        if score > best_score:
            best_score = score
            best_cooler = cooler

    return best_cooler, best_score


# Пример списка систем охлаждения
coolers = [
    {
        'name': 'Noctua NH-D15',
        'cooling_type': 'air',
        'sockets': ['AM5', 'LGA1700', 'AM4', 'LGA1200'],
        'tdp_rating': 220,
        'noise_level': '24.6dB',
        'fan_size': '140mm',
        'heat_pipes': 6,
        'price': 9000,
        'rgb': False,
        'warranty': '6 years'
    },
    {
        'name': 'Arctic Liquid Freezer II 360',
        'cooling_type': 'liquid',
        'sockets': ['AM5', 'LGA1700', 'AM4', 'LGA1200'],
        'tdp_rating': 300,
        'noise_level': '22.5dB',
        'radiator_size': '360mm',
        'fan_size': '120mm',
        'price': 12000,
        'rgb': True,
        'warranty': '2 years'
    },
    {
        'name': 'Cooler Master Hyper 212',
        'cooling_type': 'air',
        'sockets': ['AM5', 'LGA1700', 'AM4', 'LGA1200'],
        'tdp_rating': 150,
        'noise_level': '26dB',
        'fan_size': '120mm',
        'heat_pipes': 4,
        'price': 3500,
        'rgb': False,
        'warranty': '2 years'
    },
    {
        'name': 'Corsair iCUE H150i Elite',
        'cooling_type': 'liquid',
        'sockets': ['AM5', 'LGA1700', 'AM4'],
        'tdp_rating': 350,
        'noise_level': '20.1dB',
        'radiator_size': '360mm',
        'fan_size': '120mm',
        'price': 18000,
        'rgb': True,
        'warranty': '5 years'
    }
]

# Пример использования
cpu_socket = 'AM5'
cpu_tdp = 150  # Например, для Ryzen 7 7700X
best_cooler, score = select_best_cooler(coolers, cpu_socket, cpu_tdp)
print(f"Лучшая система охлаждения для сокета {cpu_socket} и TDP {cpu_tdp}W:")
print(f"{best_cooler['name']} (Оценка: {score:.2f})")
print("Характеристики:", best_cooler)

# Без учёта TDP (только сокет)
best_cooler_socket, score_socket = select_best_cooler(coolers, cpu_socket)
print(f"\nЛучшая система охлаждения для сокета {cpu_socket} (без учёта TDP):")
print(f"{best_cooler_socket['name']} (Оценка: {score_socket:.2f})")

# Полностью без ограничений
best_cooler_general, score_general = select_best_cooler(coolers)
print(f"\nЛучшая система охлаждения (без ограничений):")
print(f"{best_cooler_general['name']} (Оценка: {score_general:.2f})")