"""
Gamma 调节引擎
通过 Windows GDI32 API 调节屏幕 Gamma 值
"""

import ctypes
from ctypes import windll, byref, Structure, c_ushort, c_void_p, POINTER
import logging

logger = logging.getLogger('GammaTool')

# 尝试导入 WMI 用于备用方案
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("WMI 模块未安装,某些功能可能受限")


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
        self._gamma_ramp_supported = False
        self._primary_device_name = None  # 存储支持 Gamma Ramp 的设备名称
        self._check_gamma_ramp_support()
        
        if self._gamma_ramp_supported:
            self._save_default_ramp()
            logger.info("Gamma 引擎初始化完成 (使用 Gamma Ramp API)")
        else:
            logger.warning("=" * 60)
            logger.warning("您的显卡驱动不支持 Gamma Ramp API")
            logger.warning("这是 Windows 10/11 和现代显卡驱动的常见限制")
            logger.warning("建议解决方案:")
            logger.warning("1. 使用显卡控制面板调节亮度/对比度")
            logger.warning("2. 使用 Windows 夜间模式功能")
            logger.warning("3. 尝试更新或回退显卡驱动")
            logger.warning("4. 使用外部显示器调节按钮")
            logger.warning("=" * 60)
    
    def _check_gamma_ramp_support(self):
        """检查系统是否支持 Gamma Ramp API"""
        try:
            # 获取主显示器的设备上下文
            hdc = windll.user32.GetDC(None)
            
            if not hdc:
                error_code = ctypes.get_last_error()
                logger.error(f"无法获取主显示器设备上下文 (错误码: {error_code})")
                return
            
            # 尝试获取当前 Gamma Ramp
            ramp = RAMP()
            success = windll.gdi32.GetDeviceGammaRamp(hdc, byref(ramp))
            windll.user32.ReleaseDC(None, hdc)
            
            # 如果主显示器不支持，尝试枚举所有显示器设备
            if not success:
                logger.info("主显示器不支持 Gamma Ramp，正在检测其他显示设备...")
                self._enumerate_display_devices()
            else:
                self._gamma_ramp_supported = True
                logger.info("✓ 系统支持 Gamma Ramp API")
                
        except Exception as e:
            logger.error(f"检查 Gamma Ramp 支持时出错: {e}", exc_info=True)
    
    def _enumerate_display_devices(self):
        """枚举所有显示设备"""
        try:
            import ctypes.wintypes as wintypes
            
            # 定义 DISPLAY_DEVICE 结构
            class DISPLAY_DEVICE(ctypes.Structure):
                _fields_ = [
                    ('cb', wintypes.DWORD),
                    ('DeviceName', wintypes.WCHAR * 32),
                    ('DeviceString', wintypes.WCHAR * 128),
                    ('StateFlags', wintypes.DWORD),
                    ('DeviceID', wintypes.WCHAR * 128),
                    ('DeviceKey', wintypes.WCHAR * 128)
                ]
            
            device = DISPLAY_DEVICE()
            device.cb = ctypes.sizeof(device)
            
            i = 0
            i = 0
            while windll.user32.EnumDisplayDevicesW(None, i, ctypes.byref(device), 0):
                # 检查是否为已连接的显示器
                DISPLAY_DEVICE_ATTACHED_TO_DESKTOP = 0x00000001
                is_attached = device.StateFlags & DISPLAY_DEVICE_ATTACHED_TO_DESKTOP
                
                # 尝试为此设备创建 DC 并测试 Gamma Ramp
                if is_attached:
                    self._test_device_gamma_support(device.DeviceName, device.DeviceString)
                
                i += 1
                device = DISPLAY_DEVICE()
                device.cb = ctypes.sizeof(device)
        except Exception as e:
            logger.error(f"枚举显示设备失败: {e}", exc_info=True)
    
    def _test_device_gamma_support(self, device_name, device_desc):
        """测试特定设备的 Gamma Ramp 支持"""
        try:
            # 为特定设备创建 DC (CreateDC 在 gdi32 中，不是 user32)
            hdc = windll.gdi32.CreateDCW("DISPLAY", device_name, None, None)
            
            if not hdc:
                return
            
            # 测试 Gamma Ramp
            ramp = RAMP()
            success = windll.gdi32.GetDeviceGammaRamp(hdc, byref(ramp))
            
            if success:
                # 如果找到支持的设备，更新标志
                if not self._gamma_ramp_supported:
                    self._gamma_ramp_supported = True
                    self._primary_device_name = device_name
                    logger.info(f"✓ 找到支持的显示设备: {device_desc} ({device_name})")
            
            windll.gdi32.DeleteDC(hdc)
            
        except Exception as e:
            logger.debug(f"测试设备 {device_name} 失败: {e}")
    
    def _save_default_ramp(self):
        """保存默认 Gamma 值"""
        try:
            # 如果找到了支持的特定设备，使用该设备
            if self._primary_device_name:
                hdc = windll.gdi32.CreateDCW("DISPLAY", self._primary_device_name, None, None)
            else:
                hdc = windll.user32.GetDC(None)
            
            if hdc:
                ramp = RAMP()
                success = windll.gdi32.GetDeviceGammaRamp(hdc, byref(ramp))
                
                if success:
                    self._default_ramp = ramp
                    logger.info("默认 Gamma 值已保存")
                else:
                    error_code = ctypes.get_last_error()
                    logger.error(f"无法获取默认 Gamma 值 (错误码: {error_code})")
                
                # 释放设备上下文
                if self._primary_device_name:
                    windll.gdi32.DeleteDC(hdc)
                else:
                    windll.user32.ReleaseDC(None, hdc)
            else:
                error_code = ctypes.get_last_error()
                logger.error(f"获取设备上下文失败 (错误码: {error_code})")
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
            # 如果找到了支持的特定设备，使用该设备
            if self._primary_device_name:
                hdc = windll.gdi32.CreateDCW("DISPLAY", self._primary_device_name, None, None)
            else:
                hdc = windll.user32.GetDC(None)
            
            if hdc:
                success = windll.gdi32.SetDeviceGammaRamp(hdc, byref(ramp))
                
                if not success:
                    error_code = ctypes.get_last_error()
                    logger.error(f"SetDeviceGammaRamp 失败 (错误码: {error_code})")
                
                # 释放设备上下文
                if self._primary_device_name:
                    windll.gdi32.DeleteDC(hdc)
                else:
                    windll.user32.ReleaseDC(None, hdc)
                    
                return bool(success)
            else:
                error_code = ctypes.get_last_error()
                logger.error(f"获取设备上下文失败 (错误码: {error_code})")
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
        if not self._gamma_ramp_supported:
            logger.warning("无法应用设置: 系统不支持 Gamma Ramp API")
            return False
        
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
    
    def is_supported(self):
        """
        检查 Gamma Ramp API 是否被支持
        
        返回:
            bool: 是否支持
        """
        return self._gamma_ramp_supported
    
    def reset_to_default(self):
        """
        恢复默认设置
        
        返回:
            bool: 是否成功
        """
        if not self._gamma_ramp_supported:
            logger.warning("无法恢复默认设置: 系统不支持 Gamma Ramp API")
            # 重置内部状态
            self.current_brightness = 100
            self.current_contrast = 100
            self.current_grayscale = 0
            self.current_rgb = {'red': 255, 'green': 255, 'blue': 255}
            return False
            
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