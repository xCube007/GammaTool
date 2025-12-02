"""
系统托盘图标
提供系统托盘图标和右键菜单
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject
import logging

logger = logging.getLogger(__name__)


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标"""
    
    # 自定义信号
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    reset_settings = pyqtSignal()
    quit_app = pyqtSignal()
    brightness_changed = pyqtSignal(int)
    
    def __init__(self, icon_path, parent=None):
        """
        初始化系统托盘图标
        
        参数:
            icon_path: 图标路径
            parent: 父对象
        """
        super().__init__(QIcon(icon_path), parent)
        self.setup_menu()
        self.setup_signals()
        logger.info("系统托盘图标初始化完成")
    
    def setup_menu(self):
        """设置右键菜单"""
        menu = QMenu()
        
        # 显示主窗口
        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_window.emit)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # 快速调节子菜单
        quick_menu = menu.addMenu("快速调节")
        
        # 亮度预设
        brightness_menu = quick_menu.addMenu("亮度")
        for value in [50, 75, 100, 125, 150]:
            action = QAction(f"{value}%", self)
            action.triggered.connect(
                lambda checked, v=value: self.brightness_changed.emit(v)
            )
            brightness_menu.addAction(action)
        
        menu.addSeparator()
        
        # 恢复默认
        reset_action = QAction("恢复默认", self)
        reset_action.triggered.connect(self.reset_settings.emit)
        menu.addAction(reset_action)
        
        menu.addSeparator()
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        logger.debug("托盘菜单已设置")
    
    def setup_signals(self):
        """设置信号连接"""
        # 双击显示主窗口
        self.activated.connect(self.on_activated)
    
    def on_activated(self, reason):
        """
        托盘图标激活事件
        
        参数:
            reason: 激活原因
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window.emit()
            logger.debug("双击托盘图标，显示主窗口")
    
    def show_message(self, title, message, icon=None, duration=3000):
        """
        显示气泡通知
        
        参数:
            title: 标题
            message: 消息内容
            icon: 图标类型
            duration: 显示时长（毫秒）
        """
        if icon is None:
            icon = QSystemTrayIcon.Information
        self.showMessage(title, message, icon, duration)
        logger.debug(f"显示托盘通知: {title} - {message}")
    
    def update_tooltip(self, text):
        """
        更新工具提示
        
        参数:
            text: 提示文本
        """
        self.setToolTip(text)