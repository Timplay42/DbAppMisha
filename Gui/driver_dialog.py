# Gui/driver_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSpinBox, QDateEdit,
    QMessageBox, QComboBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import QDate, Qt
import datetime
from Shared.excel_export import ExcelExporter


class DriverDialog(QDialog):
    """Диалог для создания/редактирования водителя с выбором автомобиля"""

    def __init__(self, parent=None, driver=None, available_cars=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование водителя" if driver else "Добавление водителя")
        self.setMinimumWidth(700)  # Увеличил для кнопок экспорта

        self.driver = driver
        self.available_cars = available_cars or []

        # Сохраняем ссылку на родительское окно для доступа к сессии
        self.main_window = parent

        # Основные поля
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Фамилия Имя Отчество")

        self.license_number_input = QLineEdit()
        self.license_number_input.setPlaceholderText("1234 567890")

        self.license_category_input = QComboBox()
        self.license_category_input.addItems(["A", "B", "C", "D", "BE", "CE", "DE"])

        self.experience_years_input = QSpinBox()
        self.experience_years_input.setMinimum(0)
        self.experience_years_input.setMaximum(60)
        self.experience_years_input.setSuffix(" лет")

        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setDisplayFormat("dd.MM.yyyy")
        self.hire_date_input.setMaximumDate(QDate.currentDate())

        # Выбор автомобиля
        self.car_selection_group = QGroupBox("Назначение автомобиля")
        car_layout = QVBoxLayout()

        self.car_combo = QComboBox()
        self.car_combo.addItem("Не назначен", None)

        for car in self.available_cars:
            self.car_combo.addItem(car["full_info"], car["id"])

        self.current_car_label = QLabel("")
        self.current_car_label.setStyleSheet("color: #666; font-style: italic;")

        car_layout.addWidget(QLabel("Выберите автомобиль:"))
        car_layout.addWidget(self.car_combo)
        car_layout.addWidget(self.current_car_label)
        self.car_selection_group.setLayout(car_layout)

        # Кнопки экспорта в Excel
        self.export_group = QGroupBox("Экспорт в Excel")
        export_layout = QVBoxLayout()

        # Кнопка 1: Все водители
        self.export_all_btn = QPushButton("👥 Экспорт всех водителей")
        self.export_all_btn.clicked.connect(self.export_all_drivers)

        # Кнопка 2: Водители со стажем > 10 лет
        self.export_experienced_btn = QPushButton("⭐ Водители со стажем > 10 лет")
        self.export_experienced_btn.clicked.connect(self.export_experienced_drivers)

        # Кнопка 3: Водители без автомобиля
        self.export_without_car_btn = QPushButton("🚫 Водители без автомобиля")
        self.export_without_car_btn.clicked.connect(self.export_drivers_without_car)

        export_layout.addWidget(self.export_all_btn)
        export_layout.addWidget(self.export_experienced_btn)
        export_layout.addWidget(self.export_without_car_btn)
        self.export_group.setLayout(export_layout)

        # Кнопки сохранения/отмены
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.validate_and_accept)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.clicked.connect(self.reject)

        # Разметка
        layout = QVBoxLayout(self)

        # Сетка для основных полей
        grid = QGridLayout()
        grid.addWidget(QLabel("ФИО *"), 0, 0)
        grid.addWidget(self.full_name_input, 0, 1)

        grid.addWidget(QLabel("Номер прав *"), 1, 0)
        grid.addWidget(self.license_number_input, 1, 1)

        grid.addWidget(QLabel("Категория *"), 2, 0)
        grid.addWidget(self.license_category_input, 2, 1)

        grid.addWidget(QLabel("Стаж (лет) *"), 3, 0)
        grid.addWidget(self.experience_years_input, 3, 1)

        grid.addWidget(QLabel("Дата приема *"), 4, 0)
        grid.addWidget(self.hire_date_input, 4, 1)

        layout.addLayout(grid)
        layout.addWidget(self.car_selection_group)
        layout.addWidget(self.export_group)  # Добавляем группу экспорта

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Если передан объект водителя - заполняем поля
        if driver:
            self.load_data(driver)

    # ========== МЕТОДЫ ЭКСПОРТА ==========

    def get_session(self):
        """Получить сессию БД из главного окна"""
        if self.main_window and hasattr(self.main_window, 'session'):
            return self.main_window.session
        return None

    def export_all_drivers(self):
        """Экспорт всех водителей в Excel"""
        try:
            from Services.Driver.services import get_all_drivers_with_cars

            session = self.get_session()
            if not session:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к базе данных")
                return

            drivers = get_all_drivers_with_cars(session)

            # Подготавливаем данные для экспорта
            export_data = []
            for driver in drivers:
                export_data.append({
                    "ID": driver.get("id", ""),
                    "ФИО": driver.get("full_name", ""),
                    "Номер прав": driver.get("license_number", ""),
                    "Категория": driver.get("license_category", ""),
                    "Стаж (лет)": driver.get("experience_years", 0),
                    "Дата приема": driver.get("hire_date", ""),
                    "ID автомобиля": driver.get("car_id", ""),
                    "Автомобиль": driver.get("car_info", {}).get("full_info", "Не назначен"),
                    "Марка автомобиля": driver.get("car_info", {}).get("brand", ""),
                    "Госномер": driver.get("car_info", {}).get("license_plate", "")
                })

            # Экспорт в Excel
            filepath = ExcelExporter.export_to_excel(
                export_data,
                "Все_водители",
                "Водители"
            )

            ExcelExporter.show_success_message(filepath, self)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def export_experienced_drivers(self):
        """Экспорт водителей со стажем более 10 лет"""
        #try:
        from Services.Driver.services import get_all_drivers_with_cars

        session = self.get_session()
        if not session:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к базе данных")
            return

        drivers = get_all_drivers_with_cars(session)

            # Фильтруем водителей со стажем > 10 лет
        experienced_drivers = [
            driver for driver in drivers
            if driver.get("experience_years", 0) > 10
        ]

        export_data = []
        for driver in experienced_drivers:

            export_data.append({
                "ID": driver.get("id", ""),
                "ФИО": driver.get("full_name", ""),
                "Номер прав": driver.get("license_number", ""),
                "Категория": driver.get("license_category", ""),
                "Общий стаж (лет)": driver.get("experience_years", 0),
                "Дата приема": driver.get("hire_date", ""),
                "ID автомобиля": driver.get("car_id", ""),
                "Автомобиль": driver.get("car_info", {}).get("full_info", "Не назначен"),
                "Статус": "Опытный водитель"
            })

        filepath = ExcelExporter.export_to_excel(
            export_data,
            "Водители_со_стажем_более_10_лет",
            "Опытные водители"
        )

        ExcelExporter.show_success_message(filepath, self)

        #except Exception as e:
        #    QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    def export_drivers_without_car(self):
        """Экспорт водителей без назначенного автомобиля"""
        try:
            from Services.Driver.services import get_all_drivers_with_cars

            session = self.get_session()
            if not session:
                QMessageBox.warning(self, "Ошибка", "Не удалось получить доступ к базе данных")
                return

            drivers = get_all_drivers_with_cars(session)

            # Фильтруем водителей без машины
            drivers_without_car = [
                driver for driver in drivers
                if not driver.get("car_id")
            ]

            export_data = []
            for driver in drivers_without_car:
                export_data.append({
                    "ID": driver.get("id", ""),
                    "ФИО": driver.get("full_name", ""),
                    "Номер прав": driver.get("license_number", ""),
                    "Категория": driver.get("license_category", ""),
                    "Стаж (лет)": driver.get("experience_years", 0),
                    "Дата приема": driver.get("hire_date", ""),
                    "Статус": "Требуется автомобиль",
                    "Приоритет": "Высокий" if driver.get("experience_years", 0) > 5 else "Средний",
                    "Рекомендация": "Назначить автомобиль"
                })

            filepath = ExcelExporter.export_to_excel(
                export_data,
                "Водители_без_автомобиля",
                "Водители без авто"
            )

            ExcelExporter.show_success_message(filepath, self)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать данные: {str(e)}")

    # ========== СУЩЕСТВУЮЩИЕ МЕТОДЫ ==========

    def load_data(self, driver):
        """Заполнить поля данными водителя"""
        self.full_name_input.setText(driver.get("full_name", ""))
        self.license_number_input.setText(driver.get("license_number", ""))
        self.license_category_input.setCurrentText(driver.get("license_category", "B"))
        self.experience_years_input.setValue(driver.get("experience_years", 0))

        # Дата приема
        hire_date = driver.get("hire_date")
        if hire_date:
            if isinstance(hire_date, str):
                hire_date = datetime.date.fromisoformat(hire_date)
            qdate = QDate(hire_date.year, hire_date.month, hire_date.day)
            self.hire_date_input.setDate(qdate)

        # Автомобиль
        car_id = driver.get("car_id")
        if car_id:
            # Ищем автомобиль в списке доступных
            for i in range(self.car_combo.count()):
                if self.car_combo.itemData(i) == car_id:
                    self.car_combo.setCurrentIndex(i)
                    break

            car_info = driver.get("car_info", {})
            if car_info and car_info.get("full_info"):
                self.current_car_label.setText(f"Текущий: {car_info['full_info']}")

    def validate_and_accept(self):
        """Проверка данных перед сохранением"""
        errors = []

        if not self.full_name_input.text().strip():
            errors.append("Введите ФИО водителя")

        if not self.license_number_input.text().strip():
            errors.append("Введите номер водительского удостоверения")

        if self.experience_years_input.value() < 0:
            errors.append("Стаж не может быть отрицательным")

        if errors:
            QMessageBox.warning(self, "Ошибка заполнения", "\n".join(errors))
            return

        self.accept()

    def get_data(self):
        """Получить данные из формы"""
        # Дата приема
        qdate = self.hire_date_input.date()
        hire_date = datetime.date(qdate.year(), qdate.month(), qdate.day())

        # Выбранный автомобиль
        car_id = self.car_combo.currentData()

        return {
            "full_name": self.full_name_input.text().strip(),
            "license_number": self.license_number_input.text().strip(),
            "license_category": self.license_category_input.currentText(),
            "experience_years": self.experience_years_input.value(),
            "hire_date": hire_date.isoformat(),
            "car_id": car_id
        }