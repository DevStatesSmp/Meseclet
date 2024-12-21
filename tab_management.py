from PyQt5.QtWidgets import QPushButton, QTabBar, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class BrowserTab(QWidget):
    def __init__(self, url="about:blank"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.setUrl(url)
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

class TabManagement:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tabs = self.main_window.tabs
        self.homepage_path = self.main_window.homepage_path
        self.add_plus_button()

    def add_new_tab(self, url, title="New Tab"):
        new_tab = BrowserTab(url)
        index = self.tabs.addTab(new_tab, title)
        self.tabs.setCurrentIndex(index)  # Switch to the new tab

    def add_plus_button(self):
        """ Adds a '+' button to the tab bar """
        self.plus_button = QPushButton("+")
        self.plus_button.setFixedSize(30, 30)  # Adjust size as needed
        self.plus_button.clicked.connect(self.add_new_tab_from_button)
        self.tab_bar = self.tabs.tabBar()
        self.tab_bar.setTabButton(self.tabs.count(), QTabBar.RightSide, self.plus_button)

    def add_new_tab_from_button(self):
        """ Called when the '+' button is clicked """
        self.add_new_tab(QUrl.fromLocalFile(self.homepage_path), "New Tab")

    def close_tab(self, index):
        if self.tabs.count() > 1:  # Ensure at least one tab remains
            self.tabs.removeTab(index)

    def update_url(self, q):
        self.main_window.UrlBar.setText(q.toString())

    def navigate_to_url(self):
        url = self.main_window.UrlBar.text().strip()
        if not url.startswith("http"):
            if " " in url:
                url = "https://www.google.com/search?q=" + url.replace(" ", "+")
            else:
                url = "http://" + url
        current_tab = self.tabs.currentWidget()  # Get the active tab
        if isinstance(current_tab, BrowserTab):  # Ensure it's a valid tab
            current_tab.browser.setUrl(QUrl(url))

    def update_url_from_tab(self):
        current_tab = self.tabs.currentWidget()  # Get the active tab
        if isinstance(current_tab, BrowserTab):  # Ensure it's a valid tab
            self.main_window.UrlBar.setText(current_tab.browser.url().toString())
