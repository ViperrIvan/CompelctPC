def select_best_motherboard(motherboards_list, cpu_socket=None, weights=None):
    """
    Выбирает лучшую материнскую плату из списка с учетом сокета процессора.

    :param motherboards_list: Список словарей с характеристиками материнских плат
    :param cpu_socket: Сокет процессора (если None - игнорируется совместимость)
    :param weights: Веса характеристик (можно настроить под свои нужды)
    :return: Лучшая материнская плата и ее оценка
    """
    if not motherboards_list:
        return None, 0

    # Веса характеристик по умолчанию
    default_weights = {
        'chipset': 1.2,  # Чем новее чипсет, тем лучше
        'ram_slots': 0.8,  # Количество слотов ОЗУ
        'max_ram': 1.5,  # Максимальный объем ОЗУ (в ГБ)
        'ram_speed': 1.0,  # Поддержка частоты RAM
        'm2_slots': 1.3,  # Количество M.2 слотов
        'sata_ports': 0.5,  # Количество SATA портов
        'usb_ports': 0.7,  # Количество USB портов (включая USB-C)
        'pcie_slots': 1.2,  # Количество и версия PCIe слотов
        'vrm_quality': 1.4,  # Качество VRM (важно для разгона)
        'price': -1.0,  # Цена (чем дешевле, тем лучше)
        'wifi': 0.6,  # Наличие WiFi
        'bluetooth': 0.4,  # Наличие Bluetooth
        'audio': 0.5  # Качество аудиочипа
    }

    weights = weights or default_weights

    best_mobo = None
    best_score = -float('inf')

    for mobo in motherboards_list:
        # Проверяем совместимость с процессором (если указан сокет)
        if cpu_socket and mobo.get('socket') != cpu_socket:
            continue

        score = 0

        # Обработка чипсета (новые чипсеты получают больше баллов)
        if 'chipset' in mobo:
            chipset = mobo['chipset'].upper()
            # Присваиваем баллы в зависимости от "крутости" чипсета
            if 'X670E' in chipset:
                chip_score = 10
            elif 'Z790' in chipset:
                chip_score = 9
            elif 'B650' in chipset:
                chip_score = 8
            elif 'Z690' in chipset:
                chip_score = 7
            elif 'B660' in chipset:
                chip_score = 6
            else:
                chip_score = 5
            score += chip_score * weights['chipset']

        # Обработка характеристик
        if 'ram_slots' in mobo:
            score += mobo['ram_slots'] * weights['ram_slots']

        if 'max_ram' in mobo:
            max_ram = int(mobo['max_ram'].replace('GB', '')) if isinstance(mobo['max_ram'], str) else mobo['max_ram']
            score += max_ram * weights['max_ram']

        if 'ram_speed' in mobo:
            ram_speed = int(mobo['ram_speed'].replace('MHz', '')) if isinstance(mobo['ram_speed'], str) else mobo[
                'ram_speed']
            score += ram_speed * weights['ram_speed'] / 1000  # Нормализуем

        if 'm2_slots' in mobo:
            score += mobo['m2_slots'] * weights['m2_slots']

        if 'sata_ports' in mobo:
            score += mobo['sata_ports'] * weights['sata_ports']

        if 'usb_ports' in mobo:
            # Учитываем общее количество USB портов
            usb_count = mobo['usb_ports'].get('total', 0) if isinstance(mobo['usb_ports'], dict) else mobo['usb_ports']
            score += usb_count * weights['usb_ports']

        if 'pcie_slots' in mobo:
            # Учитываем количество и версию PCIe слотов
            pcie_score = 0
            for slot in mobo['pcie_slots']:
                version = float(slot['version'].replace('PCIe ', ''))
                pcie_score += version * (1 if slot['x16'] else 0.5)
            score += pcie_score * weights['pcie_slots']

        if 'vrm_quality' in mobo:
            # Оцениваем качество VRM по количеству фаз
            vrm_phases = mobo['vrm_quality'].get('phases', 0) if isinstance(mobo['vrm_quality'], dict) else mobo[
                'vrm_quality']
            score += vrm_phases * weights['vrm_quality']

        if 'wifi' in mobo and mobo['wifi']:
            score += weights['wifi']

        if 'bluetooth' in mobo and mobo['bluetooth']:
            score += weights['bluetooth']

        if 'audio' in mobo:
            # Оцениваем аудио по кодеку (например, ALC1220 лучше ALC897)
            audio_codec = mobo['audio'].get('codec', '') if isinstance(mobo['audio'], dict) else mobo['audio']
            if 'ALC1220' in audio_codec:
                audio_score = 2
            elif 'ALC1200' in audio_codec:
                audio_score = 1.5
            elif 'ALC897' in audio_codec:
                audio_score = 1
            else:
                audio_score = 0.5
            score += audio_score * weights['audio']

        if 'price' in mobo and mobo['price'] > 0:
            score -= mobo['price'] * abs(weights['price'])

        if score > best_score:
            best_score = score
            best_mobo = mobo

    return best_mobo, best_score


# Пример списка материнских плат
motherboards = [
    {
        'name': 'ASUS ROG Crosshair X670E Hero',
        'socket': 'AM5',
        'chipset': 'AMD X670E',
        'ram_slots': 4,
        'max_ram': '128GB',
        'ram_speed': 'DDR5-6400MHz',
        'm2_slots': 4,
        'sata_ports': 6,
        'usb_ports': {'total': 12, 'usb_c': 2},
        'pcie_slots': [
            {'version': 'PCIe 5.0', 'x16': True},
            {'version': 'PCIe 4.0', 'x16': False}
        ],
        'vrm_quality': {'phases': 18},
        'wifi': True,
        'bluetooth': True,
        'audio': {'codec': 'ALC1220'},
        'price': 45000
    },
    {
        'name': 'MSI MPG Z790 Carbon WiFi',
        'socket': 'LGA1700',
        'chipset': 'Intel Z790',
        'ram_slots': 4,
        'max_ram': '128GB',
        'ram_speed': 'DDR5-7200MHz',
        'm2_slots': 5,
        'sata_ports': 6,
        'usb_ports': {'total': 14, 'usb_c': 1},
        'pcie_slots': [
            {'version': 'PCIe 5.0', 'x16': True},
            {'version': 'PCIe 4.0', 'x16': True}
        ],
        'vrm_quality': {'phases': 16},
        'wifi': True,
        'bluetooth': True,
        'audio': {'codec': 'ALC4080'},
        'price': 38000
    },
    {
        'name': 'Gigabyte B650 Aorus Elite AX',
        'socket': 'AM5',
        'chipset': 'AMD B650',
        'ram_slots': 4,
        'max_ram': '128GB',
        'ram_speed': 'DDR5-6000MHz',
        'm2_slots': 3,
        'sata_ports': 4,
        'usb_ports': {'total': 10, 'usb_c': 1},
        'pcie_slots': [
            {'version': 'PCIe 4.0', 'x16': True}
        ],
        'vrm_quality': {'phases': 12},
        'wifi': True,
        'bluetooth': True,
        'audio': {'codec': 'ALC897'},
        'price': 22000
    }
]

# Пример использования
cpu_socket = 'AM5'  # Например, для AMD Ryzen 7000
best_mobo, score = select_best_motherboard(motherboards, cpu_socket)
print(f"Лучшая материнская плата для сокета {cpu_socket}: {best_mobo['name']} (Оценка: {score:.2f})")
print("Характеристики:", best_mobo)

# Без учета сокета
best_mobo_general, score_general = select_best_motherboard(motherboards)
print(f"\nЛучшая материнская плата (без учета сокета): {best_mobo_general['name']} (Оценка: {score_general:.2f})")