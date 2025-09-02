#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块测试脚本
"""

import sys
import time

def test_eye_tracker():
    """测试眼球追踪模块"""
    print("测试眼球追踪模块...")
    try:
        from eye_tracker import EyeTracker
        tracker = EyeTracker()
        print("✓ 眼球追踪器创建成功")
        
        # 测试设置屏幕尺寸
        tracker.set_screen_dimensions(1920, 1080)
        print("✓ 屏幕尺寸设置成功")
        
        return True
    except Exception as e:
        print(f"✗ 眼球追踪器测试失败: {e}")
        return False

def test_screen_controller():
    """测试屏幕控制模块"""
    print("测试屏幕控制模块...")
    try:
        from screen_controller import ScreenController
        controller = ScreenController()
        print("✓ 屏幕控制器创建成功")
        
        # 测试获取状态
        status = controller.get_scroll_status()
        print(f"✓ 滚动状态获取成功: {status}")
        
        # 测试设置参数
        controller.set_scroll_speed(5)
        controller.set_scroll_interval(0.1)
        print("✓ 参数设置成功")
        
        return True
    except Exception as e:
        print(f"✗ 屏幕控制器测试失败: {e}")
        return False

def test_camera():
    """测试摄像头"""
    print("测试摄像头...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ 摄像头可用")
            ret, frame = cap.read()
            if ret:
                print(f"✓ 摄像头读取成功，帧大小: {frame.shape}")
            else:
                print("⚠ 摄像头读取失败")
            cap.release()
            return True
        else:
            print("✗ 摄像头不可用")
            return False
    except Exception as e:
        print(f"✗ 摄像头测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("测试依赖包...")
    dependencies = [
        ('cv2', 'OpenCV'),
        ('mediapipe', 'MediaPipe'),
        ('numpy', 'NumPy'),
        ('pyautogui', 'PyAutoGUI'),
        ('pynput', 'pynput')
    ]
    
    all_ok = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name} 导入成功")
        except ImportError:
            print(f"✗ {name} 导入失败")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("=== 模块功能测试 ===")
    print()
    
    tests = [
        ("依赖包", test_dependencies),
        ("摄像头", test_camera),
        ("眼球追踪器", test_eye_tracker),
        ("屏幕控制器", test_screen_controller)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"【{test_name}】")
        result = test_func()
        results.append((test_name, result))
        print()
    
    # 显示测试结果
    print("=== 测试结果汇总 ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以运行主程序了。")
        return True
    else:
        print("⚠ 部分测试失败，请检查环境配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
