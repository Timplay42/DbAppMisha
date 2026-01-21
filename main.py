# main.py
import sys
from PySide6.QtWidgets import QApplication
from Gui.route_main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
