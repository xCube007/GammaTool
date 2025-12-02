"""
配置预设管理器
管理多个显示配置预设
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PresetManager:
    """配置预设管理器"""
    
    def __init__(self, presets_file: str = "config/presets.json"):
        """
        初始化预设管理器
        
        参数:
            presets_file: 预设文件路径
        """
        self.presets_file = Path(presets_file)
        self.presets: Dict[str, Dict] = {}
        self.current_preset: Optional[str] = None
        self._load_presets()
        logger.info("配置预设管理器初始化完成")
    
    def _load_presets(self):
        """从文件加载预设"""
        try:
            if self.presets_file.exists():
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.presets = data.get('presets', {})
                    self.current_preset = data.get('current_preset', None)
                logger.info(f"已加载 {len(self.presets)} 个预设")
            else:
                # 创建默认预设
                self._create_default_presets()
                self._save_presets()
                logger.info("已创建默认预设")
        except Exception as e:
            logger.error(f"加载预设失败: {e}")
            self._create_default_presets()
    
    def _create_default_presets(self):
        """创建默认预设"""
        self.presets = {
            "默认": {
                "brightness": 100,
                "contrast": 100,
                "grayscale": 0,
                "rgb": {"red": 255, "green": 255, "blue": 255},
                "hotkey": ""
            },
            "夜间模式": {
                "brightness": 80,
                "contrast": 90,
                "grayscale": 0,
                "rgb": {"red": 255, "green": 200, "blue": 150},
                "hotkey": ""
            },
            "阅读模式": {
                "brightness": 110,
                "contrast": 105,
                "grayscale": 0,
                "rgb": {"red": 255, "green": 245, "blue": 230},
                "hotkey": ""
            }
        }
        self.current_preset = "默认"
    
    def _save_presets(self):
        """保存预设到文件"""
        try:
            # 确保目录存在
            self.presets_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "current_preset": self.current_preset,
                "presets": self.presets
            }
            
            with open(self.presets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug("预设已保存")
        except Exception as e:
            logger.error(f"保存预设失败: {e}")
    
    def save_preset(self, name: str, settings: Dict) -> bool:
        """
        保存当前设置为预设
        
        参数:
            name: 预设名称
            settings: 设置字典，包含 brightness, contrast, grayscale, rgb, hotkey
        
        返回:
            bool: 是否成功
        """
        try:
            # 保留原有的快捷键（如果存在）
            existing_hotkey = ""
            if name in self.presets:
                existing_hotkey = self.presets[name].get('hotkey', '')
            
            self.presets[name] = {
                "brightness": settings.get('brightness', 100),
                "contrast": settings.get('contrast', 100),
                "grayscale": settings.get('grayscale', 0),
                "rgb": settings.get('rgb', {"red": 255, "green": 255, "blue": 255}),
                "hotkey": settings.get('hotkey', existing_hotkey)
            }
            self._save_presets()
            logger.info(f"预设已保存: {name}")
            return True
        except Exception as e:
            logger.error(f"保存预设失败 [{name}]: {e}")
            return False
    
    def load_preset(self, name: str) -> Optional[Dict]:
        """
        加载预设
        
        参数:
            name: 预设名称
        
        返回:
            dict: 预设设置，如果不存在返回 None
        """
        if name in self.presets:
            self.current_preset = name
            self._save_presets()
            logger.info(f"预设已加载: {name}")
            return self.presets[name].copy()
        else:
            logger.warning(f"预设不存在: {name}")
            return None
    
    def delete_preset(self, name: str) -> bool:
        """
        删除预设
        
        参数:
            name: 预设名称
        
        返回:
            bool: 是否成功
        """
        if name in self.presets:
            del self.presets[name]
            if self.current_preset == name:
                self.current_preset = None
            self._save_presets()
            logger.info(f"预设已删除: {name}")
            return True
        else:
            logger.warning(f"预设不存在: {name}")
            return False
    
    def get_preset_names(self) -> List[str]:
        """
        获取所有预设名称
        
        返回:
            list: 预设名称列表
        """
        return list(self.presets.keys())
    
    def get_current_preset_name(self) -> Optional[str]:
        """
        获取当前预设名称
        
        返回:
            str: 当前预设名称，如果没有返回 None
        """
        return self.current_preset
    
    def switch_to_next_preset(self) -> Optional[Dict]:
        """
        切换到下一个预设
        
        返回:
            dict: 下一个预设的设置，如果没有预设返回 None
        """
        preset_names = self.get_preset_names()
        if not preset_names:
            return None
        
        if self.current_preset is None or self.current_preset not in preset_names:
            # 如果当前没有预设或预设不存在，切换到第一个
            next_name = preset_names[0]
        else:
            # 切换到下一个预设
            current_index = preset_names.index(self.current_preset)
            next_index = (current_index + 1) % len(preset_names)
            next_name = preset_names[next_index]
        
        return self.load_preset(next_name)
    
    def set_preset_hotkey(self, name: str, hotkey: str) -> bool:
        """
        设置预设的快捷键
        
        参数:
            name: 预设名称
            hotkey: 快捷键字符串
        
        返回:
            bool: 是否成功
        """
        if name in self.presets:
            self.presets[name]['hotkey'] = hotkey
            self._save_presets()
            logger.info(f"预设 '{name}' 的快捷键已设置为: {hotkey}")
            return True
        else:
            logger.warning(f"预设不存在: {name}")
            return False
    
    def get_preset_hotkey(self, name: str) -> str:
        """
        获取预设的快捷键
        
        参数:
            name: 预设名称
        
        返回:
            str: 快捷键字符串，如果不存在返回空字符串
        """
        if name in self.presets:
            return self.presets[name].get('hotkey', '')
        return ''
    
    def get_all_hotkeys(self) -> Dict[str, str]:
        """
        获取所有预设的快捷键映射
        
        返回:
            dict: {预设名称: 快捷键} 的字典
        """
        hotkeys = {}
        for name, preset in self.presets.items():
            hotkey = preset.get('hotkey', '')
            if hotkey:
                hotkeys[name] = hotkey
        return hotkeys