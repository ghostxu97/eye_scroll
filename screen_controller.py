import pyautogui
import time
import threading
from typing import Optional

class ScreenController:
    """屏幕控制器类，用于执行滚动等操作"""
    
    def __init__(self):
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # 操作间隔
        
        # 滚动参数
        self.scroll_speed = 3  # 每次滚动的像素数
        self.scroll_interval = 0.05  # 滚动间隔（秒）
        self.adaptive_speed = True  # 是否启用自适应速度
        self.max_scroll_speed = 8  # 最大滚动速度
        self.acceleration = 0.2  # 加速度
        self.current_speed = 0  # 当前速度
        
        # 当前滚动状态
        self.is_scrolling_up = False
        self.is_scrolling_down = False
        
        # 滚动线程控制
        self.stop_scrolling = False
        self.scroll_thread = None
        
    def start_scroll_up(self):
        """开始向上滚动"""
        if not self.is_scrolling_up:
            self.is_scrolling_up = True
            self.is_scrolling_down = False
            self.stop_scrolling = False
            self.current_speed = 1  # 初始速度
            if self.scroll_thread is None or not self.scroll_thread.is_alive():
                self.scroll_thread = threading.Thread(target=self._scroll_up_continuous, daemon=True)
                self.scroll_thread.start()
            
    def start_scroll_down(self):
        """开始向下滚动"""
        if not self.is_scrolling_down:
            self.is_scrolling_down = True
            self.is_scrolling_up = False
            self.stop_scrolling = False
            self.current_speed = 1  # 初始速度
            if self.scroll_thread is None or not self.scroll_thread.is_alive():
                self.scroll_thread = threading.Thread(target=self._scroll_down_continuous, daemon=True)
                self.scroll_thread.start()
            
    def stop_all_scrolling(self):
        """停止所有滚动"""
        self.stop_scrolling = True
        self.is_scrolling_up = False
        self.is_scrolling_down = False
        self.current_speed = 0  # 重置速度
        
        # 等待线程结束
        if self.scroll_thread and self.scroll_thread.is_alive():
            # 不阻塞主线程，设置超时
            self.scroll_thread.join(timeout=0.1)
            self.scroll_thread = None
        
    def _scroll_up_continuous(self):
        """持续向上滚动，支持自适应速度"""
        while self.is_scrolling_up and not self.stop_scrolling:
            try:
                if self.adaptive_speed:
                    # 自适应速度控制，逐渐加速到最大速度
                    if self.current_speed < self.max_scroll_speed:
                        self.current_speed = min(self.max_scroll_speed, 
                                               self.current_speed + self.acceleration)
                    actual_speed = int(self.current_speed)
                else:
                    actual_speed = self.scroll_speed
                    
                pyautogui.scroll(actual_speed)
                time.sleep(self.scroll_interval)
            except Exception as e:
                print(f"向上滚动出错: {e}")
                break
                
    def _scroll_down_continuous(self):
        """持续向下滚动，支持自适应速度"""
        while self.is_scrolling_down and not self.stop_scrolling:
            try:
                if self.adaptive_speed:
                    # 自适应速度控制，逐渐加速到最大速度
                    if self.current_speed < self.max_scroll_speed:
                        self.current_speed = min(self.max_scroll_speed, 
                                               self.current_speed + self.acceleration)
                    actual_speed = int(self.current_speed)
                else:
                    actual_speed = self.scroll_speed
                    
                pyautogui.scroll(-actual_speed)
                time.sleep(self.scroll_interval)
            except Exception as e:
                print(f"向下滚动出错: {e}")
                break
                
    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self.scroll_speed = max(1, min(20, speed))  # 限制在1-20之间
        
    def set_scroll_speed_by_eye_movement(self, eye_speed: int):
        """根据眼球运动速度设置滚动速度
        
        Args:
            eye_speed: 眼球运动速度 (1-10)
        """
        # 将眼球运动速度(1-10)映射到滚动速度(1-8)
        scroll_speed = min(8, max(1, eye_speed))
        self.max_scroll_speed = scroll_speed
        self.current_speed = min(self.current_speed, scroll_speed)
        
    def update_scroll_speed(self, eye_speed: int):
        """动态更新当前滚动速度
        
        Args:
            eye_speed: 眼球运动速度 (1-10)
        """
        if self.is_scrolling_up or self.is_scrolling_down:
            self.set_scroll_speed_by_eye_movement(eye_speed)
        
    def set_scroll_interval(self, interval: float):
        """设置滚动间隔"""
        self.scroll_interval = max(0.01, min(1.0, interval))  # 限制在0.01-1.0之间
        
    def get_scroll_status(self) -> dict:
        """获取当前滚动状态"""
        return {
            'scrolling_up': self.is_scrolling_up,
            'scrolling_down': self.is_scrolling_down,
            'scroll_speed': self.scroll_speed,
            'scroll_interval': self.scroll_interval,
            'adaptive_speed': self.adaptive_speed,
            'current_speed': self.current_speed,
            'max_scroll_speed': self.max_scroll_speed
        }
        
    def test_scroll(self):
        """测试滚动功能"""
        print("测试向上滚动...")
        pyautogui.scroll(5)
        time.sleep(0.5)
        
        print("测试向下滚动...")
        pyautogui.scroll(-5)
        time.sleep(0.5)
        
        print("滚动测试完成")
