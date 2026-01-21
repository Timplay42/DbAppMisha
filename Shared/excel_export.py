# Utils/excel_export.py
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Утилита для экспорта данных в Excel"""

    @staticmethod
    def export_to_excel(data: List[Dict], filename: str, sheet_name: str = "Данные") -> str:
        """
        Экспорт данных в Excel файл

        Args:
            data: Список словарей с данными
            filename: Имя файла (без расширения)
            sheet_name: Название листа

        Returns:
            Путь к сохраненному файлу
        """
        try:
            # Создаем DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                raise ValueError("Нет данных для экспорта")

            # Создаем имя файла с timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_with_ts = f"{filename}_{timestamp}.xlsx"

            # Путь для сохранения (папка загрузок пользователя)
            downloads_path = Path.home() / "Downloads"
            downloads_path.mkdir(exist_ok=True)

            file_path = downloads_path / filename_with_ts

            # Сохраняем в Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Автонастройка ширины столбцов
                worksheet = writer.sheets[sheet_name]
                for column in df:
                    column_width = max(df[column].astype(str).map(len).max(), len(column)) + 2
                    col_idx = df.columns.get_loc(column)
                    worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_width, 50)

            logger.info(f"Файл успешно сохранен: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Ошибка при экспорте в Excel: {e}")
            raise

    @staticmethod
    def show_success_message(filepath: str, parent=None):
        """Показать сообщение об успешном сохранении"""
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QDir

        # Получаем только имя файла для отображения
        filename = os.path.basename(filepath)

        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Экспорт завершен")
        msg.setText(f"Данные успешно экспортированы в файл:\n{filename}")
        msg.setInformativeText(f"Файл сохранен в папке:\n{QDir.toNativeSeparators(os.path.dirname(filepath))}")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()