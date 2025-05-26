import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QMessageBox, QFileDialog, QHeaderView)
from PyQt5.QtCore import Qt

class BookInventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(100, 100, 600, 400)

        self.conn = sqlite3.connect('books.db')
        self.create_table()

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.student_label = QLabel("Nama: Maftuh Ahnan Al-Kautsar | NIM: F1D022135")
        self.student_label.setAlignment(Qt.AlignCenter)
        self.student_label.setStyleSheet("margin-bottom: 10px;")
        self.layout.addWidget(self.student_label)

        self.form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul")
        self.title_input.setStyleSheet("padding: 5px;")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Pengarang")
        self.author_input.setStyleSheet("padding: 5px;")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Tahun")
        self.year_input.setStyleSheet("padding: 5px;")
        
        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_book)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; border-radius: 3px;")
        
        self.form_layout.addWidget(QLabel("Judul:"))
        self.form_layout.addWidget(self.title_input)
        self.form_layout.addWidget(QLabel("Pengarang:"))
        self.form_layout.addWidget(self.author_input)
        self.form_layout.addWidget(QLabel("Tahun:"))
        self.form_layout.addWidget(self.year_input)
        self.form_layout.addWidget(self.save_button)
        self.layout.addLayout(self.form_layout)

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari Judul")
        self.search_input.setStyleSheet("padding: 5px; width: 200px;")
        self.search_input.textChanged.connect(self.search_books)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addStretch()
        self.layout.addLayout(self.search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Judul', 'Pengarang', 'Tahun'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(3, 60)
        self.table.setStyleSheet("QTableWidget { border: 1px solid #ccc; } "
                               "QHeaderView::section { background-color: #f0f0f0; border: 1px solid #ccc; padding: 4px; } "
                               "QTableWidget::item { padding: 4px; }")
        self.table.setEditTriggers(QTableWidget.DoubleClicked)
        self.table.itemChanged.connect(self.on_item_changed)
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Hapus Data")
        self.delete_button.clicked.connect(self.delete_book)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px; border-radius: 3px;")
        self.export_button = QPushButton("Ekspor")
        self.export_button.clicked.connect(self.export_to_csv)
        self.export_button.setStyleSheet("background-color: #ff9800; color: white; padding: 5px; border-radius: 3px;")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.export_button)
        self.layout.addLayout(self.button_layout)

        self.is_loading = False
        self.load_data()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER
            )
        ''')
        self.conn.commit()

    def save_book(self):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.text().strip()

        if not title or not author:
            QMessageBox.warning(self, "Input Error", "Judul dan Pengarang wajib diisi!")
            return

        try:
            year = int(year) if year else 0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Tahun harus berupa angka!")
            return

        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
                      (title, author, year))
        self.conn.commit()
        
        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()
        self.load_data()

    def load_data(self, search_text=""):
        self.is_loading = True  
        cursor = self.conn.cursor()
        if search_text:
            cursor.execute('SELECT * FROM books WHERE title LIKE ?', (f'%{search_text}%',))
        else:
            cursor.execute('SELECT * FROM books')
        
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        
        for row_idx, row_data in enumerate(rows):
            for col_idx, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignCenter)
                if col_idx == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        self.is_loading = False 

    def search_books(self):
        search_text = self.search_input.text().strip()
        self.load_data(search_text)

    def on_item_changed(self, item):
        if self.is_loading:
            return 

        row = item.row()
        book_id = int(self.table.item(row, 0).text())
        column = item.column()

        title = self.table.item(row, 1).text().strip()
        author = self.table.item(row, 2).text().strip()
        year = self.table.item(row, 3).text().strip()

        if column in [1, 2]: 
            if not title or not author:
                QMessageBox.warning(self, "Input Error", "Judul dan Pengarang wajib diisi!")
                self.load_data()  
                return
        if column == 3:  # Tahun
            try:
                year = int(year) if year else 0
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Tahun harus berupa angka!")
                self.load_data() 
                return

        cursor = self.conn.cursor()
        cursor.execute('UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?',
                      (title, author, year, book_id))
        self.conn.commit()
        self.load_data() 

    def delete_book(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Error", "Pilih data yang ingin dihapus!")
            return

        book_id = int(self.table.item(selected, 0).text())
        reply = QMessageBox.question(self, 'Konfirmasi Hapus',
                                   'Apakah Anda yakin ingin menghapus data ini?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            self.conn.commit()
            self.load_data()

    def export_to_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")
        if not file_path:
            return

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM books')
        rows = cursor.fetchall()

        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Judul', 'Pengarang', 'Tahun'])
                writer.writerows(rows)
            QMessageBox.information(self, "Ekspor Berhasil", f"Data berhasil diekspor ke {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Ekspor Gagal", f"Terjadi kesalahan saat mengekspor: {str(e)}")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookInventoryApp()
    window.show()
    sys.exit(app.exec_())