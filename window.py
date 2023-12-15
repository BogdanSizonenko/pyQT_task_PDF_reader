import sys

from fitz import open, Matrix

from PyQt5.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFileDialog, QApplication 
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPen, QPainter, QPixmap, QImage    


class MyLabel(QLabel):
    # Пользовательский виджет QLabel с возможность рисовать на на самом виджете
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    flag = False
    
    def mousePressEvent(self,event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        
    def mouseReleaseEvent(self,event):
        self.flag = False
        
    def mouseMoveEvent(self,event):
        if self.flag:
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()
            
    def paintEvent(self, event):
        super().paintEvent(event)
        rect =QRect(self.x0, self.y0, abs(self.x1-self.x0), abs(self.y1-self.y0))
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red,2,Qt.SolidLine))
        painter.drawRect(rect)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(450, 50, 720, 900)
        # Основной QWidget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        # Разбиваем кнопки и отображение самого pdf файла вертикальным layout
        self.layout = QVBoxLayout()
        main_widget.setLayout(self.layout)
        # Горизонтальный layout для кнопок    
        self.sublayout = QHBoxLayout()
        self.layout.addLayout(self.sublayout)
        # Инициализация кнопок, сигналы для них, а также добавление в горизонтальный виджет
        # Кнопка "Загрузка" 
        self.dwn_button = QPushButton('Загрузка')
        self.dwn_button.clicked.connect(self.open_file_dialog)
        self.sublayout.addWidget(self.dwn_button)
        # Кнопка "<" - переход к предыдущей странице    
        self.prev_button = QPushButton('<')
        self.prev_button.clicked.connect(self.prev_page)
        self.sublayout.addWidget(self.prev_button)
        # Кнопка ">" - переход к следующей странице
        self.next_button = QPushButton('>')
        self.next_button.clicked.connect(self.next_page)
        self.sublayout.addWidget(self.next_button)
        # Добавляем стэк для страниц в вертикальный layout       
        self.stackedWidget = QStackedWidget()
        self.layout.addWidget(self.stackedWidget)
            
    # Отображение страниц файла через MyLabel(пользовательский) виджет      
    def pdf_pages_widget(self):
        for val in self.pages.values():
            self.label = MyLabel(self)
            self.label.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap()
            pixmap.convertFromImage(val)
            self.label.setPixmap(QPixmap(pixmap))
            self.label.setCursor(Qt.CrossCursor)
            self.label.resize(pixmap.width(), pixmap.height())
            self.stackedWidget.addWidget(self.label)
        self.current_page = 0
    
    # Слот на преключение на следущую страницу   
    def next_page(self):
        if self.current_page != len(self.pages) - 1:
            self.current_page += 1
            self.next_button = self.sender()
            self.stackedWidget.setCurrentIndex(self.current_page)

    # Слот на преключение на ппредыдущую страницу
    def prev_page(self):
        if self.current_page  != 0:
            self.current_page -= 1
            self.prev_button = self.sender()
            self.stackedWidget.setCurrentIndex(self.current_page)
    
    # Окрывает проводник при запуске программы         
    def first_open(self):
        self.path_file = QFileDialog.getOpenFileName(filter="file (*.pdf)")[0]
        self.pdf_to_img()
        self.pdf_pages_widget()
       
    #Открывает проводник, для загрузки нового файла
    def open_file_dialog(self):
        self.path_file = QFileDialog.getOpenFileName(filter="file (*.pdf)")[0]
        self.update_label() 
        self.pdf_to_img()
        self.pdf_pages_widget()
    
    # Обновление виджетов при загрузке нового файла
    def update_label(self):
        self.layout.removeWidget(self.stackedWidget)
        self.stackedWidget.deleteLater()
        self.stackedWidget = QStackedWidget()
        self.layout.addWidget(self.stackedWidget)
        self.label.repaint()
               
    # Преобразование pdf в словарь картинок - {"номер страницы(с 0)": "страница pdf преобразованная в картинку"}        
    def pdf_to_img(self):
        if self.path_file == '':
            self.open_file_dialog()
        pdf_doc = open(self.path_file)
        self.pages= {}
        for page_num, pg in enumerate(pdf_doc.pages()):
            trans_a = 110
            trans_b = 110
            trans = Matrix(trans_a / 100, trans_b / 100).prerotate(0)
            pix = pdf_doc[page_num].get_pixmap(matrix=trans)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            self.pages[page_num] = pageImage

       
if __name__ == '__main__': 
            
    app = QApplication([])
    
    window = MyWindow()
    
    window.first_open()
    
    window.show()

    sys.exit(app.exec_())