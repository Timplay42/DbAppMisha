# Gui/edit_delete_route_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QDoubleSpinBox
)


class CreateRouteDialogEditDelete(QDialog):
    def __init__(self, parent=None, route=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование маршрута" if route else "Создание маршрута")

        self.route = route  # ← если редактирование
        self.route_id = None

        self.origin = QLineEdit()
        self.destination = QLineEdit()

        self.distance = QDoubleSpinBox()
        self.distance.setMaximum(100000)
        self.distance.setSuffix(" км")
        self.distance.setMinimum(0)
        self.distance.setDecimals(2)

        self.avg_time = QDoubleSpinBox()
        self.avg_time.setMaximum(1000)
        self.avg_time.setSuffix(" ч")
        self.avg_time.setMinimum(0)
        self.avg_time.setDecimals(2)

        self.road_type = QLineEdit()

        btn_text = "Обновить" if route else "Создать"
        self.save_btn = QPushButton(btn_text)
        self.save_btn.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Пункт отправления *"))
        layout.addWidget(self.origin)

        layout.addWidget(QLabel("Пункт назначения *"))
        layout.addWidget(self.destination)

        layout.addWidget(QLabel("Расстояние (км)"))
        layout.addWidget(self.distance)

        layout.addWidget(QLabel("Среднее время (ч)"))
        layout.addWidget(self.avg_time)

        layout.addWidget(QLabel("Тип дороги"))
        layout.addWidget(self.road_type)

        layout.addWidget(self.save_btn)

        if route:
            self.route_id = route.get('id')
            self.origin.setText(route.get("origin", ""))
            self.destination.setText(route.get("destination", ""))
            self.distance.setValue(route.get("distance_km", 0))
            self.avg_time.setValue(route.get("avg_time_hours", 0))
            self.road_type.setText(route.get("road_type", ""))

    def get_data(self):
        """Получение данных из формы"""
        return {
            "origin": self.origin.text().strip(),
            "destination": self.destination.text().strip(),
            "distance_km": self.distance.value(),
            "avg_time_hours": self.avg_time.value(),
            "road_type": self.road_type.text().strip(),
        }