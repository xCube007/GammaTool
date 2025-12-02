"""
工具函数模块
提供通用的工具函数
"""

import os
import sys
import winreg
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


def get_resource_path(relative_path):
    """
    获取资源文件路径（支持打包后的路径）
    
    参数:
        relative_path: 相对路径
    
    返回:
        str: 资源文件的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def set_auto_start(enable: bool, app_name: str = "GammaTool", app_path: str = None):
    """
    设置开机自启动
    
    参数:
        enable: 是否启用
        app_name: 应用名称
        app_path: 应用路径，如果为 None 则使用当前程序路径
    
    返回:
        bool: 是否成功
    """
    if app_path is None:
        app_path = sys.executable
    
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE
        )
        
        if enable:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            logging.info(f"已启用开机自启动: {app_path}")
        else:
            try:
                winreg.DeleteValue(key, app_name)
                logging.info("已禁用开机自启动")
            except FileNotFoundError:
                pass
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        logging.error(f"设置开机自启动失败: {e}")
        return False


def clamp(value, min_value, max_value):
    """
    限制数值范围
    
    参数:
        value: 要限制的值
        min_value: 最小值
        max_value: 最大值
    
    返回:
        限制后的值
    """
    return max(min_value, min(max_value, value))


def setup_logging(log_dir: Path = None, log_level=logging.INFO):
    """
    设置日志系统
    
    参数:
        log_dir: 日志目录，如果为 None 则使用默认目录
        log_level: 日志级别
    
    返回:
        Logger: 日志记录器
    """
    if log_dir is None:
        appdata = os.getenv('APPDATA')
        if appdata:
            log_dir = Path(appdata) / "GammaTool" / "logs"
        else:
            log_dir = Path.home() / ".gammatool" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gammatool.log"
    
    # 创建日志记录器
    logger = logging.getLogger('GammaTool')
    logger.setLevel(logging.DEBUG)  # 设置为 DEBUG 级别以显示所有日志
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 文件处理器（轮转日志）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,  # 1MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件记录所有 DEBUG 级别日志
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只显示 INFO 及以上级别
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("=" * 50)
    logger.info("GammaTool 日志系统已初始化")
    logger.info(f"日志文件: {log_file}")
    logger.info("=" * 50)
    
    return logger


def format_hotkey(hotkey: str) -> str:
    """
    格式化热键字符串
    
    参数:
        hotkey: 热键字符串，如 'ctrl+alt+up'
    
    返回:
        str: 格式化后的热键字符串，如 'Ctrl+Alt+Up'
    """
    parts = hotkey.split('+')
    formatted_parts = []
    
    for part in parts:
        part = part.strip().lower()
        if part == 'ctrl':
            formatted_parts.append('Ctrl')
        elif part == 'alt':
            formatted_parts.append('Alt')
        elif part == 'shift':
            formatted_parts.append('Shift')
        elif part == 'win' or part == 'meta':
            formatted_parts.append('Win')
        else:
            formatted_parts.append(part.capitalize())
    
    return '+'.join(formatted_parts)


def validate_hotkey(hotkey: str) -> bool:
    """
    验证热键字符串是否有效
    
    参数:
        hotkey: 热键字符串
    
    返回:
        bool: 是否有效
    """
    if not hotkey or not isinstance(hotkey, str):
        return False
    
    parts = hotkey.split('+')
    if len(parts) < 2:
        return False
    
    valid_modifiers = {'ctrl', 'alt', 'shift', 'win', 'meta'}
    has_modifier = False
    
    for part in parts[:-1]:
        if part.strip().lower() in valid_modifiers:
            has_modifier = True
        else:
            return False
    
    return has_modifier and len(parts[-1].strip()) > 0