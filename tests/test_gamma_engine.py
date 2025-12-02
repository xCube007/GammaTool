"""
测试 Gamma 引擎
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gamma_engine import GammaEngine
import time


def test_gamma_engine():
    """测试 Gamma 引擎基本功能"""
    print("=" * 60)
    print("测试 Gamma 引擎")
    print("=" * 60)
    
    # 创建引擎
    print("\n1. 创建 Gamma 引擎...")
    engine = GammaEngine()
    print("   ✓ 引擎创建成功")
    
    # 测试亮度调节
    print("\n2. 测试亮度调节...")
    print("   设置亮度为 150%")
    engine.set_brightness(150)
    engine.apply_settings()
    print("   ✓ 亮度已设置")
    time.sleep(2)
    
    # 测试对比度调节
    print("\n3. 测试对比度调节...")
    print("   设置对比度为 120%")
    engine.set_contrast(120)
    engine.apply_settings()
    print("   ✓ 对比度已设置")
    time.sleep(2)
    
    # 测试灰度调节
    print("\n4. 测试灰度调节...")
    print("   设置灰度为 50%")
    engine.set_grayscale(50)
    engine.apply_settings()
    print("   ✓ 灰度已设置")
    time.sleep(2)
    
    # 测试 RGB 通道
    print("\n5. 测试 RGB 通道调节...")
    print("   设置红色通道为 200")
    engine.set_rgb(200, 255, 255)
    engine.apply_settings()
    print("   ✓ RGB 通道已设置")
    time.sleep(2)
    
    # 恢复默认
    print("\n6. 恢复默认设置...")
    engine.reset_to_default()
    print("   ✓ 已恢复默认")
    
    # 获取当前设置
    print("\n7. 获取当前设置...")
    settings = engine.get_current_settings()
    print(f"   当前设置: {settings}")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_gamma_engine()
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()