#!/bin/bash

# 眼球追踪控制启动脚本

echo "=== 眼球追踪控制Mac屏幕滚动 ==="
echo "正在检查环境..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ Python版本: $python_version"
else
    echo "✗ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查依赖包
echo "检查依赖包..."
if ! python3 -c "import cv2, mediapipe, numpy, pyautogui, pynput" 2>/dev/null; then
    echo "✗ 缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
    if [[ $? -ne 0 ]]; then
        echo "✗ 依赖包安装失败，请手动安装"
        exit 1
    fi
    echo "✓ 依赖包安装完成"
else
    echo "✓ 依赖包检查通过"
fi

# 检查摄像头权限
echo "检查摄像头权限..."
if ! python3 -c "import cv2; cap = cv2.VideoCapture(0); print('摄像头可用' if cap.isOpened() else '摄像头不可用'); cap.release()" 2>/dev/null | grep -q "摄像头可用"; then
    echo "⚠ 摄像头可能不可用，请检查权限设置"
    echo "在系统偏好设置 > 安全性与隐私 > 隐私 > 摄像头中允许终端访问摄像头"
fi

echo ""
echo "启动程序..."
echo "操作说明："
echo "- 注视屏幕顶部：向上滚动"
echo "- 注视屏幕底部：向下滚动"
echo "- 注视屏幕中间：停止滚动"
echo "- 按 'q' 键退出程序"
echo "- 按 's' 键切换预览显示"
echo ""

# 启动程序
python3 main.py
