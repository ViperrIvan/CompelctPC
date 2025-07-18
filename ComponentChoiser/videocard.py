def select_best_gpu(gpus_list, weights=None):
    """
    Выбирает лучшую видеокарту из списка на основе взвешенной оценки характеристик.

    :param gpus_list: Список словарей с характеристиками видеокарт.
    :param weights: Словарь с весами характеристик (по умолчанию важны производительность и память).
    :return: Лучшая видеокарта и её оценка.
    """
    if not gpus_list:
        return None, 0

    # Веса характеристик по умолчанию (можно настроить)
    default_weights = {
        'gpu_clock': 1.2,  # Базовая частота GPU
        'boost_clock': 1.5,  # Турбо-частота (важна для производительности)
        'vram_size': 1.8,  # Объём видеопамяти (чем больше, тем лучше)
        'vram_type': 1.0,  # Тип памяти (GDDR6 > GDDR5 и т. д.)
        'memory_bandwidth': 1.3,  # Пропускная способность памяти
        'tflops': 2.0,  # Вычислительная мощность (TFLOPS)
        'tdp': -0.7,  # Энергопотребление (чем меньше, тем лучше)
        'price': -1.0,  # Цена (чем дешевле, тем лучше)
    }

    weights = weights or default_weights

    best_gpu = None
    best_score = -float('inf')

    for gpu in gpus_list:
        score = 0

        # Нормализация и подсчёт очков для каждой характеристики
        if 'gpu_clock' in gpu:
            clock = float(gpu['gpu_clock'].replace('MHz', '')) if isinstance(gpu['gpu_clock'], str) else gpu[
                'gpu_clock']
            score += clock * weights['gpu_clock']

        if 'boost_clock' in gpu:
            boost = float(gpu['boost_clock'].replace('MHz', '')) if isinstance(gpu['boost_clock'], str) else gpu[
                'boost_clock']
            score += boost * weights['boost_clock']

        if 'vram_size' in gpu:
            vram = int(gpu['vram_size'].replace('GB', '')) if isinstance(gpu['vram_size'], str) else gpu['vram_size']
            score += vram * weights['vram_size']

        if 'vram_type' in gpu:
            # Присваиваем баллы в зависимости от типа памяти
            vram_type_scores = {
                'GDDR6': 10,
                'GDDR6X': 12,
                'GDDR5': 6,
                'HBM2': 8,
                'HBM3': 15
            }
            vram_type = gpu['vram_type']
            score += vram_type_scores.get(vram_type, 5) * weights['vram_type']

        if 'memory_bandwidth' in gpu:
            bandwidth = float(gpu['memory_bandwidth'].replace('GB/s', '')) if isinstance(gpu['memory_bandwidth'],
                                                                                         str) else gpu[
                'memory_bandwidth']
            score += bandwidth * weights['memory_bandwidth']

        if 'tflops' in gpu:
            tflops = float(gpu['tflops'].replace('TFLOPS', '')) if isinstance(gpu['tflops'], str) else gpu['tflops']
            score += tflops * weights['tflops']

        if 'tdp' in gpu:
            tdp = int(gpu['tdp'].replace('W', '')) if isinstance(gpu['tdp'], str) else gpu['tdp']
            score -= tdp * abs(weights['tdp'])  # Чем больше TDP, тем хуже

        if 'price' in gpu and gpu['price'] > 0:
            score -= gpu['price'] * abs(weights['price'])  # Чем выше цена, тем хуже

        if score > best_score:
            best_score = score
            best_gpu = gpu

    return best_gpu, best_score


# Пример списка видеокарт
gpus = [
    {
        'name': 'NVIDIA RTX 4090',
        'gpu_clock': '2235MHz',
        'boost_clock': '2520MHz',
        'vram_size': '24GB',
        'vram_type': 'GDDR6X',
        'memory_bandwidth': '1008GB/s',
        'tflops': '82.6TFLOPS',
        'tdp': '450W',
        'price': 200000
    },
    {
        'name': 'AMD RX 7900 XTX',
        'gpu_clock': '1900MHz',
        'boost_clock': '2500MHz',
        'vram_size': '24GB',
        'vram_type': 'GDDR6',
        'memory_bandwidth': '960GB/s',
        'tflops': '61TFLOPS',
        'tdp': '355W',
        'price': 120000
    },
    {
        'name': 'NVIDIA RTX 4080',
        'gpu_clock': '2205MHz',
        'boost_clock': '2505MHz',
        'vram_size': '16GB',
        'vram_type': 'GDDR6X',
        'memory_bandwidth': '736GB/s',
        'tflops': '48.7TFLOPS',
        'tdp': '320W',
        'price': 110000
    }
]

best_gpu, score = select_best_gpu(gpus)
print(f"Лучшая видеокарта: {best_gpu['name']} (Оценка: {score:.2f})")
print("Характеристики:", best_gpu)