"""
配置管理器
负责配置文件的读写和管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config: Dict[str, Any] = {}
        self.load_config()
        logger.info(f"配置管理器初始化完成，配置文件: {self.config_file}")
    
    def _get_config_dir(self) -> Path:
        """
        获取配置目录
        
        返回:
            Path: 配置目录路径
        """
        # Windows: %APPDATA%/GammaTool
        appdata = os.getenv('APPDATA')
        if appdata:
            config_dir = Path(appdata) / "GammaTool"
        else:
            # 备用方案：使用用户主目录
            config_dir = Path.home() / ".gammatool"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self._validate_config()
                logger.info("配置文件加载成功")
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
                self.config = self._get_default_config()
                self.save_config()
        else:
            logger.info("配置文件不存在，使用默认配置")
            self.config = self._get_default_config()
            self.save_config()
    
    def save_config(self):
        """
        保存配置
        
        返回:
            bool: 是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("配置文件保存成功")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        返回:
            dict: 默认配置
        """
        return {
            "version": "1.0.0",
            "display": {
                "brightness": 100,
                "contrast": 100,
                "grayscale": 0,
                "rgb": {"red": 255, "green": 255, "blue": 255}
            },
            "hotkeys": {
                "increase_brightness": "ctrl+alt+up",
                "decrease_brightness": "ctrl+alt+down",
                "increase_contrast": "ctrl+alt+right",
                "decrease_contrast": "ctrl+alt+left",
                "reset": "ctrl+alt+r",
                "toggle_window": "ctrl+alt+g"
            },
            "ui": {
                "theme": "dark",
                "window_opacity": 0.95,
                "always_on_top": False,
                "start_minimized": False
            },
            "system": {
                "auto_start": False,
                "minimize_to_tray": True,
                "close_to_tray": True,
                "restore_on_exit": True
            },
            "advanced": {
                "adjustment_step": 5,
                "smooth_transition": True,
                "transition_duration": 200,
                "debounce_delay": 100
            }
        }
    
    def _validate_config(self):
        """验证配置，确保所有必需的键都存在"""
        default = self._get_default_config()
        
        def merge_dict(target, source):
            """递归合并字典"""
            for key, value in source.items():
                if key not in target:
                    target[key] = value
                elif isinstance(value, dict) and isinstance(target[key], dict):
                    merge_dict(target[key], value)
        
        merge_dict(self.config, default)
    
    def get(self, key: str, default=None):
        """
        获取配置值
        
        参数:
            key: 配置键，支持点号分隔的嵌套键，如 'display.brightness'
            default: 默认值
        
        返回:
            配置值
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        参数:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()
        logger.debug(f"配置已更新: {key} = {value}")
    
    def reset_to_default(self):
        """
        重置为默认配置
        
        返回:
            bool: 是否成功
        """
        self.config = self._get_default_config()
        success = self.save_config()
        if success:
            logger.info("配置已重置为默认值")
        return success
    
    def get_config_file_path(self) -> str:
        """
        获取配置文件路径
        
        返回:
            str: 配置文件路径
        """
        return str(self.config_file)