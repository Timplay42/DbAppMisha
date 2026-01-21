# Gui/main_window.py
import datetime
from typing import Optional

from Gui.shipment_dialog import ShipmentDialog
from Services.Transportation.service import (
    get_all_shipments, create_shipment, update_shipment, delete_shipment,
    get_available_cars_with_drivers, get_all_drivers,
    get_all_routes, get_active_tariffs,
    calculate_shipment_cost
)

from PySide6.QtWidgets import QStyle
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QApplication,
    QToolBar, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from Gui.assignment_dialog import AssignmentDialog
from Gui.driver_dialog import DriverDialog
from Services.Driver.services import (
    create_driver, update_driver, delete_driver, get_all_cars_for_assignment,
    get_all_drivers_with_cars, assign_driver_to_car, swap_driver_car
)
from Gui.car_dialog import CarDialog
from Services.Car.services import (
    get_all_cars, create_car, update_car, delete_car
)
from Gui.edit_delete_route_dialog import CreateRouteDialogEditDelete
from Services.Route.services import delete_route, update_route
from Shared.DataBaseSession import SyncDatabase
from Services.Route.services import get_all_routes, create_route
from Gui.route_dialog import CreateRouteDialog

from Gui.tariff_dialog import TariffDialog
from Services.Rate.services import (
    get_all_tariffs, create_tariff, update_tariff, delete_tariff
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления перевозками")
        self.resize(1200, 700)

        # УСТАНОВИТЬ БЕЛЫЙ ФОН ДЛЯ ВСЕГО ПРИЛОЖЕНИЯ
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
            }
            QWidget {
                background-color: white;
                color: black;
                font-family: Arial, sans-serif;
            }
            QTabWidget::pane {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: black;
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
            QTableView {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #dddddd;
                selection-background-color: #0078d7;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                color: black;
                padding: 5px;
                border: 1px solid #dddddd;
                font-weight: bold;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                color: black;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #bbbbbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QToolBar {
                background-color: #f8f8f8;
                border: 1px solid #dddddd;
                spacing: 5px;
                padding: 3px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #e8e8e8;
                border-radius: 3px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #cccccc;
                color: black;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0078d7;
            }
            QLabel {
                color: black;
            }
            QMenuBar {
                background-color: #f8f8f8;
                color: black;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #e8e8e8;
            }
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
                color: black;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QStatusBar {
                background-color: #f5f5f5;
                color: #666666;
                border-top: 1px solid #dddddd;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)

        self.session = SyncDatabase.get_session()

        # Создаем центральный виджет
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: white;")  # Дополнительно для центрального виджета
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)

        # Создаем меню
        self.create_menu()

        # Создаем панель инструментов
        self.create_toolbar()

        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
        """)
        self.main_layout.addWidget(self.tabs)

        # Создаем вкладки для разных сущностей
        self.setup_route_tab()
        self.setup_car_tab()
        self.setup_driver_tab()
        self.setup_shipment_tab()

        # Загружаем данные
        self.load_routes()
        self.load_cars()
        self.load_drivers()
        self.load_shipments()

        self.setup_tariff_tab()
        self.load_tariffs()

        # Создаем статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово к работе")

        # Загружаем начальные данные
        self.load_all_data()


    def setup_tariff_tab(self):
        """Настройка вкладки тарифов"""
        self.tariff_tab = QWidget()
        layout = QVBoxLayout(self.tariff_tab)

        # Таблица
        self.tariff_table = QTableWidget(0, 7)  # Уменьшили количество колонок с 8 до 7
        self.tariff_table.setHorizontalHeaderLabels([
            "ID", "Цена за км (руб)",
            "Мин. цена (руб)", "Дата начала", "Дата окончания",
            "Статус", "Описание"
        ])
        self.tariff_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tariff_table.setAlternatingRowColors(True)
        self.tariff_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tariff_table.itemSelectionChanged.connect(self.on_tariff_selected)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.tariff_add_btn = QPushButton("➕ Добавить тариф")
        self.tariff_edit_btn = QPushButton("✏ Редактировать")
        self.tariff_delete_btn = QPushButton("🗑 Удалить")
        self.tariff_view_active_btn = QPushButton("👁 Показать активные")

        self.tariff_add_btn.clicked.connect(self.add_tariff)
        self.tariff_edit_btn.clicked.connect(self.edit_tariff)
        self.tariff_delete_btn.clicked.connect(self.delete_tariff)
        self.tariff_view_active_btn.clicked.connect(self.toggle_active_view)

        self.tariff_edit_btn.setEnabled(False)
        self.tariff_delete_btn.setEnabled(False)

        btn_layout.addWidget(self.tariff_add_btn)
        btn_layout.addWidget(self.tariff_edit_btn)
        btn_layout.addWidget(self.tariff_delete_btn)
        btn_layout.addWidget(self.tariff_view_active_btn)
        btn_layout.addStretch()

        layout.addWidget(self.tariff_table)
        layout.addLayout(btn_layout)

        self.tabs.addTab(self.tariff_tab, "💰 Тарифы")

        self.show_active_tariffs_only = False

    def load_tariffs(self):
        """Загрузить тарифы в таблицу"""
        from PySide6.QtGui import QColor, QFont

        self.tariff_table.setRowCount(0)

        if self.show_active_tariffs_only:
            tariffs = get_all_tariffs(self.session)
        else:
            tariffs = get_all_tariffs(self.session)

        for row, tariff in enumerate(tariffs):
            self.tariff_table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(tariff["id"]))
            id_item.setData(Qt.UserRole, tariff["id"])
            self.tariff_table.setItem(row, 0, id_item)

            # Цена за км (сдвигаем на 1 колонку влево)
            price_item = QTableWidgetItem(f"{tariff['price_per_km']:.2f}")
            price_item.setData(Qt.UserRole, tariff["price_per_km"])
            self.tariff_table.setItem(row, 1, price_item)

            # Минимальная цена (сдвигаем на 1 колонку влево)
            min_price_item = QTableWidgetItem(f"{tariff['min_price']:.2f}")
            min_price_item.setData(Qt.UserRole, tariff["min_price"])
            self.tariff_table.setItem(row, 2, min_price_item)

            # Дата начала (сдвигаем на 1 колонку влево)
            start_date = tariff["date_start"]
            if "T" in start_date:
                start_date = start_date.split("T")[0]
            start_item = QTableWidgetItem(start_date)
            self.tariff_table.setItem(row, 3, start_item)

            # Дата окончания (сдвигаем на 1 колонку влево)
            end_date = tariff["date_end"]
            if end_date:
                if "T" in end_date:
                    end_date = end_date.split("T")[0]
                end_item = QTableWidgetItem(end_date)
            else:
                end_item = QTableWidgetItem("Бессрочно")
            self.tariff_table.setItem(row, 4, end_item)

            # Статус (активный/неактивный) (сдвигаем на 1 колонку влево)
            is_active = tariff.get("is_active", False)
            status_item = QTableWidgetItem("✅ Активен" if is_active else "⏳ Не активен")

            if is_active:
                status_item.setForeground(QColor("green"))
                status_item.setFont(QFont("Arial", 10, QFont.Bold))
            else:
                status_item.setForeground(QColor("gray"))
                status_item.setFont(QFont("Arial", 10, -1, True))

            self.tariff_table.setItem(row, 5, status_item)

            # Описание (обрезаем если длинное) (сдвигаем на 1 колонку влево)
            description = tariff.get("description", "")
            if len(description) > 50:
                description = description[:47] + "..."
            desc_item = QTableWidgetItem(description)
            self.tariff_table.setItem(row, 6, desc_item)

    def add_tariff(self):
        """Добавить новый тариф"""
        try:
            dialog = TariffDialog(self)

            if dialog.exec():
                data = dialog.get_data()

                # Проверка обязательных полей
                required_fields = ["price_per_km", "min_price", "date_start"]
                for field in required_fields:
                    if not data.get(field):
                        QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                        return

                # Дополнительная проверка дат перед отправкой в БД
                if data.get('date_end'):
                    date_start = datetime.datetime.fromisoformat(data['date_start']) if isinstance(data['date_start'],
                                                                                                   str) else data[
                        'date_start']
                    date_end = datetime.datetime.fromisoformat(data['date_end']) if isinstance(data['date_end'],
                                                                                               str) else data[
                        'date_end']

                    if date_end <= date_start:
                        QMessageBox.warning(
                            self,
                            "Ошибка в датах",
                            f"Дата окончания ({date_end.strftime('%d.%m.%Y')}) должна быть позже даты начала ({date_start.strftime('%d.%m.%Y')})"
                        )
                        return

                # Проверка, что дата начала не слишком старая
                date_start = datetime.datetime.fromisoformat(data['date_start']) if isinstance(data['date_start'],
                                                                                               str) else data[
                    'date_start']
                if date_start < datetime.datetime.now() - datetime.timedelta(days=365 * 2):
                    reply = QMessageBox.question(
                        self,
                        "Подтверждение",
                        f"Дата начала тарифа очень старая: {date_start.strftime('%d.%m.%Y')}\n"
                        "Вы уверены, что хотите создать тариф с такой датой?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return

                create_tariff(self.session, **data)
                self.load_tariffs()
                self.status_bar.showMessage("Тариф создан", 3000)

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка в датах", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать тариф: {str(e)}")

    def edit_tariff(self):
        """Редактировать тариф"""
        selected = self.tariff_table.selectedItems()
        if not selected:
            return

        row = self.tariff_table.currentRow()
        tariff_id = int(self.tariff_table.item(row, 0).text())

        # Получаем данные тарифа
        tariffs = get_all_tariffs(self.session)
        tariff = next((t for t in tariffs if t["id"] == tariff_id), None)

        if not tariff:
            QMessageBox.warning(self, "Ошибка", "Тариф не найден")
            return

        try:
            dialog = TariffDialog(self, tariff=tariff)

            if dialog.exec():
                data = dialog.get_data()

                # Проверка обязательных полей
                required_fields = ["price_per_km", "min_price", "date_start"]
                for field in required_fields:
                    if not data.get(field):
                        QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                        return

                # Проверка дат
                if data.get('date_end'):
                    date_start = datetime.datetime.fromisoformat(data['date_start']) if isinstance(data['date_start'],
                                                                                                   str) else data[
                        'date_start']
                    date_end = datetime.datetime.fromisoformat(data['date_end']) if isinstance(data['date_end'],
                                                                                               str) else data[
                        'date_end']

                    if date_end <= date_start:
                        QMessageBox.warning(
                            self,
                            "Ошибка в датах",
                            f"Дата окончания ({date_end.strftime('%d.%m.%Y')}) должна быть позже даты начала ({date_start.strftime('%d.%m.%Y')})"
                        )
                        return

                success = update_tariff(self.session, tariff_id, **data)
                if success:
                    self.load_tariffs()
                    self.status_bar.showMessage("Тариф обновлен", 3000)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить тариф")

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка в датах", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить тариф: {str(e)}")



    def delete_tariff(self):
        """Удалить тариф"""
        selected = self.tariff_table.selectedItems()
        if not selected:
            return

        row = self.tariff_table.currentRow()
        tariff_id = int(self.tariff_table.item(row, 0).text())

        # Проверяем, активен ли тариф
        tariff_data = next((t for t in get_all_tariffs(self.session) if t["id"] == tariff_id), None)
        if tariff_data and tariff_data.get("is_active", False):
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Вы пытаетесь удалить активный тариф.\n"
                "Это может повлиять на будущие перевозки.\n"
                "Продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить тариф #{tariff_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = delete_tariff(self.session, tariff_id)
            if success:
                self.load_tariffs()
                self.status_bar.showMessage("Тариф удален", 3000)
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Не удалось удалить тариф. Возможно, он используется в перевозках.")

    def toggle_active_view(self):
        """Переключить отображение только активных тарифов"""
        self.show_active_tariffs_only = not self.show_active_tariffs_only

        if self.show_active_tariffs_only:
            self.tariff_view_active_btn.setText("👁 Показать все")
        else:
            self.tariff_view_active_btn.setText("👁 Показать активные")

        self.load_tariffs()

    def on_tariff_selected(self):
        """Обработчик выбора тарифа"""
        selected = self.tariff_table.selectedItems()
        has_selection = len(selected) > 0

        self.tariff_edit_btn.setEnabled(has_selection)
        self.tariff_delete_btn.setEnabled(has_selection)

    def setup_shipment_tab(self):
        """Настройка вкладки перевозок"""
        self.shipment_tab = QWidget()
        layout = QVBoxLayout(self.shipment_tab)

        # Таблица (уменьшили количество колонок с 9 до 8)
        self.shipment_table = QTableWidget(0, 8)
        self.shipment_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Вес (кг)", "Статус",
            "Автомобиль", "Водитель", "Маршрут", "Стоимость (руб)"
        ])
        self.shipment_table.setAlternatingRowColors(True)
        self.shipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shipment_table.itemSelectionChanged.connect(self.on_shipment_selected)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.shipment_add_btn = QPushButton("➕ Добавить перевозку")
        self.shipment_edit_btn = QPushButton("✏ Редактировать")
        self.shipment_delete_btn = QPushButton("🗑 Удалить")
        self.shipment_calc_btn = QPushButton("📊 Пересчитать стоимость")

        self.shipment_add_btn.clicked.connect(self.add_shipment)
        self.shipment_edit_btn.clicked.connect(self.edit_shipment)
        self.shipment_delete_btn.clicked.connect(self.delete_shipment)
        self.shipment_calc_btn.clicked.connect(self.recalculate_shipment_cost)

        self.shipment_edit_btn.setEnabled(False)
        self.shipment_delete_btn.setEnabled(False)

        btn_layout.addWidget(self.shipment_add_btn)
        btn_layout.addWidget(self.shipment_edit_btn)
        btn_layout.addWidget(self.shipment_delete_btn)
        btn_layout.addWidget(self.shipment_calc_btn)
        btn_layout.addStretch()

        layout.addWidget(self.shipment_table)
        layout.addLayout(btn_layout)

        self.tabs.addTab(self.shipment_tab, "🚚 Перевозки")

    def load_shipments(self):
        """Загрузить перевозки в таблицу"""
        self.shipment_table.setRowCount(0)
        shipments = get_all_shipments(self.session)

        for row, shipment in enumerate(shipments):
            self.shipment_table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(shipment["id"]))
            id_item.setData(Qt.UserRole, shipment["id"])
            self.shipment_table.setItem(row, 0, id_item)

            # Дата
            date_str = shipment["shipment_date"]
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            self.shipment_table.setItem(row, 1, QTableWidgetItem(date_str))

            # Вес
            self.shipment_table.setItem(row, 2, QTableWidgetItem(str(shipment["cargo_weight"])))

            # Статус (с цветовым кодированием) (сдвигаем на 1 колонку влево)
            status_item = QTableWidgetItem(shipment["status"])
            if shipment["status"] == "pending":
                status_item.setForeground(QColor("orange"))
            elif shipment["status"] == "in_transit":
                status_item.setForeground(QColor("blue"))
            elif shipment["status"] == "delivered":
                status_item.setForeground(QColor("green"))
            elif shipment["status"] == "cancelled":
                status_item.setForeground(QColor("red"))
            self.shipment_table.setItem(row, 3, status_item)

            # Автомобиль (сдвигаем на 1 колонку влево)
            car_info = shipment.get("car_info", {})
            car_text = f"{car_info.get('brand', '')} ({car_info.get('license_plate', '')})"
            self.shipment_table.setItem(row, 4, QTableWidgetItem(car_text))

            # Водитель (сдвигаем на 1 колонку влево)
            driver_info = shipment.get("driver_info", {})
            driver_text = driver_info.get('full_name', '')
            self.shipment_table.setItem(row, 5, QTableWidgetItem(driver_text))

            # Маршрут (сдвигаем на 1 колонку влево)
            route_info = shipment.get("route_info", {})
            route_text = f"{route_info.get('origin', '')} → {route_info.get('destination', '')}"
            self.shipment_table.setItem(row, 6, QTableWidgetItem(route_text))

            # Стоимость (сдвигаем на 1 колонку влево)
            cost = shipment.get("total_cost", 0)
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            if cost > 0:
                cost_item.setForeground(QColor("darkGreen"))
                cost_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.shipment_table.setItem(row, 7, cost_item)

    def add_shipment(self):
        """Добавить новую перевозку"""
        available_cars = get_available_cars_with_drivers(self.session)
        available_drivers = get_all_drivers(self.session)
        available_routes = get_all_routes(self.session)

        # Получаем активные тарифы
        shipment_date = datetime.datetime.now()
        available_tariffs = get_active_tariffs(self.session, shipment_date)

        if not available_cars:
            QMessageBox.warning(self, "Ошибка", "Нет доступных автомобилей с водителями")
            return

        if not available_tariffs:
            QMessageBox.warning(self, "Ошибка", "Нет активных тарифов")
            return

        dialog = ShipmentDialog(
            self,
            available_cars=available_cars,
            available_drivers=available_drivers,
            available_routes=available_routes,
            available_tariffs=available_tariffs,
        )

        if dialog.exec():
            data = dialog.get_data()

            # Создаем перевозку
            create_shipment(self.session, **data)
            self.load_shipments()
            self.status_bar.showMessage("Перевозка создана", 3000)

    def edit_shipment(self):
        """Редактировать перевозку"""
        selected = self.shipment_table.selectedItems()
        if not selected:
            return

        row = self.shipment_table.currentRow()
        shipment_id = int(self.shipment_table.item(row, 0).text())

        # Получаем данные перевозки
        shipments = get_all_shipments(self.session)
        shipment = next((s for s in shipments if s["id"] == shipment_id), None)

        if not shipment:
            QMessageBox.warning(self, "Ошибка", "Перевозка не найдена")
            return

        try:
            # Получаем данные для формы
            available_cars = get_available_cars_with_drivers(self.session)
            available_drivers = get_all_drivers(self.session)
            available_routes = get_all_routes(self.session)

            # Получаем активные тарифы на дату перевозки
            shipment_date = datetime.datetime.fromisoformat(shipment["shipment_date"])
            available_tariffs = get_active_tariffs(self.session, shipment_date)

            dialog = ShipmentDialog(
                self,
                shipment=shipment,
                available_cars=available_cars,
                available_drivers=available_drivers,
                available_routes=available_routes,
                available_tariffs=available_tariffs
            )

            if dialog.exec():
                data = dialog.get_data()

                # Обновляем перевозку
                update_shipment(self.session, shipment_id, **data)
                self.load_shipments()
                self.status_bar.showMessage("Перевозка обновлена", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить перевозку: {str(e)}")

    def delete_shipment(self):
        """Удалить перевозку"""
        selected = self.shipment_table.selectedItems()
        if not selected:
            return

        row = self.shipment_table.currentRow()
        shipment_id = self.shipment_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить перевозку #{shipment_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if delete_shipment(self.session, shipment_id):
                self.load_shipments()
                self.status_bar.showMessage("Перевозка удалена", 3000)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить перевозку")

    def recalculate_shipment_cost(self):
        """Пересчитать стоимость выбранной перевозки"""
        selected = self.shipment_table.selectedItems()
        if not selected:
            return

        row = self.shipment_table.currentRow()
        shipment_id = str(self.shipment_table.item(row, 0))

        # Здесь можно добавить пересчет стоимости
        # Пока просто обновим данные
        self.load_shipments()
        self.status_bar.showMessage("Данные обновлены", 2000)

    def on_shipment_selected(self):
        """Обработчик выбора перевозки"""
        selected = self.shipment_table.selectedItems()
        has_selection = len(selected) > 0

        self.shipment_edit_btn.setEnabled(has_selection)
        self.shipment_delete_btn.setEnabled(has_selection)

    def create_menu(self):
        """Создание меню приложения"""
        menu_bar = self.menuBar()

        # Меню Файл
        file_menu = menu_bar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

        # Меню Данные
        data_menu = menu_bar.addMenu("Данные")

        refresh_action = QAction("Обновить все", self)
        refresh_action.triggered.connect(self.load_all_data)
        data_menu.addAction(refresh_action)

        # Меню Справка
        help_menu = menu_bar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Панель инструментов")
        self.addToolBar(toolbar)

        # Кнопки для быстрого добавления
        add_route_action = QAction("+ Маршрут", self)
        add_route_action.triggered.connect(self.open_create_dialog)
        toolbar.addAction(add_route_action)

        add_car_action = QAction("+ Машина", self)
        add_car_action.triggered.connect(self.open_create_car_dialog)
        toolbar.addAction(add_car_action)

        add_driver_action = QAction("+ Водитель", self)
        add_driver_action.triggered.connect(self.open_create_driver_dialog)
        toolbar.addAction(add_driver_action)

        toolbar.addSeparator()

        # Новая кнопка для управления назначениями
        assign_action = QAction("🚗 Назначения", self)
        assign_action.triggered.connect(self.open_assignment_dialog)
        toolbar.addAction(assign_action)

        add_tariff_action = QAction("💰 Тариф", self)
        add_tariff_action.triggered.connect(self.add_tariff)
        toolbar.addAction(add_tariff_action)

        # Кнопка обновления
        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.load_all_data)
        toolbar.addAction(refresh_action)

    def setup_route_tab(self):
        """Настройка вкладки с маршрутами"""
        self.route_tab = QWidget()
        layout = QVBoxLayout(self.route_tab)

        # Таблица маршрутов
        self.route_table = QTableWidget(0, 6)
        self.route_table.setHorizontalHeaderLabels([
            "ID", "Откуда", "Куда",
            "Расстояние (км)", "Время (ч)", "Тип дороги"
        ])
        self.route_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.route_table.setAlternatingRowColors(True)
        self.route_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.route_table.setSelectionMode(QTableWidget.SingleSelection)
        self.route_table.itemSelectionChanged.connect(self.on_route_selected)

        # Кнопки для маршрутов
        btn_layout = QHBoxLayout()

        self.route_create_btn = QPushButton("Добавить маршрут")
        self.route_edit_btn = QPushButton("Изменить")
        self.route_delete_btn = QPushButton("Удалить")

        self.route_create_btn.clicked.connect(self.open_create_dialog)
        self.route_edit_btn.clicked.connect(self.edit_route)
        self.route_delete_btn.clicked.connect(self.delete_route)

        self.route_edit_btn.setEnabled(False)
        self.route_delete_btn.setEnabled(False)

        btn_layout.addWidget(self.route_create_btn)
        btn_layout.addWidget(self.route_edit_btn)
        btn_layout.addWidget(self.route_delete_btn)
        btn_layout.addStretch()

        layout.addWidget(self.route_table)
        layout.addLayout(btn_layout)

        self.tabs.addTab(self.route_tab, "🚚 Маршруты")

    def setup_car_tab(self):
        """Настройка вкладки с машинами"""
        self.car_tab = QWidget()
        layout = QVBoxLayout(self.car_tab)

        # Таблица машин
        self.car_table = QTableWidget(0, 6)
        self.car_table.setHorizontalHeaderLabels([
            "ID", "Марка", "Госномер",
            "Грузоподъемность (т)", "Тип кузова", "Расход топлива (л/100км)"
        ])
        self.car_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.car_table.setAlternatingRowColors(True)
        self.car_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.car_table.setSelectionMode(QTableWidget.SingleSelection)
        self.car_table.itemSelectionChanged.connect(self.on_car_selected)

        # Кнопки для машин
        btn_layout = QHBoxLayout()

        self.car_create_btn = QPushButton("Добавить машину")
        self.car_edit_btn = QPushButton("Изменить")
        self.car_delete_btn = QPushButton("Удалить")

        self.car_create_btn.clicked.connect(self.open_create_car_dialog)
        self.car_edit_btn.clicked.connect(self.edit_car)
        self.car_delete_btn.clicked.connect(self.delete_car)

        self.car_edit_btn.setEnabled(False)
        self.car_delete_btn.setEnabled(False)

        btn_layout.addWidget(self.car_create_btn)
        btn_layout.addWidget(self.car_edit_btn)
        btn_layout.addWidget(self.car_delete_btn)
        btn_layout.addStretch()

        layout.addWidget(self.car_table)
        layout.addLayout(btn_layout)

        self.tabs.addTab(self.car_tab, "🚗 Автомобили")

    def setup_driver_tab(self):
        """Настройка вкладки с водителями"""
        self.driver_tab = QWidget()
        layout = QVBoxLayout(self.driver_tab)

        # Таблица водителей
        self.driver_table = QTableWidget(0, 6)
        self.driver_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Номер прав",
            "Категория", "Стаж (лет)", "Автомобиль"
        ])
        self.driver_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.driver_table.setAlternatingRowColors(True)
        self.driver_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.driver_table.setSelectionMode(QTableWidget.SingleSelection)
        self.driver_table.itemSelectionChanged.connect(self.on_driver_selected)

        # Кнопки для водителей
        btn_layout = QHBoxLayout()

        self.driver_create_btn = QPushButton("👤 Добавить водителя")
        self.driver_edit_btn = QPushButton("✏ Изменить")
        self.driver_delete_btn = QPushButton("🗑 Удалить")
        self.driver_assign_btn = QPushButton("🚗 Управление назначениями")

        self.driver_create_btn.clicked.connect(self.open_create_driver_dialog)
        self.driver_edit_btn.clicked.connect(self.edit_driver)
        self.driver_delete_btn.clicked.connect(self.delete_driver)
        self.driver_assign_btn.clicked.connect(self.open_assignment_dialog)

        self.driver_edit_btn.setEnabled(False)
        self.driver_delete_btn.setEnabled(False)

        btn_layout.addWidget(self.driver_create_btn)
        btn_layout.addWidget(self.driver_edit_btn)
        btn_layout.addWidget(self.driver_delete_btn)
        btn_layout.addWidget(self.driver_assign_btn)
        btn_layout.addStretch()

        layout.addWidget(self.driver_table)
        layout.addLayout(btn_layout)

        self.tabs.addTab(self.driver_tab, "👤 Водители")

    # ========== Методы для работы с данными ==========

    def load_all_data(self):
        """Загрузить все данные"""
        self.load_routes()
        self.load_cars()
        self.load_drivers()
        self.load_shipments()
        self.load_tariffs()
        self.status_bar.showMessage("Данные загружены", 2000)

    # ========== Методы для водителей ==========
    def load_drivers(self):
        """Загрузка водителей в таблицу"""
        self.driver_table.setRowCount(0)
        drivers = get_all_drivers_with_cars(self.session)

        for row, driver in enumerate(drivers):
            self.driver_table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(driver["id"]))
            id_item.setData(Qt.UserRole, driver["id"])
            self.driver_table.setItem(row, 0, id_item)

            # ФИО
            self.driver_table.setItem(row, 1, QTableWidgetItem(driver["full_name"]))

            # Номер прав
            self.driver_table.setItem(row, 2, QTableWidgetItem(driver["license_number"]))

            # Категория
            self.driver_table.setItem(row, 3, QTableWidgetItem(driver["license_category"]))

            # Стаж
            exp_item = QTableWidgetItem(str(driver["experience_years"]))
            exp_item.setData(Qt.UserRole, driver["experience_years"])
            self.driver_table.setItem(row, 4, exp_item)

            # Автомобиль (красивое отображение)
            car_info = driver["car_info"]["full_info"]
            car_item = QTableWidgetItem(car_info)
            car_item.setData(Qt.UserRole, driver["car_id"])

            # Добавляем иконку и стиль в зависимости от статуса
            if car_info == "Не назначен":
                car_item.setForeground(QColor(128, 128, 128))
                icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
                car_item.setIcon(icon)
            else:
                car_item.setForeground(QColor(0, 128, 0))
                icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
                car_item.setIcon(icon)

            self.driver_table.setItem(row, 5, car_item)

    def open_create_driver_dialog(self):
        """Открыть диалог создания водителя"""
        available_cars = get_all_cars_for_assignment(self.session)
        dialog = DriverDialog(self, available_cars=available_cars)

        if dialog.exec():
            data = dialog.get_data()

            required_fields = ["full_name", "license_number"]
            for field in required_fields:
                if not data.get(field):
                    QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                    return

            # Дополнительная проверка стажа перед созданием
            if 'experience_years' in data and data['experience_years'] > 40:
                QMessageBox.warning(
                    self,
                    "Ошибка в данных",
                    f"Стаж водителя не может превышать 40 лет.\n"
                    f"Указано: {data['experience_years']} лет.\n\n"
                    f"Проверьте правильность введенных данных."
                )
                return

            try:
                create_driver(self.session, **data)
                self.load_drivers()
                self.status_bar.showMessage("Водитель добавлен успешно", 3000)
            except ValueError as e:
                if "40 лет" in str(e):
                    QMessageBox.warning(self, "Ошибка в стаже", str(e))
                else:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить водителя: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить водителя: {str(e)}")

    def edit_driver(self):
        """Редактирование выбранного водителя"""
        selected_rows = self.driver_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        id_item = self.driver_table.item(row, 0)
        if not id_item:
            return

        driver_id = id_item.data(Qt.UserRole)

        # Получаем полные данные водителя
        drivers = get_all_drivers_with_cars(self.session)
        driver = next((d for d in drivers if d["id"] == driver_id), None)

        if not driver:
            QMessageBox.warning(self, "Ошибка", "Водитель не найден")
            return

        # Получаем доступные автомобили
        available_cars = get_all_cars_for_assignment(self.session)

        dialog = DriverDialog(self, driver, available_cars)

        if dialog.exec():
            data = dialog.get_data()

            required_fields = ["full_name", "license_number"]
            for field in required_fields:
                if not data.get(field):
                    QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                    return

            # Дополнительная проверка стажа
            if 'experience_years' in data and data['experience_years'] > 40:
                QMessageBox.warning(
                    self,
                    "Ошибка в данных",
                    f"Стаж водителя не может превышать 40 лет.\n"
                    f"Указано: {data['experience_years']} лет."
                )
                return

            try:
                success = update_driver(self.session, driver_id, **data)
                if success:
                    self.load_drivers()
                    self.status_bar.showMessage("Данные водителя обновлены успешно", 3000)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные водителя")
            except ValueError as e:
                if "40 лет" in str(e):
                    QMessageBox.warning(self, "Ошибка в стаже", str(e))
                else:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось обновить данные водителя: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {str(e)}")


    def open_assignment_dialog(self):
        """Открыть диалог управления назначениями"""
        drivers = get_all_drivers_with_cars(self.session)
        cars = get_all_cars_for_assignment(self.session)

        dialog = AssignmentDialog(self, drivers, cars)
        dialog.exec()

    def assign_driver_to_car_requested(self, driver_id: int, car_id: Optional[int]):
        """Обработка запроса на назначение водителя на автомобиль"""
        success = assign_driver_to_car(self.session, driver_id, car_id)

        if success:
            self.load_drivers()
            self.load_cars()

            if car_id:
                self.status_bar.showMessage("Водитель успешно назначен на автомобиль", 3000)
            else:
                self.status_bar.showMessage("Водитель откреплен от автомобиля", 3000)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить назначение")

    def swap_drivers_requested(self, driver1_id: int, driver2_id: int):
        """Обработка запроса на обмен автомобилями"""
        success = swap_driver_car(self.session, driver1_id, driver2_id)

        if success:
            self.load_drivers()
            self.load_cars()
            self.status_bar.showMessage("Автомобили успешно обменены", 3000)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить обмен")

    def load_cars(self):
        """Загрузка машин в таблицу"""
        self.car_table.setRowCount(0)
        cars = get_all_cars_for_assignment(self.session)

        for row, car in enumerate(cars):
            self.car_table.insertRow(row)

            id_item = QTableWidgetItem(str(car["id"]))
            id_item.setData(Qt.UserRole, car["id"])
            self.car_table.setItem(row, 0, id_item)

            # Марка
            self.car_table.setItem(row, 1, QTableWidgetItem(car["brand"]))

            # Госномер
            self.car_table.setItem(row, 2, QTableWidgetItem(car["license_plate"]))

            # Грузоподъемность
            capacity_item = QTableWidgetItem(str(car["load_capacity"]))
            capacity_item.setData(Qt.UserRole, car["load_capacity"])
            self.car_table.setItem(row, 3, capacity_item)

            # Тип кузова
            self.car_table.setItem(row, 4, QTableWidgetItem(car["body_type"]))

            # Расход топлива и информация о водителе
            fuel_text = f"{car['fuel_consumption']} л/100км"
            if car['has_driver']:
                fuel_text += f"\n👤 {car['driver_info']}"

            fuel_item = QTableWidgetItem(fuel_text)
            fuel_item.setData(Qt.UserRole, car["fuel_consumption"])

            if car['has_driver']:
                fuel_item.setForeground(Qt.darkGreen)
                fuel_item.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
            else:
                fuel_item.setForeground(Qt.darkGray)
                fuel_item.setIcon(self.style().standardIcon(self.style().SP_MessageBoxInformation))

            self.car_table.setItem(row, 5, fuel_item)

    def on_driver_selected(self):
        """Обработчик выбора строки в таблице водителей"""
        selected_rows = self.driver_table.selectionModel().selectedRows()
        enabled = len(selected_rows) > 0

        self.driver_edit_btn.setEnabled(enabled)
        self.driver_delete_btn.setEnabled(enabled)

    def delete_driver(self):
        """Удаление выбранного водителя"""
        selected_rows = self.driver_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        item = self.driver_table.item(row, 0)
        if not item:
            return

        driver_id = item.data(Qt.UserRole)

        try:
            # Проверяем, есть ли у водителя активные перевозки
            from Services.Transportation.model import Shipment
            from sqlalchemy import and_

            # Проверяем активные перевозки (не доставленные и не отмененные)
            active_shipments = self.session.query(Shipment).filter(
                and_(
                    Shipment.driver_id == driver_id,
                    Shipment.status.in_(["pending", "in_transit"])
                )
            ).all()

            if active_shipments:
                # Формируем информацию о перевозках
                shipment_info = ""
                for shipment in active_shipments[:3]:  # Показываем первые 3 перевозки
                    shipment_date = shipment.shipment_date.strftime("%d.%m.%Y") if isinstance(shipment.shipment_date,
                                                                                              datetime.datetime) else shipment.shipment_date
                    shipment_info += f"• ID {shipment.id} от {shipment_date} (статус: {shipment.status})\n"

                if len(active_shipments) > 3:
                    shipment_info += f"• ... и еще {len(active_shipments) - 3} перевозок\n"

                QMessageBox.warning(
                    self,
                    "Водитель в пути",
                    f"Невозможно удалить водителя, так как он находится в пути!\n\n"
                    f"Активных перевозок: {len(active_shipments)}\n\n"
                    f"Перевозки:\n{shipment_info}\n"
                    "Дождитесь завершения перевозок или отмените их."
                )
                return

        except Exception as e:
            print(f"Ошибка при проверке перевозок: {e}")

        # Если нет активных перевозок, спрашиваем подтверждение
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить водителя?\n"
            "Это действие нельзя отменить.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = delete_driver(self.session, driver_id)
                if success:
                    self.load_drivers()
                    self.status_bar.showMessage("Водитель удален успешно", 3000)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить водителя")
            except Exception as e:
                error_msg = str(e)
                # Проверяем, связана ли ошибка с триггером
                if "активны" in error_msg.lower() or "перевозк" in error_msg.lower() or "active" in error_msg.lower():
                    QMessageBox.warning(
                        self,
                        "Ошибка удаления",
                        f"Невозможно удалить водителя: {error_msg}"
                    )
                else:
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {error_msg}")
    # ========== Методы для маршрутов ==========

    def load_routes(self):
        """Загрузка маршрутов в таблицу"""
        self.route_table.setRowCount(0)
        routes = get_all_routes(self.session)

        for row, route in enumerate(routes):
            self.route_table.insertRow(row)

            id_item = QTableWidgetItem(str(route["id"]))
            id_item.setData(Qt.UserRole, route["id"])
            self.route_table.setItem(row, 0, id_item)

            self.route_table.setItem(row, 1, QTableWidgetItem(route["origin"]))
            self.route_table.setItem(row, 2, QTableWidgetItem(route["destination"]))

            distance_item = QTableWidgetItem(str(route["distance_km"]))
            distance_item.setData(Qt.UserRole, route["distance_km"])
            self.route_table.setItem(row, 3, distance_item)

            time_item = QTableWidgetItem(str(route["avg_time_hours"]))
            time_item.setData(Qt.UserRole, route["avg_time_hours"])
            self.route_table.setItem(row, 4, time_item)

            self.route_table.setItem(row, 5, QTableWidgetItem(route["road_type"]))

    def open_create_dialog(self):
        """Открыть диалог создания маршрута"""
        dialog = CreateRouteDialog(self)

        if dialog.exec():
            data = dialog.get_data()

            if not data["origin"] or not data["destination"]:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return

            create_route(self.session, **data)
            self.load_routes()
            self.status_bar.showMessage("Маршрут добавлен успешно", 3000)

    def on_route_selected(self):
        """Обработчик выбора строки в таблице маршрутов"""
        selected_rows = self.route_table.selectionModel().selectedRows()
        enabled = len(selected_rows) > 0

        self.route_edit_btn.setEnabled(enabled)
        self.route_delete_btn.setEnabled(enabled)

    def delete_route(self):
        """Удаление выбранного маршрута"""
        selected_rows = self.route_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        item = self.route_table.item(row, 0)
        if not item:
            return

        route_id = item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить маршрут?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            delete_route(self.session, route_id)
            self.load_routes()
            self.status_bar.showMessage("Маршрут удален успешно", 3000)

    def edit_route(self):
        """Редактирование выбранного маршрута"""
        selected_rows = self.route_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        id_item = self.route_table.item(row, 0)
        if not id_item:
            return

        route_id = id_item.data(Qt.UserRole)

        route = {
            "id": route_id,
            "origin": self.route_table.item(row, 1).text() if self.route_table.item(row, 1) else "",
            "destination": self.route_table.item(row, 2).text() if self.route_table.item(row, 2) else "",
            "distance_km": self.route_table.item(row, 3).data(Qt.UserRole) if self.route_table.item(row, 3) else 0,
            "avg_time_hours": self.route_table.item(row, 4).data(Qt.UserRole) if self.route_table.item(row, 4) else 0,
            "road_type": self.route_table.item(row, 5).text() if self.route_table.item(row, 5) else "",
        }

        dialog = CreateRouteDialogEditDelete(self, route)

        if dialog.exec():
            data = dialog.get_data()
            if not data["origin"] or not data["destination"]:
                QMessageBox.warning(self, "Ошибка", "Заполните поля 'Откуда' и 'Куда'")
                return

            update_route(self.session, route_id, **data)
            self.load_routes()
            self.status_bar.showMessage("Маршрут обновлен успешно", 3000)

    # ========== Методы для машин ==========

    def load_cars(self):
        """Загрузка машин в таблицу"""
        self.car_table.setRowCount(0)
        cars = get_all_cars(self.session)

        for row, car in enumerate(cars):
            self.car_table.insertRow(row)

            id_item = QTableWidgetItem(str(car["id"]))
            id_item.setData(Qt.UserRole, car["id"])
            self.car_table.setItem(row, 0, id_item)

            self.car_table.setItem(row, 1, QTableWidgetItem(car["brand"]))
            self.car_table.setItem(row, 2, QTableWidgetItem(car["license_plate"]))

            capacity_item = QTableWidgetItem(str(car["load_capacity"]))
            capacity_item.setData(Qt.UserRole, car["load_capacity"])
            self.car_table.setItem(row, 3, capacity_item)

            self.car_table.setItem(row, 4, QTableWidgetItem(car["body_type"]))

            fuel_item = QTableWidgetItem(str(car["fuel_consumption"]))
            fuel_item.setData(Qt.UserRole, car["fuel_consumption"])
            self.car_table.setItem(row, 5, fuel_item)

    def open_create_car_dialog(self):
        """Открыть диалог создания машины"""
        dialog = CarDialog(self)

        if dialog.exec():
            data = dialog.get_data()

            required_fields = ["brand", "license_plate", "body_type"]
            for field in required_fields:
                if not data.get(field):
                    QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                    return

            create_car(self.session, **data)
            self.load_cars()
            self.status_bar.showMessage("Машина добавлена успешно", 3000)

    def on_car_selected(self):
        """Обработчик выбора строки в таблице машин"""
        selected_rows = self.car_table.selectionModel().selectedRows()
        enabled = len(selected_rows) > 0

        self.car_edit_btn.setEnabled(enabled)
        self.car_delete_btn.setEnabled(enabled)

    def delete_car(self):
        """Удаление выбранной машины"""
        selected_rows = self.car_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        item = self.car_table.item(row, 0)
        if not item:
            return

        car_id = item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить машину?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = delete_car(self.session, car_id)
            if success:
                self.load_cars()
                self.status_bar.showMessage("Машина удалена успешно", 3000)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить машину")

    def edit_car(self):
        """Редактирование выбранной машины"""
        selected_rows = self.car_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()

        id_item = self.car_table.item(row, 0)
        if not id_item:
            return

        car_id = id_item.data(Qt.UserRole)

        car = {
            "id": car_id,
            "brand": self.car_table.item(row, 1).text() if self.car_table.item(row, 1) else "",
            "license_plate": self.car_table.item(row, 2).text() if self.car_table.item(row, 2) else "",
            "load_capacity": self.car_table.item(row, 3).data(Qt.UserRole) if self.car_table.item(row, 3) else 0,
            "body_type": self.car_table.item(row, 4).text() if self.car_table.item(row, 4) else "",
            "fuel_consumption": self.car_table.item(row, 5).data(Qt.UserRole) if self.car_table.item(row, 5) else 0,
        }

        dialog = CarDialog(self, car)

        if dialog.exec():
            data = dialog.get_data()

            required_fields = ["brand", "license_plate", "body_type"]
            for field in required_fields:
                if not data.get(field):
                    QMessageBox.warning(self, "Ошибка", f"Заполните поле: {field}")
                    return

            success = update_car(self.session, car_id, **data)
            if success:
                self.load_cars()
                self.status_bar.showMessage("Данные машины обновлены успешно", 3000)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить данные машины")

    def show_about(self):
        """Показать информацию о программе"""
        QMessageBox.information(
            self,
            "О программе",
            "Система управления перевозками\n\n"
            "Версия 2.0\n\n"
            "Управление:\n"
            "• Маршрутами\n"
            "• Автомобилями\n"
            "• Водителями\n"
            "• Перевозками\n"
            "• Тарифами\n\n"
            "© 2024"
        )