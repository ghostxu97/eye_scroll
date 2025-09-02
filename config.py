# -*- coding: utf-8 -*-
"""
配置文件 - 眼球追踪控制参数
"""

# 眼球追踪参数
GAZE_THRESHOLD = 0.4        # 注视置信度阈值 (0.1-1.0)，降低以提高灵敏度
POSITION_HOLD_TIME = 0.3    # 位置保持时间 (秒)，降低以提高响应速度

# 摄像头参数
CAMERA_WIDTH = 640          # 摄像头宽度
CAMERA_HEIGHT = 480         # 摄像头高度
CAMERA_FPS = 30             # 摄像头帧率

# 滚动参数
SCROLL_SPEED = 3            # 基础滚动速度 (像素/次)
SCROLL_INTERVAL = 0.05      # 滚动间隔 (秒)
ADAPTIVE_SPEED = True       # 是否启用自适应速度
MAX_SCROLL_SPEED = 8        # 最大滚动速度
ACCELERATION = 0.2          # 加速度

# 注视区域参数
TOP_THRESHOLD = 0.3         # 顶部区域阈值 (屏幕高度的比例)
BOTTOM_THRESHOLD = 0.7      # 底部区域阈值 (屏幕高度的比例)

# 显示参数
SHOW_PREVIEW = True         # 是否显示预览窗口
PREVIEW_WINDOW_NAME = "Eye Tracking Control"

# 调试参数
DEBUG_MODE = True           # 是否启用调试模式
LOG_LEVEL = "INFO"          # 日志级别

# 校准参数
CALIBRATION_MODE = False    # 是否启用校准模式
GAZE_OFFSET_MULTIPLIER = 4.5 # 注视偏移放大倍数 - 适当降低以减少过度灵敏

# 针对Mac摄像头位于屏幕顶端的特性进行优化
# 由于注视摄像头附近时实际上是在看屏幕顶部，我们调整阈值使其更符合这一特性
GAZE_TOP_THRESHOLD = 0.0070 # 向上注视阈值 - 根据实际测试值调整，向上看时offset_y约为0.008-0.009
GAZE_BOTTOM_THRESHOLD = 0.0080 # 向下注视阈值 - 根据实际测试值调整，向下看时offset_y约为0.009
