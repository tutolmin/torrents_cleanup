#!/usr/bin/env python3

from transmission_rpc import Client

# Подключение к Transmission
client = Client(
    host="127.0.0.1",
    port=9091,
    username="",
    password=""
)

# Получаем первый торрент
torrents = client.get_torrents()
if not torrents:
    print("Нет активных торрентов")
    exit()

first_torrent = torrents[0]
print(f"Торрент: {first_torrent.name}")

# Получаем и выводим все файлы
files = first_torrent.get_files()
print(f"Всего файлов: {len(files)}")
print("-" * 50)

for file in files:
    print(f"ID: {file.id}")
    print(f"Имя: {file.name}")
    print(f"Размер: {file.size / (1024**2):.2f} MB")
    print(f"Скачано: {file.completed}%")
    print(f"Приоритет: {file.priority}")
    print("-" * 50)
