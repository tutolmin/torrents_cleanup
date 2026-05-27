#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from transmission_rpc import Client

# ========== НАСТРОЙКИ ==========
TRANSMISSION_HOST = "127.0.0.1"
TRANSMISSION_PORT = 9091
TRANSMISSION_USER = ""
TRANSMISSION_PASS = ""

# ВАЖНО: Укажите путь к вашей папке загрузок
#DOWNLOAD_DIR = "/mnt/data2/films"  # ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ПУТЬ!
###DOWNLOAD_DIR = "/mnt/data2/series"  # ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ПУТЬ!
#DOWNLOAD_DIR = "/mnt/data2/mults"  # ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ПУТЬ!
#DOWNLOAD_DIR = "/mnt/data2/soft"  # ЗАМЕНИТЕ НА ВАШ РЕАЛЬНЫЙ ПУТЬ!
# ===============================

def connect_to_transmission():
    """Подключение к Transmission"""
    print(f"[1] Подключение к Transmission {TRANSMISSION_HOST}:{TRANSMISSION_PORT}...")
    client = Client(
        host=TRANSMISSION_HOST,
        port=TRANSMISSION_PORT,
        username=TRANSMISSION_USER,
        password=TRANSMISSION_PASS
    )
    session = client.get_session()
    print(f"[✓] Успешно. Версия: {session.version}")
    return client

def get_all_torrent_files(client):
    """Получение всех файлов из всех торрентов"""
    print("[2] Получение списка торрентов...")

    torrents = client.get_torrents()
    print(f"[✓] Найдено торрентов: {len(torrents)}")

    known_paths = set()

    for idx, torrent in enumerate(torrents, 1):
        torrent_name = torrent.name
        print(f"   [{idx}/{len(torrents)}] {torrent_name[:50]}...")

        files = torrent.get_files()

        if not files:
            continue

        base_path = Path(torrent.download_dir)

        for file in files:
            full_path = base_path / file.name
            known_paths.add(str(full_path))

        print(f"      Файлов: {len(files)}")

    print(f"[✓] Всего уникальных путей: {len(known_paths)}")
    return known_paths

def find_orphan_files(directory, known_paths, dry_run=True):
    """Поиск файлов-сирот (без обработки папок)"""
    print(f"\n[3] Поиск файлов-сирот в: {directory}")
    print(f"    Режим: {'ПРОСМОТР' if dry_run else 'УДАЛЕНИЕ'}")

    if not os.path.exists(directory):
        print(f"[✗] Директория не существует: {directory}")
        sys.exit(1)

    orphan_files = []
    total_files = 0

    # Исключаемые папки (не заходим внутрь)
    excluded_dirs = {'_incomplete', '.incomplete', 'incomplete', 'temp', 'tmp'}

    print("\n    Поиск...")

    for root, dirs, files in os.walk(directory):
        # Пропускаем исключённые папки
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            total_files += 1
            file_path = os.path.join(root, file)

            if file_path not in known_paths:
                orphan_files.append(file_path)
                if dry_run:
                    print(f"      [СИРОТА] {file_path}")

    print(f"\n[✓] Проверено файлов: {total_files}")
    print(f"[✓] Найдено сирот: {len(orphan_files)}")

    return orphan_files

def delete_files(file_list, dry_run=True):
    """Удаление файлов"""
    if not file_list:
        print("\n[✓] Сирот не найдено. Всё чисто!")
        return

    total_size = 0
    for file_path in file_list:
        try:
            total_size += os.path.getsize(file_path)
        except OSError:
            pass

    print(f"\n[4] Освободится: ~{total_size / (1024**3):.2f} GiB ({len(file_list)} файлов)")

    if not dry_run:
        confirm = input("\n⚠ Удалить эти файлы? (yes/NO): ")
        if confirm.lower() != 'yes':
            print("Отменено.")
            return

        print("\n    Удаление...")
        for file_path in file_list:
            try:
                os.remove(file_path)
                print(f"      [УДАЛЕН] {file_path}")
            except Exception as e:
                print(f"      [ОШИБКА] {file_path}: {e}")

        print("\n[✓] Готово!")

def main():
    print("=" * 60)
    print("ПОИСК ФАЙЛОВ-СИРОТ (не принадлежащих торрентам)")
    print("=" * 60)

    if DOWNLOAD_DIR == "/home/andrei/downloads":
        print("\n[!] Укажите правильный путь DOWNLOAD_DIR в скрипте!")
        sys.exit(1)

    dry_run = True  # False для реального удаления

    client = connect_to_transmission()
    known_paths = get_all_torrent_files(client)
    orphan_files = find_orphan_files(DOWNLOAD_DIR, known_paths, dry_run)
    delete_files(orphan_files, dry_run)

    print("\n" + "=" * 60)
    if dry_run:
        print("РЕЖИМ ПРОСМОТРА: для удаления измените dry_run = False")
    print("=" * 60)

if __name__ == "__main__":
    main()
