"""
GammaTool 主程序入口
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from gamma_engine import GammaEngine
from main_window import MainWindow
from hotkey_manager import HotkeyManager
from config_manager import ConfigManager
from tray_icon import TrayIcon
from preset_manager import PresetManager
from utils import get_resource_path, setup_logging

import logging

logger = None


class GammaTool:
    """主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        # 初始化 Qt 应用
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("GammaTool")
        self.app.setQuitOnLastWindowClosed(False)
        
        # 初始化日志
        global logger
        logger = setup_logging()
        logger.info("=" * 60)
        logger.info("GammaTool 启动")
        logger.info("=" * 60)
        
        try:
            # 初始化各个组件
            self.config_manager = ConfigManager()
            self.gamma_engine = GammaEngine()
            self.hotkey_manager = HotkeyManager()
            self.preset_manager = PresetManager()
            
            # 创建主窗口
            self.main_window = MainWindow(
                self.gamma_engine,
                self.config_manager,
                self.hotkey_manager,
                self.preset_manager
            )
            
            # 创建系统托盘
            icon_path = get_resource_path("resources/icons/tray_icon.png")
            # 如果图标不存在，使用默认图标
            if not Path(icon_path).exists():
                logger.warning(f"托盘图标不存在: {icon_path}，使用默认图标")
                icon_path = ""
            
            self.tray_icon = TrayIcon(icon_path, self.main_window)
            
            # 连接信号
            self.setup_connections()
            
            # 加载配置并应用
            self.load_and_apply_settings()
            
            # 注册热键
            self.register_hotkeys()
            
            # 显示托盘图标
            self.tray_icon.show()
            self.tray_icon.show_message(
                "GammaTool",
                "程序已启动，双击托盘图标显示主窗口",
                duration=2000
            )
            
            # 根据配置决定是否显示主窗口
            if not self.config_manager.get('ui.start_minimized', False):
                self.main_window.show()
            
            logger.info("应用程序初始化完成")
            
        except Exception as e:
            logger.error(f"应用程序初始化失败: {e}", exc_info=True)
            sys.exit(1)
    
    def setup_connections(self):
        """设置信号连接"""
        # 托盘图标信号
        self.tray_icon.show_window.connect(self.show_main_window)
        self.tray_icon.reset_settings.connect(self.reset_settings)
        self.tray_icon.quit_app.connect(self.quit_application)
        self.tray_icon.brightness_changed.connect(self.set_brightness)
        
        # 主窗口信号
        self.main_window.settings_changed.connect(self.on_settings_changed)
        
        logger.debug("信号连接已设置")
    
    def load_and_apply_settings(self):
        """加载配置并应用"""
        try:
            # 加载显示设置
            brightness = self.config_manager.get('display.brightness', 100)
            contrast = self.config_manager.get('display.contrast', 100)
            grayscale = self.config_manager.get('display.grayscale', 0)
            rgb = self.config_manager.get('display.rgb', 
                                         {'red': 255, 'green': 255, 'blue': 255})
            
            # 应用到引擎
            self.gamma_engine.set_brightness(brightness)
            self.gamma_engine.set_contrast(contrast)
            self.gamma_engine.set_grayscale(grayscale)
            self.gamma_engine.set_rgb(rgb['red'], rgb['green'], rgb['blue'])
            self.gamma_engine.apply_settings()
            
            logger.info("配置已加载并应用")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def register_hotkeys(self):
        """注册预设快捷键"""
        try:
            # 获取所有预设的快捷键
            preset_hotkeys = self.preset_manager.get_all_hotkeys()
            
            # 为每个预设注册快捷键
            for preset_name, hotkey in preset_hotkeys.items():
                if hotkey:
                    # 使用闭包捕获预设名称
                    self.hotkey_manager.register_hotkey(
                        hotkey,
                        lambda name=preset_name: self.switch_to_preset(name),
                        f"切换到预设: {preset_name}"
                    )
            
            self.hotkey_manager.start_listening()
            
            if preset_hotkeys:
                logger.info(f"已注册 {len(preset_hotkeys)} 个预设快捷键")
            else:
                logger.info("未设置预设快捷键")
            
        except Exception as e:
            logger.error(f"注册预设快捷键失败: {e}")
    
    def switch_to_preset(self, preset_name):
        """
        切换到指定预设
        
        参数:
            preset_name: 预设名称
        """
        try:
            settings = self.preset_manager.load_preset(preset_name)
            if settings:
                # 应用设置到引擎
                self.gamma_engine.set_brightness(settings.get('brightness', 100))
                self.gamma_engine.set_contrast(settings.get('contrast', 100))
                self.gamma_engine.set_grayscale(settings.get('grayscale', 0))
                rgb = settings.get('rgb', {'red': 255, 'green': 255, 'blue': 255})
                self.gamma_engine.set_rgb(rgb['red'], rgb['green'], rgb['blue'])
                self.gamma_engine.apply_settings()
                
                # 更新主窗口
                self.main_window.apply_settings(settings)
                self.main_window.update_preset_buttons()
                
                # 显示通知
                self.tray_icon.show_message(
                    "GammaTool",
                    f"已切换到预设: {preset_name}",
                    duration=1500
                )
                
                logger.info(f"通过快捷键切换到预设: {preset_name}")
        except Exception as e:
            logger.error(f"切换到预设失败 [{preset_name}]: {e}")
    
    def set_brightness(self, value):
        """
        设置亮度（用于托盘菜单）
        
        参数:
            value: 亮度值
        """
        try:
            self.gamma_engine.set_brightness(value)
            self.gamma_engine.apply_settings()
            self.main_window.update_brightness_slider(value)
            self.config_manager.set('display.brightness', value)
            
            self.tray_icon.show_message(
                "GammaTool",
                f"亮度已设置为 {value}%",
                duration=1000
            )
            
            logger.info(f"亮度已设置为: {value}")
        except Exception as e:
            logger.error(f"设置亮度失败: {e}")
    
    def on_settings_changed(self):
        """设置变更时保存"""
        try:
            settings = self.gamma_engine.get_current_settings()
            self.config_manager.set('display.brightness', settings['brightness'])
            self.config_manager.set('display.contrast', settings['contrast'])
            self.config_manager.set('display.grayscale', settings['grayscale'])
            self.config_manager.set('display.rgb', settings['rgb'])
            
            logger.debug("设置已保存到配置文件")
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
    
    def reset_settings(self):
        """恢复默认设置"""
        try:
            self.gamma_engine.reset_to_default()
            self.main_window.on_reset()
            self.tray_icon.show_message("GammaTool", "已恢复默认设置")
            
            logger.info("已恢复默认设置")
        except Exception as e:
            logger.error(f"恢复默认设置失败: {e}")
    
    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.activateWindow()
        logger.debug("主窗口已显示")
    
    def toggle_main_window(self):
        """切换主窗口显示状态"""
        if self.main_window.isVisible():
            self.main_window.hide()
            logger.debug("主窗口已隐藏")
        else:
            self.show_main_window()
    
    
    def quit_application(self):
        """退出应用程序"""
        try:
            logger.info("正在退出应用程序...")
            
            # 恢复默认设置
            if self.config_manager.get('system.restore_on_exit', True):
                self.gamma_engine.reset_to_default()
                logger.info("已恢复默认 Gamma 设置")
            
            # 停止热键监听
            self.hotkey_manager.stop_listening()
            
            # 隐藏托盘图标
            self.tray_icon.hide()
            
            logger.info("GammaTool 已退出")
            logger.info("=" * 60)
            
            # 退出应用
            self.app.quit()
            
        except Exception as e:
            logger.error(f"退出应用程序时出错: {e}")
            self.app.quit()
    
    def run(self):
        """运行应用程序"""
        return self.app.exec_()


def main():
    """主函数"""
    try:
        app = GammaTool()
        sys.exit(app.run())
    except Exception as e:
        if logger:
            logger.critical(f"程序崩溃: {e}", exc_info=True)
        else:
            print(f"程序崩溃: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()