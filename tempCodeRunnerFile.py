import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QLabel, QMessageBox)
from PyQt5.QtCore import Qt

class BookInventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku - Week 10 Assignment")
        self.setGeometry(100, 100, 800, 600)

        # Initialize database
        self.conn = sqlite3.connect('books.db')
        self.create_table()

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Student Info
        self.student_label = QLabel("Nama: Maftuh Ahnan Al-Kautsar | NIM: F1D022135")
        self.layout.addWidget(self.student_label)

        # Input form
        self.form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Pengarang")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Tahun Terbit")
        
        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_book)
        
        self.form_layout.addWidget(self.title_input)
        self.form_layout.addWidget(self.author_input)
        self.form_layout.addWidget(self.year_input)
        self.form_layout.addWidget(self.save_button)
        self.layout.addLayout(self.form_layout)

        # Search
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari Judul")
        self.search_input.textChanged.connect(self.search_books)
        self.search_layout.addWidget(self.search_input)
        self.layout.addLayout(self.search_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Judul', 'Pengarang', 'Tahun'])
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 200)
        self.table.cellDoubleClicked.connect(self.edit_book)
        self.layout.addWidget(self.table)

        # Delete and Export buttons
        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Hapus")
        self.delete_button.clicked.connect(self.delete_book)
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.export_button)
        self.layout.addLayout(self.button_layout)

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
            QMessageBox.warning(self, "Input Error", "Title and Author are required!")
            return

        try:
            year = int(year) if year else 0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Year must be a number!")
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
        cursor = self.conn.cursor()
        if search_text:
            cursor.execute('SELECT * FROM books WHERE title LIKE ?', (f'%{search_text}%',))
        else:
            cursor.execute('SELECT * FROM books')
        
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        
        for row_idx, row_data in enumerate(rows):
            for col_idx, data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    def search_books(self):
        search_text = self.search_input.text().strip()
        self.load_data(search_text)

    def edit_book(self, row, column):
        book_id = int(self.table.item(row, 0).text())
        cursor = self.conn.cursor()
        cursor.execute('SELECT title, author, year FROM books WHERE id = ?', (book_id,))
        book = cursor.fetchone()

        self.title_input.setText(book[0])
        self.author_input.setText(book[1])
        self.year_input.setText(str(book[2]) if book[2] else "")

        # Change save button to update
        self.save_button.setText("Update")
        self.save_button.disconnect()
        self.save_button.clicked.connect(lambda: self.update_book(book_id))

    def update_book(self, book_id):
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        year = self.year_input.text().strip()

        if not title or not author:
            QMessageBox.warning(self, "Input Error", "Title and Author are required!")
            return

        try:
            year = int(year) if year else 0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Year must be a number!")
            return

        cursor = self.conn.cursor()
        cursor.execute('UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?',
                      (title, author, year, book_id))
        self.conn.commit()

        self.title_input.clear()
        self.author_input.clear()
        self.year_input.clear()
        self.save_button.setText("Save")
        self.save_button.disconnect()
        self.save_button.clicked.connect(self.save_book)
        self.load_data()

    def delete_book(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a book to delete!")
            return

        book_id = int(self.table.item(selected, 0).text())
        reply = QMessageBox.question(self, 'Confirm Delete',
                                  'Are you sure you want to delete this book?',
                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            self.conn.commit()
            self.load_data()

    def export_to_csv(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM books')
        rows = cursor.fetchall()

        with open('books_export.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Judul', 'Pengarang', 'Tahun'])
            writer.writerows(rows)

        QMessageBox.information(self, "Export Success", "Data exported to books_export.csv")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BookInventoryApp()
    window.show()
    sys.exit(app.exec_())