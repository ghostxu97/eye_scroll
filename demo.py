#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复后的眼球追踪控制演示脚本
"""

import cv2
import time
from eye_tracker import EyeTracker
from screen_controller import ScreenController

def demo_eye_tracking():
    """演示眼球追踪功能"""
    print("=== 眼球追踪演示 ===")
    print("这个演示将展示如何检测眼球位置")
    print("请确保摄像头可用且面部在视野内")
    print("按 'q' 键退出演示")
    print()
    
    # 创建眼球追踪器
    tracker = EyeTracker()
    print("✓ 眼球追踪器已创建")
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ 无法打开摄像头")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("✓ 摄像头初始化成功")
    print("请将面部对准摄像头，演示将开始...")
    print()
    
    # 等待用户准备
    time.sleep(3)
    
    print("开始实时眼球追踪演示...")
    print("请尝试注视屏幕的不同位置：")
    print("- 向上看（注视屏幕顶部）")
    print("- 向下看（注视屏幕底部）")
    print("- 平视前方（注视屏幕中间）")
    print()
    
    start_time = time.time()
    last_position = None
    position_count = {'top': 0, 'center': 0, 'bottom': 0}
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧")
            break
            
        # 翻转帧（镜像显示）
        frame = cv2.flip(frame, 1)
        
        # 检测眼球位置
        eye_result = tracker.get_eye_position(frame)
        
        if eye_result:
            position, confidence = eye_result
            
            # 统计各位置出现次数
            if position in position_count:
                position_count[position] += 1
            
            # 显示检测结果
            if position != last_position:
                print(f"检测到注视位置: {position} (置信度: {confidence:.2f})")
                last_position = position
            
            # 绘制追踪信息
            frame = tracker.draw_eye_tracking(frame, position, confidence)
            
            # 显示统计信息
            cv2.putText(frame, f"Top: {position_count['top']}", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Center: {position_count['center']}", (10, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Bottom: {position_count['bottom']}", (10, 210), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "未检测到面部", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示预览窗口
        cv2.imshow('眼球追踪演示', frame)
        
        # 检查退出条件
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        # 演示持续30秒
        if time.time() - start_time > 30:
            print("演示时间到！")
            break
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    
    # 显示统计结果
    print("\n=== 演示统计结果 ===")
    total_frames = sum(position_count.values())
    if total_frames > 0:
        print(f"总检测帧数: {total_frames}")
        print(f"顶部注视: {position_count['top']} 帧 ({position_count['top']/total_frames*100:.1f}%)")
        print(f"中间注视: {position_count['center']} 帧 ({position_count['center']/total_frames*100:.1f}%)")
        print(f"底部注视: {position_count['bottom']} 帧 ({position_count['bottom']/total_frames*100:.1f}%)")
    
    print("✓ 眼球追踪演示完成")
    print()
    return True

def demo_screen_control():
    """演示屏幕控制功能"""
    print("=== 屏幕控制演示 ===")
    print("这个演示将展示如何控制屏幕滚动")
    print("注意：将执行实际的滚动操作")
    print()
    
    # 创建屏幕控制器
    controller = ScreenController()
    print("✓ 屏幕控制器已创建")
    
    # 设置较慢的滚动速度用于演示
    controller.set_scroll_speed(2)
    controller.set_scroll_interval(0.2)
    print("✓ 滚动参数已设置")
    
    # 询问用户是否继续
    response = input("是否执行滚动演示？(y/n): ").lower().strip()
    
    if response == 'y':
        print("开始滚动演示...")
        
        # 向上滚动
        print("向上滚动...")
        controller.start_scroll_up()
        time.sleep(2)
        controller.stop_all_scrolling()
        
        time.sleep(1)
        
        # 向下滚动
        print("向下滚动...")
        controller.start_scroll_down()
        time.sleep(2)
        controller.stop_all_scrolling()
        
        print("✓ 滚动演示完成")
    else:
        print("跳过滚动演示")
    
    print()

def demo_integration():
    """演示集成功能"""
    print("=== 集成功能演示 ===")
    print("这个演示将展示完整的控制流程")
    print("请确保摄像头可用且面部在视野内")
    print("按 'q' 键退出演示")
    print()
    
    # 创建组件
    tracker = EyeTracker()
    controller = ScreenController()
    
    print("✓ 组件创建完成")
    
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ 无法打开摄像头")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("✓ 摄像头初始化成功")
    
    # 设置控制参数
    controller.set_scroll_speed(3)
    controller.set_scroll_interval(0.1)
    
    print("开始集成演示...")
    print("请尝试注视屏幕不同位置来控制滚动：")
    print("- 注视顶部：向上滚动")
    print("- 注视底部：向下滚动")
    print("- 注视中间：停止滚动")
    print()
    
    # 等待用户准备
    time.sleep(3)
    
    current_action = None
    last_position = None
    position_hold_time = 0.5
    position_start_time = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        eye_result = tracker.get_eye_position(frame)
        
        if eye_result:
            position, confidence = eye_result
            current_time = time.time()
            
            # 位置变化检测
            if position != last_position:
                last_position = position
                position_start_time = current_time
                current_action = None
            
            # 位置保持时间检测
            if current_time - position_start_time >= position_hold_time:
                if position == 'top' and current_action != 'scroll_up':
                    print("开始向上滚动")
                    controller.start_scroll_up()
                    current_action = 'scroll_up'
                elif position == 'bottom' and current_action != 'scroll_down':
                    print("开始向下滚动")
                    controller.start_scroll_down()
                    current_action = 'scroll_down'
                elif position == 'center' and current_action != 'stop':
                    print("停止滚动")
                    controller.stop_all_scrolling()
                    current_action = 'stop'
            
            # 绘制追踪信息
            frame = tracker.draw_eye_tracking(frame, position, confidence)
            
            # 显示当前动作
            action_text = f"当前动作: {current_action if current_action else '无'}"
            cv2.putText(frame, action_text, (10, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            # 没有检测到面部，停止滚动
            if current_action in ['scroll_up', 'scroll_down']:
                print("未检测到面部，停止滚动")
                controller.stop_all_scrolling()
                current_action = 'stop'
            
            cv2.putText(frame, "未检测到面部", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示预览窗口
        cv2.imshow('集成功能演示', frame)
        
        # 检查退出条件
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    # 清理资源
    cap.release()
    cv2.destroyAllWindows()
    controller.stop_all_scrolling()
    
    print("✓ 集成演示完成")
    print()

def main():
    """主演示函数"""
    print("🎯 眼球追踪控制Mac屏幕滚动 - 功能演示")
    print("=" * 50)
    print()
    
    try:
        # 运行各个演示
        if demo_eye_tracking():
            demo_screen_control()
            demo_integration()
        
        print("🎉 所有演示完成！")
        print()
        print("现在您可以运行主程序来体验完整的眼球追踪控制功能：")
        print("  python3 main.py")
        print("  或者")
        print("  ./run.sh")
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        print("请检查环境配置")

if __name__ == "__main__":
    main()
