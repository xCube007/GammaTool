"""
热键设置对话框
允许用户自定义预设快捷键
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QGroupBox, QMessageBox, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class PresetHotkeyDialog(QDialog):
    """预设快捷键设置对话框"""
    
    def __init__(self, preset_manager, parent=None):
        """
        初始化预设快捷键设置对话框
        
        参数:
            preset_manager: 预设管理器
            parent: 父窗口
        """
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.hotkey_inputs = {}
        self.setup_ui()
        self.load_hotkeys()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("预设快捷键设置")
        self.setMinimumSize(500, 450)
        
        layout = QVBoxLayout()
        
        # 说明文本
        info_label = QLabel(
            "为每个预设设置快捷键，点击输入框后按下热键组合\n"
            "支持的修饰键: Ctrl, Alt, Shift\n"
            "例如: ctrl+alt+1, ctrl+shift+n\n"
            "留空表示不设置快捷键"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # 热键设置组（使用滚动区域）
        hotkey_group = QGroupBox("预设快捷键配置")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(250)
        
        scroll_widget = QWidget()
        hotkey_layout = QVBoxLayout()
        
        # 为每个预设创建热键输入行
        preset_names = self.preset_manager.get_preset_names()
        for preset_name in preset_names:
            row = self.create_hotkey_row(preset_name)
            hotkey_layout.addLayout(row)
        
        scroll_widget.setLayout(hotkey_layout)
        scroll_area.setWidget(scroll_widget)
        
        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll_area)
        hotkey_group.setLayout(group_layout)
        layout.addWidget(hotkey_group)
        
        # 按钮行
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 保存")
        save_btn.clicked.connect(self.save_hotkeys)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("🔄 恢复默认")
        reset_btn.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_hotkey_row(self, preset_name):
        """
        创建热键设置行
        
        参数:
            preset_name: 预设名称
        
        返回:
            QHBoxLayout: 热键行布局
        """
        row = QHBoxLayout()
        
        label = QLabel(preset_name + ":")
        label.setFixedWidth(120)
        label.setStyleSheet("font-weight: bold;")
        row.addWidget(label)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText("点击后按下热键组合（可留空）")
        input_field.setReadOnly(True)
        input_field.mousePressEvent = lambda e: self.start_recording(preset_name)
        row.addWidget(input_field)
        
        clear_btn = QPushButton("清除")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(lambda: self.clear_hotkey(preset_name))
        row.addWidget(clear_btn)
        
        self.hotkey_inputs[preset_name] = input_field
        
        return row
    
    def start_recording(self, key):
        """
        开始录制热键
        
        参数:
            key: 热键键名
        """
        input_field = self.hotkey_inputs[key]
        input_field.setText("按下热键组合...")
        input_field.setFocus()
        
        # 安装事件过滤器来捕获按键
        input_field.keyPressEvent = lambda e: self.record_hotkey(key, e)
    
    def record_hotkey(self, key, event):
        """
        录制热键
        
        参数:
            key: 热键键名
            event: 键盘事件
        """
        modifiers = []
        
        # 检查修饰键
        if event.modifiers() & Qt.ControlModifier:
            modifiers.append("ctrl")
        if event.modifiers() & Qt.AltModifier:
            modifiers.append("alt")
        if event.modifiers() & Qt.ShiftModifier:
            modifiers.append("shift")
        
        # 获取主键
        key_text = event.text().lower()
        if not key_text and event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right]:
            key_map = {
                Qt.Key_Up: "up",
                Qt.Key_Down: "down",
                Qt.Key_Left: "left",
                Qt.Key_Right: "right"
            }
            key_text = key_map.get(event.key(), "")
        
        # 组合热键字符串
        if modifiers and key_text:
            hotkey = "+".join(modifiers + [key_text])
            self.hotkey_inputs[key].setText(hotkey)
        elif not modifiers:
            self.hotkey_inputs[key].setText("请使用修饰键组合")
    
    def clear_hotkey(self, key):
        """
        清除热键
        
        参数:
            key: 热键键名
        """
        self.hotkey_inputs[key].setText("")
    
    def load_hotkeys(self):
        """从预设管理器加载热键"""
        try:
            for preset_name, input_field in self.hotkey_inputs.items():
                hotkey = self.preset_manager.get_preset_hotkey(preset_name)
                if hotkey:
                    input_field.setText(hotkey)
            logger.debug("预设快捷键配置已加载")
        except Exception as e:
            logger.error(f"加载预设快捷键配置失败: {e}")
    
    def save_hotkeys(self):
        def save_hotkeys(self):
            """保存预设快捷键配置"""
            try:
                # 检查是否有重复的快捷键
                hotkey_map = {}
                for preset_name, input_field in self.hotkey_inputs.items():
                    hotkey_text = input_field.text().strip()
                    if hotkey_text and hotkey_text != "按下热键组合..." and hotkey_text != "请使用修饰键组合":
                        if hotkey_text in hotkey_map:
                            QMessageBox.warning(
                                self,
                                "快捷键冲突",
                                f"快捷键 '{hotkey_text}' 被多个预设使用：\n"
                                f"- {hotkey_map[hotkey_text]}\n"
                                f"- {preset_name}\n\n"
                                f"请为每个预设设置不同的快捷键。"
                            )
                            return
                        hotkey_map[hotkey_text] = preset_name
                
                # 保存到预设管理器
                for preset_name, input_field in self.hotkey_inputs.items():
                    hotkey_text = input_field.text().strip()
                    if hotkey_text and hotkey_text != "按下热键组合..." and hotkey_text != "请使用修饰键组合":
                        self.preset_manager.set_preset_hotkey(preset_name, hotkey_text)
                    else:
                        self.preset_manager.set_preset_hotkey(preset_name, "")
                
                QMessageBox.information(
                    self,
                    "成功",
                    "预设快捷键配置已保存！\n\n请重启程序以使新快捷键生效。"
                )
                
                logger.info("预设快捷键配置已保存")
                self.accept()
                
            except Exception as e:
                logger.error(f"保存预设快捷键配置失败: {e}")
                QMessageBox.warning(self, "错误", f"保存预设快捷键配置失败: {e}")
    def reset_to_default(self):
        """清除所有快捷键"""
        try:
            reply = QMessageBox.question(
                self,
                "确认清除",
                "确定要清除所有预设的快捷键吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                for input_field in self.hotkey_inputs.values():
                    input_field.setText("")
                
                logger.info("已清除所有预设快捷键")
                
        except Exception as e:
            logger.error(f"清除预设快捷键失败: {e}")
            QMessageBox.warning(self, "错误", f"清除预设快捷键失败: {e}")