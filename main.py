#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import threading
import time
import config
from eye_tracker import EyeTracker
from screen_controller import ScreenController

class EyeScrollController:
    def __init__(self):
        self.eye_tracker = EyeTracker(debug_mode=config.DEBUG_MODE)
        self.screen_controller = ScreenController()
        
        # 配置屏幕控制器参数
        self.screen_controller.set_scroll_speed(config.SCROLL_SPEED)
        self.screen_controller.set_scroll_interval(config.SCROLL_INTERVAL)
        self.screen_controller.adaptive_speed = config.ADAPTIVE_SPEED
        self.screen_controller.max_scroll_speed = config.MAX_SCROLL_SPEED
        self.screen_controller.acceleration = config.ACCELERATION
        
        # 配置眼球追踪器参数
        self.eye_tracker.top_threshold = config.TOP_THRESHOLD
        self.eye_tracker.bottom_threshold = config.BOTTOM_THRESHOLD
        
        self.cap = None
        self.running = False
        self.show_preview = True  # 始终显示预览窗口，以便查看注视点
        self.gaze_threshold = config.GAZE_THRESHOLD
        self.position_hold_time = config.POSITION_HOLD_TIME
        self.current_position = 'center'
        self.position_start_time = 0
        self.last_action = None
        
        # 眼睛动作趋势跟踪
        self.position_history = []  # 记录最近的眼睛位置历史
        self.history_max_length = 10  # 历史记录最大长度
        self.continuous_scroll = False  # 是否处于连续滚动状态
        self.last_trend_action = None  # 最后一次基于趋势的动作
        self.eye_movement_speed = 1  # 眼球运动速度，默认为1
        
    def initialize_camera(self):
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("错误：无法打开摄像头")
                return False
            
            # 使用配置文件中的摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
            
            # 获取屏幕尺寸并设置到眼球追踪器
            import pyautogui
            screen_width, screen_height = pyautogui.size()
            self.eye_tracker.set_screen_dimensions(screen_width, screen_height)
            
            print(f"摄像头初始化成功 ({config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}@{config.CAMERA_FPS}fps)")
            print(f"屏幕尺寸: {screen_width}x{screen_height}")
            return True
        except Exception as e:
            print(f"摄像头初始化失败: {e}")
            return False
            
    def start(self):
        print("启动眼球追踪控制...")
        if not self.initialize_camera():
            return
        self.running = True
        print("眼球追踪控制已启动")
        print("按 'q' 键退出，按 's' 键切换预览显示")
        self.main_loop()
        
    def main_loop(self):
        frame_count = 0
        start_time = time.time()
        fps = 0
        
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    print("无法读取摄像头帧")
                    break
                    
                # 水平翻转图像，使其更直观
                frame = cv2.flip(frame, 1)
                
                # 获取眼球位置
                eye_result = self.eye_tracker.get_eye_position(frame)
                
                # 处理眼球位置
                if eye_result:
                    position, confidence = eye_result
                    self.process_eye_position(position, confidence)
                    
                    # 在调试模式下输出信息
                    if config.DEBUG_MODE and frame_count % 10 == 0:  # 每10帧输出一次
                        scroll_status = self.screen_controller.get_scroll_status()
                        print(f"Position: {position}, Confidence: {confidence:.2f}, Speed: {scroll_status['current_speed']:.1f}")
                    
                    if self.show_preview:
                        frame = self.eye_tracker.draw_eye_tracking(frame, position, confidence)
                else:
                    # 眼球检测失败（可能是闭眼或未检测到眼睛）
                    if config.DEBUG_MODE and frame_count % 10 == 0:
                        print("Eyes not detected or closed")
                    
                    # 停止滚动（如果有）
                    self.stop_scrolling_if_needed()
                    
                    # 在预览窗口中显示默认中心点
                    if self.show_preview:
                        frame = self.eye_tracker.draw_eye_tracking(frame)  # 不传递参数，使用默认值
                
                # 计算并显示FPS
                frame_count += 1
                if frame_count % 30 == 0:  # 每30帧更新一次FPS
                    end_time = time.time()
                    fps = 30 / (end_time - start_time)
                    start_time = end_time
                
                # 显示预览窗口
                if self.show_preview:
                    # 添加FPS和控制信息
                    cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 120, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    # 显示控制提示
                    cv2.putText(frame, "Press 'q' to quit, 's' to toggle preview, 'c' to calibrate", (10, frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # 如果在校准模式，显示提示和中心十字准心
                    if self.eye_tracker.calibration_mode:
                        cv2.putText(frame, "校准模式 - 请注视屏幕中心", (10, 60), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # 在屏幕中心绘制十字准心
                        h, w = frame.shape[:2]
                        cv2.line(frame, (w//2-20, h//2), (w//2+20, h//2), (0, 0, 255), 2)
                        cv2.line(frame, (w//2, h//2-20), (w//2, h//2+20), (0, 0, 255), 2)
                    
                    cv2.imshow(config.PREVIEW_WINDOW_NAME, frame)
                
                # 处理键盘输入
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.show_preview = not self.show_preview
                    if not self.show_preview:
                        cv2.destroyAllWindows()
                    else:
                        print("已启用预览窗口")
                elif key == ord('c'):
                    print("开始校准...")
                    self.eye_tracker.start_calibration()
                    print("请注视屏幕中心5秒钟...")
                    time.sleep(0.5)  # 防止重复触发
            except Exception as e:
                print(f"主循环出错: {e}")
                if config.DEBUG_MODE:
                    import traceback
                    traceback.print_exc()
                break
        
        self.cleanup()
        
    def process_eye_position(self, position, confidence):
        current_time = time.time()
        if confidence < self.gaze_threshold:
            return
            
        # 记录位置变化
        if position != self.current_position:
            self.current_position = position
            self.position_start_time = current_time
            
        # 添加当前位置到历史记录
        self.position_history.append((position, current_time))
        
        # 保持历史记录在指定长度内
        if len(self.position_history) > self.history_max_length:
            self.position_history.pop(0)
        
        # 计算眼球运动速度
        self.eye_movement_speed = self._calculate_eye_movement_speed()
        
        # 分析眼睛动作趋势
        self._analyze_eye_movement_trend()
            
    def _calculate_eye_movement_speed(self):
        """计算眼球运动速度
        
        基于最近几个位置变化的频率来计算速度
        返回值范围：1-10，数值越大表示眼球运动越快
        """
        if len(self.position_history) < 3:
            return 1  # 默认最低速度
            
        # 计算最近1秒内的位置变化次数
        current_time = time.time()
        recent_changes = 0
        last_position = None
        
        for position, timestamp in reversed(self.position_history):
            if current_time - timestamp > 1.0:  # 只看最近1秒
                break
            if last_position is not None and position != last_position:
                recent_changes += 1
            last_position = position
            
        # 将变化次数映射到速度范围1-10
        # 0-1次变化：速度1-2
        # 2-3次变化：速度3-5  
        # 4-5次变化：速度6-8
        # 6次以上变化：速度9-10
        if recent_changes <= 1:
            speed = 1 + recent_changes
        elif recent_changes <= 3:
            speed = 3 + (recent_changes - 2)
        elif recent_changes <= 5:
            speed = 6 + (recent_changes - 4)
        else:
            speed = min(10, 9 + (recent_changes - 6) * 0.5)
            
        return int(speed)
    
    def _analyze_eye_movement_trend(self):
        """分析眼睛动作趋势，根据趋势控制滚动
        
        根据用户需求调整眼球动作趋势分析逻辑：
        - 向下看一下再向上看一下则往上滚动一次
        - 向下看然后盯住不动则一直向上滚动
        - 向上看一下再向下看一下则往下滚动一次
        - 向上看然后盯住不动则一直向下滚动
        """
        if len(self.position_history) < 3:  # 至少需要3个样本才能分析趋势
            return
        
        # 获取最近的几个位置记录
        recent_positions = [item[0] for item in self.position_history[-3:]]
        current_position = recent_positions[-1]
        
        # 检测向下看一下再向上看一下的模式（触发向下滚动一次）
        if self._detect_pattern(recent_positions, ['bottom', 'top']) and not self.continuous_scroll:
            if config.DEBUG_MODE:
                print("检测到向下看再向上看的模式 - 向下滚动一次")
            self.start_scroll_down()
            # 滚动一次后停止
            threading.Timer(0.5, self.stop_scrolling_if_needed).start()
            self.last_trend_action = 'scroll_down_once'
            return
            
        # 检测向上看一下再向下看一下的模式（触发向上滚动一次）
        if self._detect_pattern(recent_positions, ['top', 'bottom']) and not self.continuous_scroll:
            if config.DEBUG_MODE:
                print("检测到向上看再向下看的模式 - 向上滚动一次")
            self.start_scroll_up()
            # 滚动一次后停止
            threading.Timer(0.5, self.stop_scrolling_if_needed).start()
            self.last_trend_action = 'scroll_down_once'
            return
        
        # 检测持续向下看的模式（触发持续向下滚动）
        if self._detect_continuous_gaze(recent_positions, 'bottom', 2):  # 降低连续样本要求，提高灵敏度
            if self.last_trend_action != 'continuous_scroll_down':
                if config.DEBUG_MODE:
                    print(f"检测到持续向下看 - 开始持续向下滚动 (速度: {self.eye_movement_speed})")
                self.start_scroll_down(self.eye_movement_speed)
                self.continuous_scroll = True
                self.last_trend_action = 'continuous_scroll_down'
            else:
                # 更新滚动速度
                self.screen_controller.update_scroll_speed(self.eye_movement_speed)
            return
            
        # 检测持续向上看的模式（触发持续向上滚动）
        if self._detect_continuous_gaze(recent_positions, 'top', 2):  # 降低连续样本要求，提高灵敏度
            if self.last_trend_action != 'continuous_scroll_up':
                if config.DEBUG_MODE:
                    print(f"检测到持续向上看 - 开始持续向上滚动 (速度: {self.eye_movement_speed})")
                self.start_scroll_up(self.eye_movement_speed)
                self.continuous_scroll = True
                self.last_trend_action = 'continuous_scroll_up'
            else:
                # 更新滚动速度
                self.screen_controller.update_scroll_speed(self.eye_movement_speed)
            return
            
        # 如果注视回到中心，停止滚动
        if current_position == 'center' and self.continuous_scroll:
            if config.DEBUG_MODE:
                print("注视回到中心 - 停止滚动")
            self.stop_scrolling_if_needed()
            self.continuous_scroll = False
            self.last_trend_action = 'stop'
            
    def _detect_pattern(self, positions, pattern):
        """检测位置序列中是否包含指定模式
        
        灵活检测眼球运动模式：
        - 检测从一个位置到另一个位置的转换
        - 允许中间有少量噪声，提高检测的稳定性
        """
        # 对于短序列，使用严格匹配
        if len(positions) <= 3:
            # 查找子序列
            for i in range(len(positions) - len(pattern) + 1):
                match = True
                for j in range(len(pattern)):
                    if positions[i+j] != pattern[j]:
                        match = False
                        break
                if match:
                    return True
            return False
        
        # 对于较长序列，使用更灵活的匹配
        # 特别关注序列的最后几个元素，这些通常是最新的眼球位置
        if len(pattern) == 2 and pattern[0] in ['top', 'bottom'] and pattern[1] == 'center':
            # 检查是否有从特定位置回到中心的模式
            # 例如：从底部回到中心，或从顶部回到中心
            target_pos = pattern[0]  # 'top' 或 'bottom'
            
            # 检查最近的3个位置中是否包含目标位置和中心位置
            recent = positions[-3:]
            has_target = target_pos in recent
            has_center = 'center' in recent
            
            # 如果最后一个位置是中心，且之前有目标位置，则认为匹配成功
            if has_target and has_center and positions[-1] == 'center':
                # 确保目标位置在中心位置之前出现
                target_idx = len(positions) - 1 - recent[::-1].index(target_pos)
                center_idx = len(positions) - 1
                if target_idx < center_idx:
                    return True
        
        # 默认使用原始的严格匹配
        for i in range(len(positions) - len(pattern) + 1):
            match = True
            for j in range(len(pattern)):
                if positions[i+j] != pattern[j]:
                    match = False
                    break
            if match:
                return True
        return False
        
    def _detect_continuous_gaze(self, positions, target_position, min_count):
        """检测是否持续注视某个位置
        
        根据用户需求优化持续注视检测：
        - 对于'top'位置，检测持续向上看的情况
        - 对于'bottom'位置，检测持续向下看的情况
        """
        # 对于顶部位置的检测
        if target_position == 'top':
            # 计算目标位置在最近序列中的比例
            target_count = positions.count(target_position)
            # 如果目标位置占比超过50%且至少有min_count个，则认为是持续注视
            if target_count >= min_count and target_count / len(positions) >= 0.5:
                return True
            
            # 检查最近的几个位置
            recent = positions[-min_count:]
            # 如果最近的几个位置中目标位置占多数，也认为是持续注视
            if recent.count(target_position) >= min_count / 2 + 0.5:
                return True
            return False
        
        # 对于底部位置的检测
        elif target_position == 'bottom':
            # 计算目标位置在最近序列中的比例
            target_count = positions.count(target_position)
            # 如果目标位置占比超过50%且至少有min_count个，则认为是持续注视
            if target_count >= min_count and target_count / len(positions) >= 0.5:
                return True
            
            # 检查最近的几个位置
            recent = positions[-min_count:]
            # 如果最近的几个位置中目标位置占多数，也认为是持续注视
            if recent.count(target_position) >= min_count / 2 + 0.5:
                return True
            return False
        
        # 对于其他位置，使用原始的严格连续检测
        else:
            count = 0
            for pos in positions:
                if pos == target_position:
                    count += 1
                else:
                    count = 0  # 重置计数
                    
                if count >= min_count:
                    return True
                    
            return False
                
    def start_scroll_up(self, speed=None):
        if speed:
            print(f"开始向上滚动 (速度: {speed})")
            self.screen_controller.set_scroll_speed_by_eye_movement(speed)
        else:
            print("开始向上滚动")
        threading.Thread(target=self.screen_controller.start_scroll_up, daemon=True).start()
        
    def start_scroll_down(self, speed=None):
        if speed:
            print(f"开始向下滚动 (速度: {speed})")
            self.screen_controller.set_scroll_speed_by_eye_movement(speed)
        else:
            print("开始向下滚动")
        threading.Thread(target=self.screen_controller.start_scroll_down, daemon=True).start()
        
    def stop_scrolling_if_needed(self):
        if self.last_trend_action in ['continuous_scroll_up', 'continuous_scroll_down', 'scroll_up_once', 'scroll_down_once']:
            print("停止滚动")
            self.screen_controller.stop_all_scrolling()
            self.last_trend_action = 'stop'
            self.continuous_scroll = False
            
    def cleanup(self):
        print("正在清理资源...")
        self.screen_controller.stop_all_scrolling()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("清理完成")

def main():
    print("=== 眼球追踪控制Mac屏幕滚动 ===")
    print("功能说明：")
    print("- 向下看一下再向上看一下：向上滚动一次")
    print("- 向上看一下再向下看一下：向下滚动一次")
    print("- 持续向下看：持续向上滚动")
    print("- 持续向上看：持续向下滚动")
    print("- 注视屏幕中间：停止滚动")
    print("- 按 'q' 键退出程序")
    print("- 按 's' 键切换预览显示")
    print("- 按 'c' 键进入校准模式")
    print()
    
    controller = EyeScrollController()
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        controller.cleanup()
    print("程序已退出")

if __name__ == "__main__":
    main()
