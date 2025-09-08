#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
米家设备整合控制系统 - 安装脚本

这个脚本帮助用户快速设置项目环境和依赖。
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def install_requirements():
    """安装项目依赖"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ 错误: 找不到requirements.txt文件")
        return False
    
    print("📦 正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_config_template():
    """创建配置文件模板"""
    config_file = Path("config.yaml")
    if config_file.exists():
        print("ℹ️  配置文件已存在，跳过创建")
        return True
    
    config_template = """# 米家设备整合控制系统配置文件
# 请根据实际情况修改以下配置

devices:
  # 示例设备配置
  # 客厅台灯:
  #   type: light
  #   ip: "192.168.1.100"
  #   token: "your_device_token_here"
  #   model: "philips.light.sread1"

camera:
  device_id: 0
  width: 640
  height: 480
  fps: 30

gesture:
  cooldown: 2.0
  confidence_threshold: 0.7
  enabled: true

ui:
  theme: "default"
  window_size:
    width: 800
    height: 600
  auto_refresh_interval: 60  # 秒

logging:
  level: "INFO"
  file: "app.log"
  max_size: "10MB"
  backup_count: 5
"""
    
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_template)
        print("✅ 配置文件模板创建完成: config.yaml")
        return True
    except Exception as e:
        print(f"❌ 配置文件创建失败: {e}")
        return False

def check_camera():
    """检查摄像头可用性"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ 摄像头检查通过")
            cap.release()
            return True
        else:
            print("⚠️  警告: 未检测到可用摄像头，手势控制功能可能无法使用")
            return False
    except ImportError:
        print("⚠️  警告: OpenCV未安装，无法检查摄像头")
        return False
    except Exception as e:
        print(f"⚠️  警告: 摄像头检查失败: {e}")
        return False

def create_shortcuts():
    """创建启动脚本"""
    system = platform.system()
    
    if system == "Windows":
        # 创建Windows批处理文件
        batch_content = """@echo off
echo 启动米家设备整合控制系统...
python main_app.py
pause
"""
        try:
            with open("start.bat", "w", encoding="utf-8") as f:
                f.write(batch_content)
            print("✅ Windows启动脚本创建完成: start.bat")
        except Exception as e:
            print(f"❌ Windows启动脚本创建失败: {e}")
    
    else:
        # 创建Unix/Linux shell脚本
        shell_content = """#!/bin/bash
echo "启动米家设备整合控制系统..."
python3 main_app.py
"""
        try:
            with open("start.sh", "w", encoding="utf-8") as f:
                f.write(shell_content)
            os.chmod("start.sh", 0o755)
            print("✅ Unix/Linux启动脚本创建完成: start.sh")
        except Exception as e:
            print(f"❌ Unix/Linux启动脚本创建失败: {e}")

def main():
    """主安装流程"""
    print("🚀 米家设备整合控制系统 - 安装向导")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_requirements():
        print("\n❌ 安装失败，请检查网络连接和Python环境")
        sys.exit(1)
    
    # 创建配置文件模板
    create_config_template()
    
    # 检查摄像头
    check_camera()
    
    # 创建启动脚本
    create_shortcuts()
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("\n📋 下一步操作:")
    print("1. 编辑 config.yaml 文件，配置您的米家设备")
    print("2. 运行程序: python main_app.py")
    print("3. 或使用启动脚本: start.bat (Windows) / ./start.sh (Unix/Linux)")
    print("\n📖 更多信息请查看 README.md 文件")
    print("🐛 遇到问题？请查看 CONTRIBUTING.md 或提交Issue")

if __name__ == "__main__":
    main()