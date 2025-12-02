"""
主窗口界面
提供用户交互界面
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QSpinBox, QPushButton, QGroupBox, QMessageBox,
    QComboBox, QInputDialog, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 自定义信号
    settings_changed = pyqtSignal()
    
    def __init__(self, gamma_engine, config_manager, hotkey_manager, preset_manager=None):
        """
        初始化主窗口
        
        参数:
            gamma_engine: Gamma 引擎
            config_manager: 配置管理器
            hotkey_manager: 热键管理器
            preset_manager: 预设管理器
        """
        super().__init__()
        self.gamma_engine = gamma_engine
        self.config_manager = config_manager
        self.hotkey_manager = hotkey_manager
        self.preset_manager = preset_manager
        
        # 防抖定时器
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._apply_changes)
        
        self.setup_ui()
        self.load_settings()
        
        # 检查 Gamma Ramp 支持
        if not self.gamma_engine.is_supported():
            self._show_unsupported_warning()
        
        logger.info("主窗口初始化完成")
    
    def _show_unsupported_warning(self):
        """显示不支持警告"""
        QMessageBox.warning(
            self,
            "功能受限",
            "⚠️ 您的显卡驱动不支持 Gamma Ramp API\n\n"
            "这是 Windows 10/11 和现代显卡驱动的常见限制。\n"
            "程序界面可以正常使用,但无法实际调节屏幕亮度。\n\n"
            "建议解决方案:\n"
            "• 使用显卡控制面板(NVIDIA/AMD/Intel)调节\n"
            "• 使用 Windows 夜间模式功能\n"
            "• 使用显示器的物理按钮调节\n"
            "• 尝试更新或回退显卡驱动\n\n"
            "详细信息请查看日志文件。"
        )
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("GammaTool - 屏幕亮度调节工具")
        self.setFixedSize(450, 620)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 预设管理组（如果有预设管理器）
        if self.preset_manager:
            preset_group = self.create_preset_group()
            main_layout.addWidget(preset_group)
        
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
    
    def create_preset_group(self):
        """创建预设管理组"""
        group = QGroupBox("配置预设")
        layout = QVBoxLayout()
        
        # 当前预设标签
        current_label = QLabel("当前预设: 无")
        current_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.current_preset_label = current_label
        layout.addWidget(current_label)
        
        # 预设按钮容器（使用滚动区域）
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(150)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        preset_widget = QWidget()
        self.preset_buttons_layout = QVBoxLayout()
        self.preset_buttons_layout.setSpacing(5)
        preset_widget.setLayout(self.preset_buttons_layout)
        scroll_area.setWidget(preset_widget)
        
        layout.addWidget(scroll_area)
        
        # 存储预设按钮的字典
        self.preset_buttons = {}
        
        # 创建预设按钮
        self.update_preset_buttons()
        
        # 预设操作按钮行
        button_row = QHBoxLayout()
        
        # 保存当前配置按钮
        save_btn = QPushButton("💾 保存配置")
        save_btn.clicked.connect(self.on_save_preset)
        button_row.addWidget(save_btn)
        
        # 删除预设按钮
        delete_btn = QPushButton("🗑️ 删除预设")
        delete_btn.clicked.connect(self.on_delete_preset)
        button_row.addWidget(delete_btn)
        
        # 设置快捷键按钮
        hotkey_btn = QPushButton("⌨️ 设置快捷键")
        hotkey_btn.clicked.connect(self.on_preset_hotkey_settings)
        button_row.addWidget(hotkey_btn)
        
        layout.addLayout(button_row)
        
        group.setLayout(layout)
        return group
    
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
            
            success = self.gamma_engine.apply_settings()
            
            if success:
                # 发送设置变更信号
                self.settings_changed.emit()
                logger.debug(f"设置已应用: 亮度={brightness}, 对比度={contrast}, "
                            f"灰度={grayscale}, RGB=({red},{green},{blue})")
            else:
                if not self.gamma_engine.is_supported():
                    logger.debug("设置未应用: Gamma Ramp API 不受支持")
                    
        except Exception as e:
            logger.error(f"应用设置失败: {e}")
    
    
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
    
    def get_current_settings(self):
        """
        获取当前设置
        
        返回:
            dict: 当前设置字典
        """
        return {
            'brightness': self.brightness_slider.value(),
            'contrast': self.contrast_slider.value(),
            'grayscale': self.grayscale_slider.value(),
            'rgb': {
                'red': self.red_slider.value(),
                'green': self.green_slider.value(),
                'blue': self.blue_slider.value()
            }
        }
    
    def apply_settings(self, settings):
        """
        应用设置到界面
        
        参数:
            settings: 设置字典
        """
        self.brightness_slider.setValue(settings.get('brightness', 100))
        self.contrast_slider.setValue(settings.get('contrast', 100))
        self.grayscale_slider.setValue(settings.get('grayscale', 0))
        rgb = settings.get('rgb', {'red': 255, 'green': 255, 'blue': 255})
        self.red_slider.setValue(rgb.get('red', 255))
        self.green_slider.setValue(rgb.get('green', 255))
        self.blue_slider.setValue(rgb.get('blue', 255))
    
    def update_preset_buttons(self):
        """更新预设按钮列表"""
        if not self.preset_manager:
            return
        
        # 清除现有按钮
        for button in self.preset_buttons.values():
            button.deleteLater()
        self.preset_buttons.clear()
        
        # 获取当前预设
        current_preset = self.preset_manager.get_current_preset_name()
        
        # 为每个预设创建按钮
        for preset_name in self.preset_manager.get_preset_names():
            btn = QPushButton(preset_name)
            btn.setMinimumHeight(35)
            
            # 获取快捷键
            hotkey = self.preset_manager.get_preset_hotkey(preset_name)
            if hotkey:
                btn.setText(f"{preset_name} ({hotkey})")
            
            # 如果是当前预设，高亮显示
            if preset_name == current_preset:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        font-weight: bold;
                        border: 2px solid #1976D2;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
            
            # 连接点击事件
            btn.clicked.connect(lambda checked, name=preset_name: self.on_preset_button_clicked(name))
            
            self.preset_buttons_layout.addWidget(btn)
            self.preset_buttons[preset_name] = btn
        
        # 更新当前预设标签
        if current_preset:
            self.current_preset_label.setText(f"当前预设: {current_preset}")
        else:
            self.current_preset_label.setText("当前预设: 无")
    
    def on_preset_button_clicked(self, preset_name):
        """
        预设按钮点击事件
        
        参数:
            preset_name: 预设名称
        """
        if not preset_name or not self.preset_manager:
            return
        
        try:
            settings = self.preset_manager.load_preset(preset_name)
            if settings:
                self.apply_settings(settings)
                self.update_preset_buttons()  # 更新按钮状态
                logger.info(f"已切换到预设: {preset_name}")
        except Exception as e:
            logger.error(f"切换预设失败: {e}")
            QMessageBox.warning(self, "错误", f"切换预设失败: {e}")
    
    def on_save_preset(self):
        """保存当前配置为预设"""
        if not self.preset_manager:
            return
        
        try:
            # 询问预设名称
            name, ok = QInputDialog.getText(
                self,
                "保存配置",
                "请输入预设名称:",
                text=self.preset_manager.get_current_preset_name() or ""
            )
            
            if ok and name:
                settings = self.get_current_settings()
                if self.preset_manager.save_preset(name, settings):
                    # 更新预设按钮
                    self.update_preset_buttons()
                    QMessageBox.information(self, "成功", f"配置已保存为: {name}")
                    logger.info(f"配置已保存为预设: {name}")
                else:
                    QMessageBox.warning(self, "错误", "保存配置失败")
        except Exception as e:
            logger.error(f"保存预设失败: {e}")
            QMessageBox.warning(self, "错误", f"保存配置失败: {e}")
    
    def on_delete_preset(self):
        """删除当前预设"""
        if not self.preset_manager:
            return
        
        try:
            current_preset = self.preset_manager.get_current_preset_name()
            if not current_preset:
                QMessageBox.warning(self, "提示", "请先切换到要删除的预设")
                return
            
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除预设 '{current_preset}' 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.preset_manager.delete_preset(current_preset):
                    self.update_preset_buttons()
                    QMessageBox.information(self, "成功", f"预设 '{current_preset}' 已删除")
                    logger.info(f"预设已删除: {current_preset}")
                else:
                    QMessageBox.warning(self, "错误", "删除预设失败")
        except Exception as e:
            logger.error(f"删除预设失败: {e}")
            QMessageBox.warning(self, "错误", f"删除预设失败: {e}")
    
    def on_preset_hotkey_settings(self):
        """预设快捷键设置按钮点击"""
        try:
            from hotkey_dialog import PresetHotkeyDialog
            dialog = PresetHotkeyDialog(self.preset_manager, self)
            if dialog.exec_():
                # 更新预设按钮显示
                self.update_preset_buttons()
                logger.info("预设快捷键设置已更新")
        except Exception as e:
            logger.error(f"打开预设快捷键设置对话框失败: {e}")
            QMessageBox.warning(self, "错误", f"打开预设快捷键设置对话框失败: {e}")
    
    def switch_to_next_preset(self):
        """切换到下一个预设"""
        if not self.preset_manager:
            return
        
        try:
            settings = self.preset_manager.switch_to_next_preset()
            if settings:
                self.apply_settings(settings)
                # 更新预设按钮状态
                self.update_preset_buttons()
                current_preset = self.preset_manager.get_current_preset_name()
                logger.info(f"已切换到预设: {current_preset}")
        except Exception as e:
            logger.error(f"切换预设失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 直接关闭应用程序，不再最小化到托盘
        event.accept()
        # 触发应用程序退出
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()
        logger.info("窗口已关闭，应用程序退出")