"""
Gamma 调节引擎
通过 Windows GDI32 API 调节屏幕 Gamma 值
"""

import ctypes
from ctypes import windll, byref, Structure, c_ushort
import logging

logger = logging.getLogger(__name__)


class RAMP(Structure):
    """Gamma 斜坡数组结构体"""
    _fields_ = [
        ('Red', c_ushort * 256),
        ('Green', c_ushort * 256),
        ('Blue', c_ushort * 256)
    ]


class GammaEngine:
    """Gamma 调节引擎"""
    
    def __init__(self):
        """初始化 Gamma 引擎"""
        self.current_brightness = 100
        self.current_contrast = 100
        self.current_grayscale = 0
        self.current_rgb = {'red': 255, 'green': 255, 'blue': 255}
        self._default_ramp = None
        self._save_default_ramp()
        logger.info("Gamma 引擎初始化完成")
    
    def _save_default_ramp(self):
        """保存默认 Gamma 值"""
        try:
            hdc = windll.user32.GetDC(None)
            if hdc:
                ramp = RAMP()
                success = windll.gdi32.GetDeviceGammaRamp(hdc, byref(ramp))
                if success:
                    self._default_ramp = ramp
                    logger.info("默认 Gamma 值已保存")
                else:
                    logger.warning("无法获取默认 Gamma 值")
                windll.user32.ReleaseDC(None, hdc)
        except Exception as e:
            logger.error(f"保存默认 Gamma 值失败: {e}")
    
    def _calculate_gamma_ramp(self, brightness, contrast, grayscale, r, g, b):
        """
        计算 Gamma 斜坡数组
        
        参数:
            brightness: 亮度 (0-200, 默认100)
            contrast: 对比度 (0-200, 默认100)
            grayscale: 灰度 (0-100, 默认0)
            r, g, b: RGB 通道值 (0-255, 默认255)
        
        返回:
            RAMP 结构体
        """
        ramp = RAMP()
        
        # 归一化参数
        brightness_factor = brightness / 100.0
        contrast_factor = contrast / 100.0
        grayscale_factor = grayscale / 100.0
        
        for i in range(256):
            # 1. 基础值 (0.0 - 1.0)
            value = i / 255.0
            
            # 2. 应用对比度 (围绕 0.5 中心点调节)
            value = (value - 0.5) * contrast_factor + 0.5
            
            # 3. 应用亮度
            value = value * brightness_factor
            
            # 4. 限制范围 [0.0, 1.0]
            value = max(0.0, min(1.0, value))
            
            # 5. 转换为 16 位整数 (0-65535)
            base_value = int(value * 65535)
            
            # 6. 应用灰度效果
            if grayscale_factor > 0:
                # 计算灰度值
                gray_value = base_value * (1 - grayscale_factor)
                
                # 应用 RGB 通道
                ramp.Red[i] = int(gray_value * (r / 255.0))
                ramp.Green[i] = int(gray_value * (g / 255.0))
                ramp.Blue[i] = int(gray_value * (b / 255.0))
            else:
                # 直接应用 RGB 通道
                ramp.Red[i] = int(base_value * (r / 255.0))
                ramp.Green[i] = int(base_value * (g / 255.0))
                ramp.Blue[i] = int(base_value * (b / 255.0))
        
        return ramp
    
    def _apply_gamma_ramp(self, ramp):
        """
        应用 Gamma 斜坡数组
        
        参数:
            ramp: RAMP 结构体
        
        返回:
            bool: 是否成功
        """
        try:
            hdc = windll.user32.GetDC(None)
            if hdc:
                success = windll.gdi32.SetDeviceGammaRamp(hdc, byref(ramp))
                windll.user32.ReleaseDC(None, hdc)
                return bool(success)
            return False
        except Exception as e:
            logger.error(f"应用 Gamma 值失败: {e}")
            return False
    
    def set_brightness(self, value):
        """
        设置亮度
        
        参数:
            value: 亮度值 (0-200)
        """
        self.current_brightness = max(0, min(200, value))
        logger.debug(f"亮度设置为: {self.current_brightness}")
    
    def set_contrast(self, value):
        """
        设置对比度
        
        参数:
            value: 对比度值 (0-200)
        """
        self.current_contrast = max(0, min(200, value))
        logger.debug(f"对比度设置为: {self.current_contrast}")
    
    def set_grayscale(self, value):
        """
        设置灰度
        
        参数:
            value: 灰度值 (0-100)
        """
        self.current_grayscale = max(0, min(100, value))
        logger.debug(f"灰度设置为: {self.current_grayscale}")
    
    def set_rgb(self, r, g, b):
        """
        设置 RGB 通道
        
        参数:
            r: 红色通道 (0-255)
            g: 绿色通道 (0-255)
            b: 蓝色通道 (0-255)
        """
        self.current_rgb = {
            'red': max(0, min(255, r)),
            'green': max(0, min(255, g)),
            'blue': max(0, min(255, b))
        }
        logger.debug(f"RGB 设置为: {self.current_rgb}")
    
    def apply_settings(self):
        """
        应用当前设置
        
        返回:
            bool: 是否成功
        """
        ramp = self._calculate_gamma_ramp(
            self.current_brightness,
            self.current_contrast,
            self.current_grayscale,
            self.current_rgb['red'],
            self.current_rgb['green'],
            self.current_rgb['blue']
        )
        
        success = self._apply_gamma_ramp(ramp)
        if success:
            logger.info("Gamma 设置已应用")
        else:
            logger.error("应用 Gamma 设置失败")
        return success
    
    def reset_to_default(self):
        """
        恢复默认设置
        
        返回:
            bool: 是否成功
        """
        if self._default_ramp:
            success = self._apply_gamma_ramp(self._default_ramp)
            if success:
                self.current_brightness = 100
                self.current_contrast = 100
                self.current_grayscale = 0
                self.current_rgb = {'red': 255, 'green': 255, 'blue': 255}
                logger.info("已恢复默认 Gamma 设置")
            return success
        else:
            logger.warning("没有保存的默认 Gamma 值")
            return False
    
    def get_current_settings(self):
        """
        获取当前设置
        
        返回:
            dict: 当前设置
        """
        return {
            'brightness': self.current_brightness,
            'contrast': self.current_contrast,
            'grayscale': self.current_grayscale,
            'rgb': self.current_rgb.copy()
        }