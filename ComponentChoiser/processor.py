def select_best_cpu(cpus_list, weights=None):
    """
    Выбирает лучший процессор из списка на основе взвешенной оценки характеристик.

    :param cpus_list: Список словарей с характеристиками процессоров.
    :param weights: Словарь с весами характеристик (по умолчанию все равны 1).
    :return: Лучший процессор и его оценку.
    """
    if not cpus_list:
        return None, 0

    # Веса характеристик по умолчанию (можно настроить)
    default_weights = {
        'cores': 1.5,  # Ядра важны для многопоточности
        'threads': 1.2,  # Потоки улучшают многозадачность
        'frequency': 1.3,  # Тактовая частота важна для игр
        'turbo_frequency': 1.1,  # Турбо-буст добавляет производительности
        'cache': 1.0,  # Кэш ускоряет обработку данных
        'tdp': -0.5,  # Высокий TDP — больше тепла и энергопотребление (минус)
        'price': -0.7,  # Высокая цена — минус (если указана)
    }

    weights = weights or default_weights

    best_cpu = None
    best_score = -float('inf')

    for cpu in cpus_list:
        score = 0

        # Считаем оценку для каждой характеристики
        for key, weight in weights.items():
            if key in cpu:
                # Нормализуем частоту (переводим ГГц в МГц для единообразия)
                if key in ['frequency', 'turbo_frequency']:
                    value = float(cpu[key].replace('GHz', '')) * 1000 if isinstance(cpu[key], str) else cpu[key] * 1000
                else:
                    value = cpu[key]

                score += value * weight

        # Учитываем цену (если она указана)
        if 'price' in cpu and cpu['price'] > 0:
            score -= cpu['price'] * abs(weights.get('price', 0))

        if score > best_score:
            best_score = score
            best_cpu = cpu

    return best_cpu, best_score


# Пример списка процессоров
cpus = [
    {
        'name': 'Intel Core i5-13600K',
        'cores': 14,  # 6P + 8E
        'threads': 20,
        'frequency': '3.5GHz',
        'turbo_frequency': '5.1GHz',
        'cache': '24MB',
        'tdp': 125,
        'price': 25000
    },
    {
        'name': 'AMD Ryzen 7 7700X',
        'cores': 8,
        'threads': 16,
        'frequency': '4.5GHz',
        'turbo_frequency': '5.4GHz',
        'cache': '32MB',
        'tdp': 105,
        'price': 30000
    },
    {
        'name': 'Intel Core i9-13900K',
        'cores': 24,  # 8P + 16E
        'threads': 32,
        'frequency': '3.0GHz',
        'turbo_frequency': '5.8GHz',
        'cache': '36MB',
        'tdp': 125,
        'price': 50000
    }
]

best_cpu, score = select_best_cpu(cpus)
print(f"Лучший процессор: {best_cpu['name']} (Оценка: {score:.2f})")
print("Характеристики:", best_cpu)