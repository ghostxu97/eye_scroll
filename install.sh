#!/bin/bash

# 眼球追踪控制项目安装脚本

echo "=== 眼球追踪控制Mac屏幕滚动 - 安装脚本 ==="
echo ""

# 检查操作系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠ 警告：此脚本专为macOS设计，当前系统: $OSTYPE"
    echo "在其他系统上可能无法正常工作"
    echo ""
fi

# 检查Python版本
echo "检查Python环境..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ Python版本: $python_version"
else
    echo "✗ 未找到Python3"
    echo "请先安装Python3: https://www.python.org/downloads/"
    exit 1
fi

# 检查pip
echo "检查pip..."
if ! python3 -m pip --version >/dev/null 2>&1; then
    echo "✗ pip不可用，正在尝试安装..."
    python3 -m ensurepip --upgrade
    if [[ $? -ne 0 ]]; then
        echo "✗ pip安装失败，请手动安装"
        exit 1
    fi
fi
echo "✓ pip可用"

# 升级pip
echo "升级pip..."
python3 -m pip install --upgrade pip

# 安装依赖包
echo "安装Python依赖包..."
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

if python3 -m pip install -r requirements.txt; then
    echo "✓ 依赖包安装成功"
else
    echo "✗ 依赖包安装失败"
    echo "请检查网络连接或手动安装："
    echo "  pip3 install opencv-python mediapipe numpy pyautogui pynput"
    exit 1
fi

# 设置权限
echo "设置脚本权限..."
chmod +x run.sh
chmod +x install.sh
echo "✓ 权限设置完成"

# 测试环境
echo "测试环境..."
if python3 test_modules.py; then
    echo "✓ 环境测试通过"
else
    echo "⚠ 环境测试失败，但安装已完成"
    echo "请检查错误信息并手动解决"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "使用方法："
echo "1. 运行测试: python3 test_modules.py"
echo "2. 运行演示: python3 demo.py"
echo "3. 运行主程序: python3 main.py"
echo "4. 或使用启动脚本: ./run.sh"
echo ""
echo "注意事项："
echo "- 首次运行时需要允许摄像头权限"
echo "- 确保有足够的照明条件"
echo "- 建议先运行测试脚本验证环境"
echo ""
echo "如有问题，请查看README.md文件或运行测试脚本"
