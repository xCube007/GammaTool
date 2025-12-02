"""
主窗口界面
提供用户交互界面
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 自定义信号
    settings_changed = pyqtSignal()
    
    def __init__(self, gamma_engine, config_manager, hotkey_manager):
        """
        初始化主窗口
        
        参数:
            gamma_engine: Gamma 引擎
            config_manager: 配置管理器
            hotkey_manager: 热键管理器
        """
        super().__init__()
        self.gamma_engine = gamma_engine
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        
        # 防抖定时器
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._apply_changes)
        
        self.setup_ui()
        self.load_settings()
        logger.info("主窗口初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("GammaTool - 屏幕亮度调节工具")
        self.setFixedSize(450, 550)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 基础调节组
        basic_group = self.create_basic_group()
        main_layout.addWidget(basic_group)
        
        # RGB 通道调节组
        rgb_group = self.create_rgb_group()
        main_layout.addWidget(rgb_group)
        
        # 按钮组
        button_layout = self.create_button_layout()
        main_layout.addLayout(button_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        logger.debug("UI 界面已设置")
    
    def create_basic_group(self):
        """创建基础调节组"""
        group = QGroupBox("基础调节")
        layout = QVBoxLayout()
        
        # 亮度
        self.brightness_slider, self.brightness_spinbox = self.create_slider_row(
            "亮度:", 0, 200, 100, layout
        )
        
        # 对比度
        self.contrast_slider, self.contrast_spinbox = self.create_slider_row(
            "对比度:", 0, 200, 100, layout
        )
        
        # 灰度
        self.grayscale_slider, self.grayscale_spinbox = self.create_slider_row(
            "灰度:", 0, 100, 0, layout
        )
        
        group.setLayout(layout)
        return group
    
    def create_rgb_group(self):
        """创建 RGB 通道调节组"""
        group = QGroupBox("RGB 通道调节")
        layout = QVBoxLayout()
        
        # 红色通道
        self.red_slider, self.red_spinbox = self.create_slider_row(
            "红色:", 0, 255, 255, layout
        )
        
        # 绿色通道
        self.green_slider, self.green_spinbox = self.create_slider_row(
            "绿色:", 0, 255, 255, layout
        )
        
        # 蓝色通道
        self.blue_slider, self.blue_spinbox = self.create_slider_row(
            "蓝色:", 0, 255, 255, layout
        )
        
        group.setLayout(layout)
        return group
    
    def create_slider_row(self, label_text, min_val, max_val, default_val, parent_layout):
        """
        创建滑块行
        
        参数:
            label_text: 标签文本
            min_val: 最小值
            max_val: 最大值
            default_val: 默认值
            parent_layout: 父布局
        
        返回:
            tuple: (slider, spinbox)
        """
        row_layout = QHBoxLayout()
        
        # 标签
        label = QLabel(label_text)
        label.setFixedWidth(60)
        row_layout.addWidget(label)
        
        # 滑块
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(self.on_slider_changed)
        row_layout.addWidget(slider)
        
        # 数值框
        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default_val)
        spinbox.setFixedWidth(70)
        spinbox.valueChanged.connect(self.on_spinbox_changed)
        row_layout.addWidget(spinbox)
        
        # 连接滑块和数值框
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)
        
        parent_layout.addLayout(row_layout)
        return slider, spinbox
    
    def create_button_layout(self):
        """创建按钮布局"""
        layout = QHBoxLayout()
        
        # 热键设置按钮
        hotkey_btn = QPushButton("⚙️ 热键设置")
        hotkey_btn.clicked.connect(self.on_hotkey_settings)
        layout.addWidget(hotkey_btn)
        
        # 恢复默认按钮
        reset_btn = QPushButton("🔄 恢复默认")
        reset_btn.clicked.connect(self.on_reset)
        layout.addWidget(reset_btn)
        
        # 最小化按钮
        minimize_btn = QPushButton("➖ 最小化")
        minimize_btn.clicked.connect(self.hide)
        layout.addWidget(minimize_btn)
        
        return layout
    
    def on_slider_changed(self, value):
        """滑块值变化时触发"""
        # 重启防抖定时器
        debounce_delay = self.config_manager.get('advanced.debounce_delay', 100)
        self._debounce_timer.stop()
        self._debounce_timer.start(debounce_delay)
    
    def on_spinbox_changed(self, value):
        """数值框值变化时触发"""
        # 重启防抖定时器
        debounce_delay = self.config_manager.get('advanced.debounce_delay', 100)
        self._debounce_timer.stop()
        self._debounce_timer.start(debounce_delay)
    
    def _apply_changes(self):
        """实际应用更改"""
        try:
            # 获取所有滑块的值
            brightness = self.brightness_slider.value()
            contrast = self.contrast_slider.value()
            grayscale = self.grayscale_slider.value()
            red = self.red_slider.value()
            green = self.green_slider.value()
            blue = self.blue_slider.value()
            
            # 应用到 Gamma 引擎
            self.gamma_engine.set_brightness(brightness)
            self.gamma_engine.set_contrast(contrast)
            self.gamma_engine.set_grayscale(grayscale)
            self.gamma_engine.set_rgb(red, green, blue)
            self.gamma_engine.apply_settings()
            
            # 发送设置变更信号
            self.settings_changed.emit()
            
            logger.debug(f"设置已应用: 亮度={brightness}, 对比度={contrast}, "
                        f"灰度={grayscale}, RGB=({red},{green},{blue})")
        except Exception as e:
            logger.error(f"应用设置失败: {e}")
    
    def on_hotkey_settings(self):
        """热键设置按钮点击"""
        # TODO: 实现热键设置对话框
        logger.info("热键设置功能待实现")
    
    def on_reset(self):
        """恢复默认按钮点击"""
        try:
            # 恢复 Gamma 引擎默认值
            self.gamma_engine.reset_to_default()
            
            # 更新界面
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.grayscale_slider.setValue(0)
            self.red_slider.setValue(255)
            self.green_slider.setValue(255)
            self.blue_slider.setValue(255)
            
            logger.info("已恢复默认设置")
        except Exception as e:
            logger.error(f"恢复默认设置失败: {e}")
    
    def load_settings(self):
        """从配置加载设置"""
        try:
            brightness = self.config_manager.get('display.brightness', 100)
            contrast = self.config_manager.get('display.contrast', 100)
            grayscale = self.config_manager.get('display.grayscale', 0)
            rgb = self.config_manager.get('display.rgb', 
                                         {'red': 255, 'green': 255, 'blue': 255})
            
            # 更新界面
            self.brightness_slider.setValue(brightness)
            self.contrast_slider.setValue(contrast)
            self.grayscale_slider.setValue(grayscale)
            self.red_slider.setValue(rgb['red'])
            self.green_slider.setValue(rgb['green'])
            self.blue_slider.setValue(rgb['blue'])
            
            logger.info("配置已加载到界面")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def update_brightness_slider(self, value):
        """
        更新亮度滑块（用于热键调节）
        
        参数:
            value: 亮度值
        """
        self.brightness_slider.setValue(value)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果配置为关闭到托盘，则隐藏窗口而不是关闭
        if self.config_manager.get('system.close_to_tray', True):
            event.ignore()
            self.hide()
            logger.debug("窗口已最小化到托盘")
        else:
            event.accept()
            logger.info("窗口已关闭")