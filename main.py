import sys
import os
import time
import traceback
from pathlib import Path


# ============================================
# НАСТРОЙКА ПУТЕЙ ДЛЯ PyInstaller
# ============================================

def setup_paths():
    """
    Настройка путей для корректной работы в EXE и при разработке.
    PyInstaller упаковывает все файлы во временную директорию.
    """

    if getattr(sys, 'frozen', False):
        # Режим EXE: файлы во временной папке _MEIPASS
        base_dir = sys._MEIPASS
        app_dir = os.path.dirname(sys.executable)  # где лежит exe файл
    else:
        # Режим разработки: файлы в текущей директории
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = base_dir

    # Добавляем пути для импортов
    paths_to_add = [
        base_dir,
        os.path.join(base_dir, 'Gui'),
        os.path.join(base_dir, 'Services'),
        os.path.join(base_dir, 'Shared'),
        os.path.join(base_dir, 'Models'),
        os.path.join(base_dir, 'Services', 'Driver'),
        os.path.join(base_dir, 'Services', 'Car'),
        os.path.join(base_dir, 'Services', 'Route'),
        os.path.join(base_dir, 'Services', 'Rate'),
        os.path.join(base_dir, 'Services', 'Transportation'),
    ]

    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)

    return base_dir, app_dir


def setup_environment(app_dir):
    """
    Настройка переменных окружения для подключения к PostgreSQL.
    Можно читать из конфиг файла рядом с EXE.
    """
    config_file = os.path.join(app_dir, 'config.ini')

    if os.path.exists(config_file):
        # Читаем конфиг из файла
        import configparser
        config = configparser.ConfigParser()
        config.read(config_file)

        # Устанавливаем переменные окружения для подключения к БД
        if 'DATABASE' in config:
            os.environ['DB_HOST'] = config['DATABASE'].get('host', 'localhost')
            os.environ['DB_PORT'] = config['DATABASE'].get('port', '5432')
            os.environ['DB_NAME'] = config['DATABASE'].get('name', 'transportation_db')
            os.environ['DB_USER'] = config['DATABASE'].get('user', 'postgres')
            os.environ['DB_PASSWORD'] = config['DATABASE'].get('password', 'password')
    else:
        # Значения по умолчанию (для Docker Compose)
        os.environ.setdefault('DB_HOST', 'localhost')
        os.environ.setdefault('DB_PORT', '5432')
        os.environ.setdefault('DB_NAME', 'transportation_db')
        os.environ.setdefault('DB_USER', 'postgres')
        os.environ.setdefault('DB_PASSWORD', 'password')

        # Создаем пример конфиг файла
        create_example_config(app_dir)


def create_example_config(app_dir):
    """Создать пример конфиг файла"""
    config_path = os.path.join(app_dir, 'config.ini.example')
    example_config = """[DATABASE]
# Подключение к PostgreSQL (должна быть запущена в Docker)
host = localhost
port = 5432
name = transportation_db
user = postgres
password = password

[APPLICATION]
# Настройки приложения
language = ru
theme = light
"""

    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(example_config)


def check_database_connection():
    """Проверка подключения к PostgreSQL"""
    try:
        # Импортируем здесь, после настройки путей
        from Shared.DataBaseSession import SyncDatabase

        # Пробуем подключиться
        session = SyncDatabase.get_session()
        result = session.execute("SELECT 1").scalar()
        session.close()

        if result == 1:
            print("✅ Подключение к PostgreSQL установлено")
            return True
        else:
            print("❌ Не удалось подключиться к PostgreSQL")
            return False

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ПРИЛОЖЕНИЯ
# ============================================

def main():
    """Точка входа приложения"""

    print("=" * 50)
    print("Система управления перевозками")
    print("=" * 50)

    try:
        # 1. Настраиваем пути для PyInstaller
        base_dir, app_dir = setup_paths()
        print(f"📁 Базовая директория: {base_dir}")
        print(f"📁 Директория приложения: {app_dir}")

        # 2. Настраиваем окружение для БД
        setup_environment(app_dir)
        print("⚙️  Настройки окружения загружены")

        # 3. Проверяем наличие конфига
        config_file = os.path.join(app_dir, 'config.ini')
        if os.path.exists(config_file):
            print("📄 Конфигурационный файл найден")
        else:
            print("⚠️  Конфигурационный файл не найден, используются значения по умолчанию")

        # 4. Импортируем Qt (только после настройки путей!)
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt

        # 5. Импортируем главное окно
        from Gui.main_window import MainWindow

        # 6. Создаем Qt приложение
        app = QApplication(sys.argv)
        app.setApplicationName("Система управления перевозками")
        app.setOrganizationName("Transportation Corp")

        # 7. Устанавливаем стиль (опционально)
        app.setStyle('Fusion')

        # 8. Создаем и показываем главное окно
        window = MainWindow()
        window.show()

        print("✅ Приложение запущено успешно")

        # 9. Запускаем цикл событий
        return_code = app.exec()

        print("👋 Приложение завершено")
        return return_code

    except ImportError as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось импортировать модуль")
        print(f"   Модуль: {e.name}")
        print(f"   Путь Python: {sys.path}")
        print("\n   Проверьте что все файлы добавлены в PyInstaller:")
        print("   --add-data='Gui;Gui'")
        print("   --add-data='Services;Services'")
        print("   --add-data='Shared;Shared'")
        traceback.print_exc()

    except Exception as e:
        print(f"\n❌ НЕИЗВЕСТНАЯ ОШИБКА: {e}")
        traceback.print_exc()

    # Пауза перед выходом (только в EXE режиме)
    if getattr(sys, 'frozen', False) and sys.platform == 'win32':
        # Для Windows EXE - показываем MessageBox вместо input()
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0,
                                             "Приложение завершилось с ошибкой.\n\n" + str(e),
                                             "Ошибка",
                                             0)
        except:
            pass  # Просто выходим без паузы
        time.sleep(2)  # Небольшая задержка перед выходом

    return 1


# ============================================
# ТОЧКА ВХОДА
# ============================================

if __name__ == "__main__":
    sys.exit(main())