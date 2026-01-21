# Gui/assignment_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AssignmentDialog(QDialog):
    """Диалог для управления назначениями водителей и автомобилей"""

    def __init__(self, parent=None, drivers=None, cars=None):
        super().__init__(parent)
        self.setWindowTitle("Управление назначениями")
        self.resize(800, 500)

        self.drivers = drivers or []
        self.cars = cars or []

        # Списки
        self.drivers_list = QListWidget()
        self.cars_list = QListWidget()

        # Кнопки
        self.assign_btn = QPushButton("➡ Назначить")
        self.unassign_btn = QPushButton("❌ Открепить")
        self.swap_btn = QPushButton("🔄 Поменять")
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.close_btn = QPushButton("✖ Закрыть")

        # Информационная панель
        self.info_label = QLabel("Выберите водителя и автомобиль для назначения")
        self.info_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
                font-weight: bold;
            }
        """)

        # Настройка
        self.setup_ui()
        self.load_data()
        self.setup_connections()

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)

        # Разделитель с двумя списками
        splitter = QSplitter(Qt.Horizontal)

        # Группа водителей
        drivers_group = QGroupBox("Водители")
        drivers_layout = QVBoxLayout()
        drivers_layout.addWidget(QLabel("Доступные водители:"))
        drivers_layout.addWidget(self.drivers_list)
        drivers_group.setLayout(drivers_layout)

        # Группа автомобилей
        cars_group = QGroupBox("Автомобили")
        cars_layout = QVBoxLayout()
        cars_layout.addWidget(QLabel("Доступные автомобили:"))
        cars_layout.addWidget(self.cars_list)
        cars_group.setLayout(cars_layout)

        splitter.addWidget(drivers_group)
        splitter.addWidget(cars_group)
        splitter.setSizes([400, 400])

        main_layout.addWidget(splitter)
        main_layout.addWidget(self.info_label)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.assign_btn)
        btn_layout.addWidget(self.unassign_btn)
        btn_layout.addWidget(self.swap_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.close_btn)

        main_layout.addLayout(btn_layout)

    def setup_connections(self):
        """Настройка соединений"""
        self.drivers_list.itemSelectionChanged.connect(self.update_info)
        self.cars_list.itemSelectionChanged.connect(self.update_info)

        self.assign_btn.clicked.connect(self.assign_driver_to_car)
        self.unassign_btn.clicked.connect(self.unassign_driver)
        self.swap_btn.clicked.connect(self.swap_assignment)
        self.refresh_btn.clicked.connect(self.load_data)
        self.close_btn.clicked.connect(self.accept)

    def load_data(self):
        """Загрузить данные в списки"""
        self.drivers_list.clear()
        self.cars_list.clear()

        # Загружаем водителей
        for driver in self.drivers:
            item_text = f"👤 {driver['full_name']}\n"
            item_text += f"   📋 Права: {driver['license_number']} ({driver['license_category']})\n"
            item_text += f"   ⭐ Стаж: {driver['experience_years']} лет"

            if driver['car_info'] and driver['car_info']['full_info'] != "Не назначен":
                item_text += f"\n   🚗 Авто: {driver['car_info']['full_info']}"
                item_text = f"✅ {item_text}"
            else:
                item_text = f"⏳ {item_text}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, driver)

            # Устанавливаем шрифт
            font = QFont()
            font.setPointSize(10)
            item.setFont(font)

            # Устанавливаем цвет в зависимости от статуса
            if driver.get('car_id'):
                item.setForeground(Qt.darkGreen)
            else:
                item.setForeground(Qt.darkGray)

            self.drivers_list.addItem(item)

        # Загружаем автомобили
        for car in self.cars:
            # Проверяем наличие всех необходимых полей
            load_capacity = car.get('load_capacity', 'N/A')
            fuel_consumption = car.get('fuel_consumption', 'N/A')

            item_text = f"🚗 {car['brand']} - {car['license_plate']}\n"
            item_text += f"   📦 Кузов: {car['body_type']}\n"
            item_text += f"   ⚖ Груз: {load_capacity} т\n"
            item_text += f"   ⛽ Расход: {fuel_consumption} л/100км"

            if car['has_driver']:
                item_text += f"\n   👤 Водитель: {car['driver_info']}"
                item_text = f"✅ {item_text}"
            else:
                item_text = f"🆓 {item_text}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, car)

            # Устанавливаем шрифт
            font = QFont()
            font.setPointSize(10)
            item.setFont(font)

            # Устанавливаем цвет в зависимости от статуса
            if car['has_driver']:
                item.setForeground(Qt.darkGreen)
            else:
                item.setForeground(Qt.blue)

            self.cars_list.addItem(item)

    def update_info(self):
        """Обновить информацию о выбранных элементах"""
        selected_drivers = self.drivers_list.selectedItems()
        selected_cars = self.cars_list.selectedItems()

        if selected_drivers and selected_cars:
            driver = selected_drivers[0].data(Qt.UserRole)
            car = selected_cars[0].data(Qt.UserRole)

            driver_name = driver['full_name']
            car_info = f"{car['brand']} ({car['license_plate']})"

            if car['has_driver']:
                current_driver = car['driver_info']
                self.info_label.setText(
                    f"⚠ Автомобиль {car_info} уже назначен водителю {current_driver}.\n"
                    f"Назначить {driver_name} на этот автомобиль?"
                )
                self.assign_btn.setText("🔄 Перепривязать")
            else:
                self.info_label.setText(
                    f"Назначить водителя {driver_name}\n"
                    f"на автомобиль {car_info}?"
                )
                self.assign_btn.setText("➡ Назначить")

            self.assign_btn.setEnabled(True)
        elif selected_drivers:
            driver = selected_drivers[0].data(Qt.UserRole)
            driver_name = driver['full_name']

            if driver.get('car_id'):
                current_car = driver['car_info']['full_info']
                self.info_label.setText(
                    f"Водитель {driver_name} уже назначен на автомобиль {current_car}.\n"
                    f"Вы можете открепить его от автомобиля."
                )
                self.unassign_btn.setEnabled(True)
            else:
                self.info_label.setText(
                    f"Выбран водитель: {driver_name}\n"
                    f"Выберите автомобиль для назначения."
                )
                self.unassign_btn.setEnabled(False)

            self.assign_btn.setEnabled(False)
        elif selected_cars:
            car = selected_cars[0].data(Qt.UserRole)
            car_info = f"{car['brand']} ({car['license_plate']})"

            if car['has_driver']:
                current_driver = car['driver_info']
                self.info_label.setText(
                    f"Автомобиль {car_info} назначен водителю {current_driver}.\n"
                    f"Вы можете открепить водителя или выбрать другого."
                )
                self.unassign_btn.setEnabled(True)
            else:
                self.info_label.setText(
                    f"Выбран автомобиль: {car_info}\n"
                    f"Автомобиль свободен. Выберите водителя для назначения."
                )
                self.unassign_btn.setEnabled(False)

            self.assign_btn.setEnabled(False)
        else:
            self.info_label.setText("Выберите водителя и автомобиль для назначения")
            self.assign_btn.setEnabled(False)
            self.unassign_btn.setEnabled(False)

    def assign_driver_to_car(self):
        """Назначить водителя на автомобиль"""
        selected_drivers = self.drivers_list.selectedItems()
        selected_cars = self.cars_list.selectedItems()

        if not selected_drivers or not selected_cars:
            return

        driver = selected_drivers[0].data(Qt.UserRole)
        car = selected_cars[0].data(Qt.UserRole)

        # Отправляем сигнал родителю для выполнения назначения
        self.parent().assign_driver_to_car_requested(driver['id'], car['id'])
        self.load_data()

    def unassign_driver(self):
        """Открепить водителя от автомобиля"""
        selected_drivers = self.drivers_list.selectedItems()
        selected_cars = self.cars_list.selectedItems()

        if selected_drivers:
            driver = selected_drivers[0].data(Qt.UserRole)
            if driver.get('car_id'):
                # Отправляем сигнал родителю
                self.parent().assign_driver_to_car_requested(driver['id'], None)

        elif selected_cars:
            car = selected_cars[0].data(Qt.UserRole)
            if car['has_driver']:
                # Находим водителя этого автомобиля
                for driver in self.drivers:
                    if driver.get('car_id') == car['id']:
                        self.parent().assign_driver_to_car_requested(driver['id'], None)
                        break

        self.load_data()

    def swap_assignment(self):
        """Поменять автомобили между водителями"""
        selected_drivers = self.drivers_list.selectedItems()

        if len(selected_drivers) != 2:
            QMessageBox.warning(self, "Ошибка", "Выберите ровно двух водителей для обмена")
            return

        driver1 = selected_drivers[0].data(Qt.UserRole)
        driver2 = selected_drivers[1].data(Qt.UserRole)

        # Проверяем, что у водителей есть автомобили для обмена
        if not driver1.get('car_id') and not driver2.get('car_id'):
            QMessageBox.warning(self, "Ошибка",
                                "У обоих водителей нет автомобилей для обмена")
            return

        # Отправляем сигнал родителю
        self.parent().swap_drivers_requested(driver1['id'], driver2['id'])
        self.load_data()