# 眼球追踪控制Mac屏幕滚动

这是一个基于Python的眼球追踪项目，可以通过用户的眼球注视来控制Mac电脑的屏幕滚动。通过注视屏幕顶部或底部区域，系统会自动识别并执行相应的滚动操作。

## 功能特性

- **向上滚动**：注视屏幕顶部区域时，持续向上滚动
- **向下滚动**：注视屏幕底部区域时，持续向下滚动
- **停止滚动**：注视屏幕中间区域或移开视线时，停止滚动
- **自适应速度**：滚动速度会随着注视时间逐渐增加，提供更自然的滚动体验
- **实时预览**：显示摄像头画面和眼球追踪状态，包括FPS和当前注视位置
- **可调节参数**：通过配置文件支持调整各种参数，包括注视阈值、滚动速度等

## 系统要求

- macOS 系统
- Python 3.7+
- 内置或外接摄像头
- 足够的照明条件

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. **启动程序**：
   ```bash
   python main.py
   ```

2. **操作说明**：
   - 注视屏幕顶部：向上滚动
   - 注视屏幕底部：向下滚动
   - 注视屏幕中间：停止滚动
   - 按 `q` 键：退出程序
   - 按 `s` 键：切换预览显示

3. **注意事项**：
   - 确保面部在摄像头视野内
   - 保持适当的照明条件
   - 避免剧烈头部运动
   - 初次使用时可能需要调整姿势和距离

## 配置参数

可以通过修改 `config.py` 文件来调整程序的各项参数：

```python
# 眼球追踪参数
GAZE_THRESHOLD = 0.6        # 注视置信度阈值 (0.1-1.0)
POSITION_HOLD_TIME = 0.5    # 位置保持时间 (秒)

# 滚动参数
SCROLL_SPEED = 3            # 基础滚动速度 (像素/次)
ADAPTIVE_SPEED = True       # 是否启用自适应速度
MAX_SCROLL_SPEED = 8        # 最大滚动速度
```

## 高级使用

### 测试模块

在使用前可以测试各个模块是否正常工作：

```bash
python test_modules.py
```

### 自定义滚动行为

如果需要自定义滚动行为，可以修改 `screen_controller.py` 中的相关方法。例如，可以调整自适应速度的加速度和最大速度：

```python
self.acceleration = 0.2      # 加速度
self.max_scroll_speed = 8    # 最大滚动速度
```

## 项目结构

```
eye_scorll/
├── main.py              # 主程序文件
├── eye_tracker.py       # 眼球追踪模块
├── screen_controller.py # 屏幕控制模块
├── config.py           # 配置参数文件
├── requirements.txt    # 依赖库列表
├── install.sh          # 安装脚本
├── run.sh              # 运行脚本
├── test_modules.py     # 模块测试脚本
└── README.md           # 项目说明文档
```

## 技术原理

### 眼球追踪
- 使用MediaPipe进行面部检测和关键点识别
- 通过虹膜位置计算注视方向
- 支持实时视频流处理

### 屏幕控制
- 使用pyautogui执行滚动操作
- 支持持续滚动和停止控制
- 线程安全的滚动控制

### 控制逻辑
- 注视位置检测和分类
- 时间阈值控制，避免误触发
- 状态机管理滚动行为

## 参数调整

可以在代码中调整以下参数：

- `gaze_threshold`：注视置信度阈值（0.1-1.0）
- `position_hold_time`：位置保持时间（秒）
- `scroll_speed`：滚动速度
- `scroll_interval`：滚动间隔

## 故障排除

### 常见问题

1. **摄像头无法打开**
   - 检查摄像头权限设置
   - 确保没有其他程序占用摄像头

2. **眼球追踪不准确**
   - 改善照明条件
   - 调整面部与摄像头距离
   - 避免强光直射

3. **滚动响应延迟**
   - 调整`position_hold_time`参数
   - 检查系统性能

### 调试模式

程序运行时会显示实时状态信息，包括：
- 当前注视位置
- 追踪置信度
- 滚动状态

## 安全说明

- 程序包含安全机制，移动鼠标到屏幕角落可紧急停止
- 建议在测试环境中先验证功能
- 避免在重要工作环境中直接使用

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。

## Just For Fun
制作不易，打赏随意，感谢大家~ :)
|   微信   |   支付宝    |
|------------|-----------|
|<img src="https://github.com/ghostxu97/clash-for-linux/assets/43178911/4914c6f8-ff73-495e-99fc-f4766ccf8959?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Jib3lmZWl5dQ==,size_16,color_FFFFFF,t_70" width="200"/>| <img src="https://github.com/ghostxu97/clash-for-linux/assets/43178911/201ae7e3-6319-420a-88f3-d599dd3fa6f7?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Jib3lmZWl5dQ==,size_16,color_FFFFFF,t_70" width="200"/>  |
