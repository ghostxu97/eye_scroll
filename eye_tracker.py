import cv2
import mediapipe as mp
import numpy as np
import config
from typing import Tuple, Optional

class EyeTracker:
    """眼球追踪器类，用于检测用户眼球位置和注视方向"""
    
    def __init__(self, debug_mode=False):
        # 初始化MediaPipe
        self.debug_mode = debug_mode
        self.calibration_mode = config.CALIBRATION_MODE
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 眼部关键点索引
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # 虹膜关键点索引
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # 屏幕尺寸
        self.screen_width = 1920  # 默认值，会在运行时更新
        self.screen_height = 1080
        
        # 注视区域阈值
        self.top_threshold = 0.3  # 屏幕顶部30%区域
        self.bottom_threshold = 0.7  # 屏幕底部30%区域
        
        # 校准数据
        self.calibration_samples = []
        self.is_calibrated = False
        
    def set_screen_dimensions(self, width: int, height: int):
        """设置屏幕尺寸"""
        self.screen_width = width
        self.screen_height = height
        
    def start_calibration(self):
        """开始校准过程"""
        self.calibration_mode = True
        self.calibration_samples = []
        self.is_calibrated = False
        print("校准模式已启动，请注视屏幕中心5秒钟...")
        
    # 已将add_calibration_sample方法的功能整合到get_eye_position方法中
            
    def finish_calibration(self):
        """完成校准过程"""
        if len(self.calibration_samples) < 10:
            print("校准失败：样本数量不足")
            return
            
        # 计算中心注视的平均偏移值
        avg_x = sum(sample[0] for sample in self.calibration_samples) / len(self.calibration_samples)
        avg_y = sum(sample[1] for sample in self.calibration_samples) / len(self.calibration_samples)
        
        # 计算标准差，用于确定阈值
        std_y = np.std([sample[1] for sample in self.calibration_samples])
        
        # 设置新的阈值（中心偏移值 +/- 2.5倍标准差）
        new_top_threshold = avg_y - (2.5 * std_y)
        new_bottom_threshold = avg_y + (2.5 * std_y)
        
        # 更新配置
        config.GAZE_TOP_THRESHOLD = new_top_threshold
        config.GAZE_BOTTOM_THRESHOLD = new_bottom_threshold
        
        print(f"校准完成！新的阈值设置为：上 {new_top_threshold:.6f}，下 {new_bottom_threshold:.6f}")
        
        # 退出校准模式
        self.calibration_mode = False
        self.is_calibrated = True
        
    def get_eye_position(self, frame) -> Optional[Tuple[str, float]]:
        """获取眼球位置
        返回：(位置, 置信度)
        位置可能是：'top', 'center', 'bottom'
        置信度范围：0.0-1.0
        """
        # 转换为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 处理图像
        results = self.face_mesh.process(rgb_frame)
        
        # 如果没有检测到面部，返回None
        if not results.multi_face_landmarks:
            return None
            
        # 获取第一个检测到的面部
        face_landmarks = results.multi_face_landmarks[0]
        
        # 获取左右眼虹膜中心点
        left_iris = self._get_iris_center(face_landmarks, self.LEFT_IRIS)
        right_iris = self._get_iris_center(face_landmarks, self.RIGHT_IRIS)
        
        # 获取左右眼中心点
        left_eye_center = self._get_eye_center(face_landmarks, self.LEFT_EYE)
        right_eye_center = self._get_eye_center(face_landmarks, self.RIGHT_EYE)
        
        # 如果在校准模式，添加校准样本
        if self.calibration_mode:
            # 计算左右眼偏移
            left_offset_x = left_iris[0] - left_eye_center[0]
            left_offset_y = left_iris[1] - left_eye_center[1]
            right_offset_x = right_iris[0] - right_eye_center[0]
            right_offset_y = right_iris[1] - right_eye_center[1]
            
            # 添加校准样本
            avg_offset_x = (left_offset_x + right_offset_x) / 2
            avg_offset_y = (left_offset_y + right_offset_y) / 2
            self.calibration_samples.append((avg_offset_x, avg_offset_y))
            
            # 如果收集了足够的样本，完成校准
            if len(self.calibration_samples) >= 100:  # 约5秒，每秒20帧
                self.finish_calibration()
                
            return 'center', 1.0  # 校准模式下固定返回中心位置
        
        if left_iris is None or right_iris is None:
            return None
            
        # 计算注视方向
        gaze_direction = self._calculate_gaze_direction(face_landmarks, left_iris, right_iris)
        
        # 判断注视位置
        position = self._determine_gaze_position(gaze_direction)
        
        # 计算置信度（基于面部检测的置信度）
        confidence = 0.8  # 简化处理
        
        return position, confidence
        
    def _get_iris_center(self, landmarks, iris_indices) -> Optional[Tuple[float, float]]:
        """获取虹膜中心点"""
        try:
            x_coords = [landmarks.landmark[idx].x for idx in iris_indices]
            y_coords = [landmarks.landmark[idx].y for idx in iris_indices]
            
            center_x = sum(x_coords) / len(x_coords)
            center_y = sum(y_coords) / len(y_coords)
            
            return center_x, center_y
        except:
            return None
            
    def _calculate_gaze_direction(self, landmarks, left_iris, right_iris) -> Tuple[float, float]:
        """计算注视方向向量"""
        # 获取眼睛中心点
        left_eye_center = self._get_eye_center(landmarks, self.LEFT_EYE)
        right_eye_center = self._get_eye_center(landmarks, self.RIGHT_EYE)
        
        # 计算虹膜相对于眼睛中心的偏移
        left_offset_x = left_iris[0] - left_eye_center[0]
        left_offset_y = left_iris[1] - left_eye_center[1]
        
        right_offset_x = right_iris[0] - right_eye_center[0]
        right_offset_y = right_iris[1] - right_eye_center[1]
        
        # 平均偏移 - 使用配置文件中的垂直方向权重
        avg_offset_x = (left_offset_x + right_offset_x) / 2
        
        # 对垂直偏移应用更强的权重，并反转方向使向下看为正值
        # 这样更符合直觉：向下看时值为正，向上看时值为负
        avg_offset_y = -1 * (left_offset_y + right_offset_y) / 2 * config.GAZE_OFFSET_MULTIPLIER
        
        # 保存最近一次计算的注视方向，用于在draw_eye_tracking方法中绘制注视点
        self._last_gaze_direction = (avg_offset_x, avg_offset_y)
        
        # 打印调试信息
        print(f"Eye offset - Left: ({left_offset_x:.4f}, {left_offset_y:.4f}), Right: ({right_offset_x:.4f}, {right_offset_y:.4f}), Avg: ({avg_offset_x:.4f}, {avg_offset_y:.4f})")
        
        return avg_offset_x, avg_offset_y
        
    def _get_eye_center(self, landmarks, eye_indices) -> Tuple[float, float]:
        """获取眼睛中心点"""
        x_coords = [landmarks.landmark[idx].x for idx in eye_indices]
        y_coords = [landmarks.landmark[idx].y for idx in eye_indices]
        
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        
        return center_x, center_y
        
    def _determine_gaze_position(self, gaze_direction) -> str:
        """根据注视方向判断注视位置
        
        针对Mac摄像头位于屏幕顶端的特性进行优化：
        - 当用户注视摄像头附近时，实际上是在看屏幕的顶部区域，我们将其判断为中心区域
        - 只有当用户明显向上看（超过摄像头）时，才判断为向上注视
        - 当用户向下看时，更容易被判断为向下注视
        """
        offset_x, offset_y = gaze_direction
        
        # 垂直方向判断（上下注视）- 基于实际测试值设定阈值
        # 根据用户测试：看中间0.013，看上面0.017，看下面0.009
        # 设定阈值：小于0.011为向下注视，大于0.015为向上注视，中间为中心注视
        
        if offset_y < 0.009:  # 向下注视（小于0.009）
            if self.debug_mode:
                print(f"向下注视检测: {offset_y:.6f} < 0.009")
            return 'bottom'
        elif offset_y > 0.015:  # 向上注视（大于0.015）
            if self.debug_mode:
                print(f"向上注视检测: {offset_y:.6f} > 0.015")
            return 'top'
        else:  # 中心注视（0.009 <= offset_y <= 0.015）
            if self.debug_mode:
                print(f"中心注视检测: 0.009 <= {offset_y:.6f} <= 0.015")
            return 'center'
            
    def draw_eye_tracking(self, frame, eye_position: str = None, confidence: float = 0.0):
        """在帧上绘制眼球追踪信息"""
        # 绘制注视位置指示器
        height, width = frame.shape[:2]
        
        # 顶部区域指示器
        cv2.rectangle(frame, (0, 0), (width, int(height * self.top_threshold)), 
                     (0, 255, 0) if eye_position == 'top' else (100, 100, 100), 2)
        
        # 底部区域指示器
        cv2.rectangle(frame, (0, int(height * self.bottom_threshold)), (width, height), 
                     (0, 255, 0) if eye_position == 'bottom' else (100, 100, 100), 2)
        
        # 使用英文显示当前注视位置，避免中文编码问题
        position_map = {
            'top': 'TOP',
            'bottom': 'BOTTOM',
            'center': 'CENTER',
            None: 'NONE (EYES CLOSED/NOT DETECTED)'
        }
        position_display = position_map.get(eye_position, str(eye_position))
        
        # 显示当前注视位置
        position_text = f"GAZE: {position_display}"
        confidence_text = f"CONF: {confidence:.2f}"
        
        # 使用绿色显示文本，增强可见性
        cv2.putText(frame, position_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, confidence_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 如果检测到眼睛并有注视方向数据
        if eye_position is not None and hasattr(self, '_last_gaze_direction'):
            # 计算注视点在屏幕上的位置
            gaze_x, gaze_y = self._last_gaze_direction
            
            # 将相对偏移转换为屏幕上的坐标
            # 注意：这里使用简化的映射，实际应用中可能需要更复杂的映射算法
            screen_x = int(width/2 + gaze_x * width * 60)  # 进一步放大偏移量使其更明显
            screen_y = int(height/2 + gaze_y * height * 60)
            
            # 显示原始偏移值，用于调试
            cv2.putText(frame, f"RAW OFFSET: ({gaze_x:.6f}, {gaze_y:.6f})", 
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 确保坐标在屏幕范围内
            screen_x = max(0, min(screen_x, width-1))
            screen_y = max(0, min(screen_y, height-1))
            
            # 在屏幕上绘制注视点 - 使用更明显的视觉效果
            # 绘制十字准心
            cv2.line(frame, (screen_x-15, screen_y), (screen_x+15, screen_y), (0, 255, 255), 2)  # 黄色水平线
            cv2.line(frame, (screen_x, screen_y-15), (screen_x, screen_y+15), (0, 255, 255), 2)  # 黄色垂直线
            
            # 绘制注视点圆圈
            cv2.circle(frame, (screen_x, screen_y), 8, (0, 0, 255), -1)  # 红色实心圆
            cv2.circle(frame, (screen_x, screen_y), 12, (255, 255, 255), 2)  # 白色边框
            cv2.circle(frame, (screen_x, screen_y), 20, (0, 255, 255), 1)  # 黄色外圈
            
            # 显示注视点坐标
            cv2.putText(frame, f"GAZE POINT: ({screen_x}, {screen_y})", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            # 如果没有检测到眼睛或闭眼，在屏幕中心显示默认注视点
            center_x = width // 2
            center_y = height // 2
            
            # 绘制中心点指示器 - 使用不同颜色表示这是默认位置
            cv2.line(frame, (center_x-20, center_y), (center_x+20, center_y), (0, 165, 255), 2)  # 橙色水平线
            cv2.line(frame, (center_x, center_y-20), (center_x, center_y+20), (0, 165, 255), 2)  # 橙色垂直线
            
            # 绘制中心点圆圈
            cv2.circle(frame, (center_x, center_y), 10, (0, 165, 255), -1)  # 橙色实心圆
            cv2.circle(frame, (center_x, center_y), 15, (255, 255, 255), 2)  # 白色边框
            cv2.circle(frame, (center_x, center_y), 25, (0, 165, 255), 1)  # 橙色外圈
            
            # 显示默认中心点信息
            cv2.putText(frame, "DEFAULT CENTER POINT (EYES NOT DETECTED)", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            # 重置最后的注视方向为中心点（零偏移）
            self._last_gaze_direction = (0.0, 0.0)
        
        return frame
