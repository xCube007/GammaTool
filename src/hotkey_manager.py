"""
热键管理器
管理全局热键的注册和响应
"""

import keyboard
from typing import Callable, Dict
import logging

logger = logging.getLogger(__name__)


class HotkeyManager:
    """热键管理器"""
    
    def __init__(self):
        """初始化热键管理器"""
        self._hotkeys: Dict[str, Callable] = {}
        self._is_listening = False
        logger.info("热键管理器初始化完成")
    
    def register_hotkey(self, key_combo: str, callback: Callable, description: str = ""):
        """
        注册热键
        
        参数:
            key_combo: 热键组合，如 'ctrl+alt+up'
            callback: 回调函数
            description: 热键描述
        
        返回:
            bool: 是否成功
        """
        try:
            # 先注销已存在的热键
            if key_combo in self._hotkeys:
                self.unregister_hotkey(key_combo)
            
            # 注册热键
            keyboard.add_hotkey(key_combo, callback, suppress=False)
            self._hotkeys[key_combo] = callback
            
            desc = f" ({description})" if description else ""
            logger.info(f"热键已注册: {key_combo}{desc}")
            return True
        except Exception as e:
            logger.error(f"注册热键失败 [{key_combo}]: {e}")
            return False
    
    def unregister_hotkey(self, key_combo: str):
        """
        注销热键
        
        参数:
            key_combo: 热键组合
        
        返回:
            bool: 是否成功
        """
        try:
            keyboard.remove_hotkey(key_combo)
            if key_combo in self._hotkeys:
                del self._hotkeys[key_combo]
            logger.info(f"热键已注销: {key_combo}")
            return True
        except Exception as e:
            logger.error(f"注销热键失败 [{key_combo}]: {e}")
            return False
    
    def unregister_all(self):
        """
        注销所有热键
        
        返回:
            int: 注销的热键数量
        """
        count = 0
        for key_combo in list(self._hotkeys.keys()):
            if self.unregister_hotkey(key_combo):
                count += 1
        logger.info(f"已注销 {count} 个热键")
        return count
    
    def start_listening(self):
        """开始监听热键"""
        self._is_listening = True
        logger.info("热键监听已启动")
    
    def stop_listening(self):
        """停止监听热键"""
        self._is_listening = False
        self.unregister_all()
        logger.info("热键监听已停止")
    
    def is_listening(self) -> bool:
        """
        检查是否正在监听
        
        返回:
            bool: 是否正在监听
        """
        return self._is_listening
    
    def get_registered_hotkeys(self) -> Dict[str, Callable]:
        """
        获取已注册的热键
        
        返回:
            dict: 热键字典
        """
        return self._hotkeys.copy()
    
    def is_hotkey_registered(self, key_combo: str) -> bool:
        """
        检查热键是否已注册
        
        参数:
            key_combo: 热键组合
        
        返回:
            bool: 是否已注册
        """
        return key_combo in self._hotkeys