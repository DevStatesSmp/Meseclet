import os
import json
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebChannel import QWebChannel

class PyAPI(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    @pyqtSlot(result=QVariant)
    def get_recent_downloads(self):
        # Giả sử bạn lưu các file đã tải trong thư mục 'downloads'
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        files = os.listdir(download_dir)
        return sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)[:5]

    @pyqtSlot(str)
    def download_file(self, filename):
        # Thực hiện tải file
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        file_path = os.path.join(download_dir, filename)
        # Thêm logic tải file ở đây
        print(f"Đang tải xuống file: {file_path}")


class CustomTabBar(QTabBar):
    def __init__(self, parent=None, *args, **kwargs):
        super(CustomTabBar, self).__init__(parent, *args, **kwargs)
        self.setTabsClosable(True)
        self.setStyleSheet("""
            QTabBar {
                background: #f0f0f0;
                padding: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                padding: 10px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border: 1px solid #4a90e2;
            }
            QTabBar::tab:!selected {
                margin-left: 5px;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.homepage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "index.html")
        data_folder = 'data'
        self.history_file = os.path.join(data_folder, 'history.json')
        self.py_api = PyAPI(self)

        # Set window icon
        icon_path = 'meseclet.ico'
        if os.path.isfile(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Setup tabs
        self.tabs = QTabWidget()
        self.tab_bar_widget = CustomTabBar()
        self.tabs.setTabBar(self.tab_bar_widget)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Add browser tabs
        self.add_new_tab(QUrl.fromLocalFile(self.homepage_path), "Meseclet Homepage")

        # Navigation toolbar
        navbar = QToolBar("Navigation")
        navbar.setIconSize(QSize(24, 24))
        self.addToolBar(navbar)

        # Back button
        self.backbtn = QAction(QIcon('asset/button/back.png'), 'Go back', self)
        self.backbtn.setEnabled(False)
        self.backbtn.triggered.connect(lambda: self.current_browser().back() if self.current_browser() else None)
        navbar.addAction(self.backbtn)

        # Forward button
        self.forwardbtn = QAction(QIcon('asset/button/forward.png'), 'Go forward', self)
        self.forwardbtn.setEnabled(False)
        self.forwardbtn.triggered.connect(lambda: self.current_browser().forward() if self.current_browser() else None)
        navbar.addAction(self.forwardbtn)

        # Reload button
        self.reloadbtn = QAction(QIcon('asset/button/reload.png'), 'Reload', self)
        self.reloadbtn.triggered.connect(self.reload_page)
        navbar.addAction(self.reloadbtn)

        # Home button
        self.homebtn = QAction(QIcon('asset/button/home.png'), 'Home', self)
        self.homebtn.triggered.connect(self.navigate_home)
        navbar.addAction(self.homebtn)

        # URL bar
        self.UrlBar = QLineEdit()
        self.UrlBar.returnPressed.connect(self.handle_search)
        self.UrlBar.setPlaceholderText('Search or enter URL')
        self.UrlBar.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                height: 30px;
                border: 2px solid #dcdcdc;
                border-radius: 15px;
                font-size: 16px;
                background-color: #ffffff;
                width: 1000px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        navbar.addWidget(self.UrlBar)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Signals for navigation
        self.tabs.currentChanged.connect(self.update_nav_buttons)
        self.update_nav_buttons()  # Update button states on startup
        
        #download
        self.downloadbtn = QPushButton(QIcon('asset/button/download.png'), '', self)
        self.downloadbtn.setFixedSize(32, 32)
        self.downloadbtn.setStyleSheet("border: none;")
        self.downloadbtn.clicked.connect(self.open_download)
        navbar.addWidget(self.downloadbtn)

        # New tab
        self.new_tab_button = QPushButton(QIcon('asset/button/add_box.png'), '', self)
        self.new_tab_button.setFixedSize(32, 32)
        self.new_tab_button.setStyleSheet("border: none;")
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab())
        navbar.addWidget(self.new_tab_button)
        
        #menu
        self.menu_button = QPushButton(QIcon('asset/button/menu.png'), '', self)
        self.menu_button.setFixedSize(32, 32)
        self.menu_button.setStyleSheet("border: none;")
        self.menu_button.clicked.connect(self.open_menu)
        navbar.addWidget(self.menu_button)

    def open_menu(self):
        menu = QMenu(self)
        menu.addAction("Information", self.open_settings)
        menu.addAction("History", self.open_history)
        menu.exec_(QCursor.pos())

    def open_settings(self):
        settings_page = QWebEngineView()
        settings_page.setUrl(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "settings.html")))

        self.add_new_tab(settings_page.url(), "Settings")
        self.tabs.setCurrentWidget(settings_page)

    def open_history(self):
        history_page = QWebEngineView()
        history_page.setUrl(QUrl.fromLocalFile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "history.html")))
        self.add_new_tab(history_page.url(), "History") 
        self.tabs.setCurrentWidget(history_page)

    def open_download(self):
        download_page = QWebEngineView()
        
        # Tạo một QWebChannel và kết nối nó với trang web
        channel = QWebChannel()
        channel.registerObject("pyApi", self.py_api)
        
        # Tạo một QWebEnginePage mới và set channel cho nó
        page = QWebEnginePage()
        page.setWebChannel(channel)
        download_page.setPage(page)
        
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples", "download_page.html")
        download_page.setUrl(QUrl.fromLocalFile(html_path))
        
        self.add_new_tab(download_page.url(), "Download")
        self.tabs.setCurrentWidget(download_page)

    def navigate_home(self):
        if self.tabs.count() > 0:
            current_browser = self.current_browser()
            if current_browser:
                current_browser.setUrl(QUrl.fromLocalFile(self.homepage_path))
                self.save_history(self.homepage_path)
        else:
            self.add_new_tab(QUrl.fromLocalFile(self.homepage_path), "Meseclet Homepage")

    def handle_search(self):
        url = self.UrlBar.text().strip()
        if url:
            if not (url.startswith('http://') or url.startswith('https://')):
                if '.' in url:
                    url = 'http://' + url
                else:
                    url = f'https://www.google.com/search?q={url}'
            self.current_browser().setUrl(QUrl(url))
            self.save_history(url)

    def reload_page(self):
        current_browser = self.current_browser()
        if current_browser:
            current_url = current_browser.url().toString()
            self.save_history(current_url)  # Lưu vào lịch sử trước khi reload
            current_browser.reload()

    def add_new_tab(self, url=None, title="New Tab"):
        if url is None:
            url = QUrl.fromLocalFile(self.homepage_path)
        elif isinstance(url, str):
            url = QUrl(url)
        elif not isinstance(url, QUrl):
            print(f"Invalid URL type: {type(url)}. Expected QUrl or str.")
            return

        new_tab = QWebEngineView()
        new_tab.setUrl(url)
        index = self.tabs.addTab(new_tab, title)
        self.tabs.setCurrentIndex(index)
        new_tab.page().titleChanged.connect(lambda: self.update_tab_title(index))
        new_tab.page().iconChanged.connect(lambda: self.update_tab_icon(index))
        new_tab.loadFinished.connect(self.update_nav_buttons)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            reply = QMessageBox.question(self, 'Confirm Exit',
                                         'This is the last tab. Quit?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.close()

    def update_url(self, q):
        url_str = q.toString()
        if url_str.startswith('file:///'):
            url_str = ''
        self.UrlBar.setText(url_str)

    def update_nav_buttons(self):
        current_browser = self.current_browser()
        if current_browser:
            self.backbtn.setEnabled(current_browser.history().canGoBack())
            self.forwardbtn.setEnabled(current_browser.history().canGoForward())

    def update_tab_title(self, index):
        current_browser = self.tabs.widget(index)
        title = current_browser.page().title()
        self.tabs.setTabText(index, title)

    def update_tab_icon(self, index):
        current_browser = self.tabs.widget(index)
        icon = current_browser.page().icon()
        if icon:
            pixmap = icon.pixmap(16, 16)
            self.tabs.tabBar().setTabIcon(index, QIcon(pixmap))

    def current_browser(self):
        if self.tabs and self.tabs.count() > 0:
            return self.tabs.currentWidget()
        return None

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                return json.load(file)
        return []
    
    def save_history(self, url):
        history = self.load_history()
        if url not in history:
            history.append(url)
            with open(self.history_file, 'w') as file:
                json.dump(history, file)

# Startup
if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Meseclet Browser")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
