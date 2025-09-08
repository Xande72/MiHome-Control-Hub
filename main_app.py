#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
米家设备整合控制系统 - 主应用程序
功能:
- 设备发现与配置管理
- 手势识别控制
- 设备状态监控
- 图形化用户界面
"""

import sys
import os
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# GUI库
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError:
    print("错误: 无法导入tkinter库")
    sys.exit(1)

# 导入自定义模块
try:
    from device_controller import DeviceController, LightDevice
    from gesture_recognition import GestureController, GestureType
    from config_manager import ConfigManager, DeviceConfig
except ImportError as e:
    print(f"错误: 无法导入模块 - {e}")
    sys.exit(1)

# 配置日志
log_file = Path('mihome_control.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

class MiHomeControlApp:
    """米家设备控制主应用"""
    
    def __init__(self):
        # 初始化组件
        self.config_manager = ConfigManager("config.yaml")
        self.device_controller = DeviceController()
        self.gesture_controller = None
        
        # GUI相关
        self.root = None
        self.notebook = None
        self.device_tree = None
        self.status_text = None
        self.gesture_status_label = None
        
        # 状态变量
        self.is_running = False
        self.gesture_enabled = False
        self.status_update_thread = None
        
        # 设备选中状态字典
        self.device_checked = {}
        
        # 加载配置
        self._load_initial_config()
    
    def _load_initial_config(self):
        """加载初始配置"""
        try:
            # 加载配置文件
            if not self.config_manager.load_config():
                logger.warning("使用默认配置")
            
            # 检查是否有light.json文件，如果有则导入
            light_json_path = Path("light.json")
            if light_json_path.exists():
                logger.info("发现light.json文件，正在导入设备配置...")
                if self.config_manager.load_from_json("light.json"):
                    self.config_manager.save_config()
                    logger.info("设备配置导入成功")
            
            # 加载设备到控制器
            self._load_devices_to_controller()
            
        except Exception as e:
            logger.error(f"加载初始配置失败: {str(e)}")
    
    def _load_devices_to_controller(self):
        """将配置中的设备加载到控制器"""
        try:
            devices = self.config_manager.get_enabled_devices()
            if not devices:
                logger.warning("没有找到启用的设备")
                return
            
            # 创建临时配置文件供设备控制器使用
            temp_config = {
                'devices': {}
            }
            
            for name, device_config in devices.items():
                temp_config['devices'][name] = {
                    'type': device_config.type,
                    'ip': device_config.ip,
                    'token': device_config.token,
                    'model': device_config.model,
                    'did': device_config.did,
                    'mac': device_config.mac
                }
            
            # 保存临时配置并加载到设备控制器
            import yaml
            with open('temp_devices.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(temp_config, f, default_flow_style=False, allow_unicode=True)
            
            if self.device_controller.load_config('temp_devices.yaml'):
                logger.info(f"成功加载 {len(devices)} 个设备到控制器")
            
            # 清理临时文件
            try:
                os.remove('temp_devices.yaml')
            except:
                pass
                
        except Exception as e:
            logger.error(f"加载设备到控制器失败: {str(e)}")
    
    def create_gui(self):
        """创建图形用户界面"""
        self.root = tk.Tk()
        self.root.title("米家设备整合控制系统")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 创建主菜单
        self._create_menu()
        
        # 创建主界面
        self._create_main_interface()
        
        # 创建状态栏
        self._create_status_bar()
        
        logger.info("GUI界面创建完成")
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入设备配置", command=self.import_device_config)
        file_menu.add_command(label="导出设备配置", command=self.export_device_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 设备菜单
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设备", menu=device_menu)
        device_menu.add_command(label="刷新设备状态", command=self.refresh_device_status)
        device_menu.add_command(label="打开所有设备", command=self.turn_on_all_devices)
        device_menu.add_command(label="关闭所有设备", command=self.turn_off_all_devices)
        
        # 手势菜单
        gesture_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="手势控制", menu=gesture_menu)
        gesture_menu.add_command(label="启动手势识别", command=self.start_gesture_recognition)
        gesture_menu.add_command(label="停止手势识别", command=self.stop_gesture_recognition)
        gesture_menu.add_command(label="手势说明", command=self.show_gesture_help)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def _create_main_interface(self):
        """创建主界面"""
        # 创建笔记本控件（标签页）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 设备控制标签页
        self._create_device_tab()
        
        # 手势控制标签页
        self._create_gesture_tab()
        
        # 系统监控标签页
        self._create_monitor_tab()
        
        # 设置标签页
        self._create_settings_tab()
    
    def _create_device_tab(self):
        """创建设备控制标签页"""
        device_frame = ttk.Frame(self.notebook)
        self.notebook.add(device_frame, text="设备控制")
        
        # 设备列表
        list_frame = ttk.LabelFrame(device_frame, text="设备列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树形控件
        columns = ('选择', '名称', '类型', '状态', '亮度', '色温', 'IP地址')
        self.device_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题和宽度
        self.device_tree.heading('选择', text='选择')
        self.device_tree.column('选择', width=50, anchor='center')
        
        for col in columns[1:]:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=100)
        
        # 绑定点击事件
        self.device_tree.bind('<Button-1>', self._on_device_tree_click)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=scrollbar.set)
        
        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设备控制按钮
        control_frame = ttk.Frame(device_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="打开选中设备", command=self.turn_on_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="关闭选中设备", command=self.turn_off_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="增加亮度", command=self.increase_brightness).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="减少亮度", command=self.decrease_brightness).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="提高色温", command=self.increase_color_temp).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="降低色温", command=self.decrease_color_temp).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="刷新状态", command=self.refresh_device_status).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="检查在线状态", command=self.check_devices_online).pack(side=tk.LEFT, padx=2)
    
    def _create_gesture_tab(self):
        """创建手势控制标签页"""
        gesture_frame = ttk.Frame(self.notebook)
        self.notebook.add(gesture_frame, text="手势控制")
        
        # 手势状态
        status_frame = ttk.LabelFrame(gesture_frame, text="手势识别状态")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.gesture_status_label = ttk.Label(status_frame, text="手势识别: 未启动", font=('Arial', 12))
        self.gesture_status_label.pack(pady=10)
        
        # 控制按钮
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="启动手势识别", command=self.start_gesture_recognition).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="停止手势识别", command=self.stop_gesture_recognition).pack(side=tk.LEFT, padx=5)
        
        # 手势说明
        help_frame = ttk.LabelFrame(gesture_frame, text="支持的手势")
        help_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        gesture_help_text = """
手势控制说明:

通用手势（左右手通用）:
🤛 拳头 (Fist) - 关闭所有设备
✋ 张开手掌 (Open Palm) - 打开所有设备
✌️ V手势 (Peace) - 切换设备状态

右手专用手势:
👍 右手拇指向上 - 增加亮度 (+20%)
☝️ 右手食指向上 - 设置最大亮度 (100%)

左手专用手势:
👍 左手拇指向上 - 降低亮度 (-20%)
☝️ 左手食指向上 - 设置最小亮度 (1%)

注意事项:
- 请确保摄像头正常工作
- 手势需要保持稳定几秒钟才会触发
- 在光线充足的环境下效果更好
- 左右手功能不同，请注意区分
- 按 'q' 键可以退出手势识别窗口
        """
        
        help_text = tk.Text(help_frame, wrap=tk.WORD, font=('Arial', 10))
        help_text.insert(tk.END, gesture_help_text)
        help_text.config(state=tk.DISABLED)
        
        help_scrollbar = ttk.Scrollbar(help_frame, orient=tk.VERTICAL, command=help_text.yview)
        help_text.configure(yscrollcommand=help_scrollbar.set)
        
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_monitor_tab(self):
        """创建系统监控标签页"""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="系统监控")
        
        # 系统状态
        status_frame = ttk.LabelFrame(monitor_frame, text="系统状态")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 状态信息
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text="系统版本:").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(info_frame, text="1.0.0").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="设备数量:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.device_count_label = ttk.Label(info_frame, text="0")
        self.device_count_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="在线设备:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.online_count_label = ttk.Label(info_frame, text="0")
        self.online_count_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(monitor_frame, text="系统日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 清空日志按钮
        ttk.Button(monitor_frame, text="清空日志", command=self.clear_log).pack(pady=5)
    
    def _create_settings_tab(self):
        """创建设置标签页"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="设置")
        
        # 手势设置
        gesture_settings_frame = ttk.LabelFrame(settings_frame, text="手势识别设置")
        gesture_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(gesture_settings_frame, text="摄像头索引:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.camera_index_var = tk.StringVar(value="0")
        ttk.Entry(gesture_settings_frame, textvariable=self.camera_index_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(gesture_settings_frame, text="亮度调节步长:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.brightness_step_var = tk.StringVar(value="20")
        ttk.Entry(gesture_settings_frame, textvariable=self.brightness_step_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # 系统设置
        system_settings_frame = ttk.LabelFrame(settings_frame, text="系统设置")
        system_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(system_settings_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(system_settings_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], width=10)
        log_level_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # 保存设置按钮
        ttk.Button(settings_frame, text="保存设置", command=self.save_settings).pack(pady=10)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_bar = ttk.Label(status_frame, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=2, pady=2)
    
    def start_gesture_recognition(self):
        """启动手势识别"""
        try:
            if self.gesture_controller and self.gesture_controller.is_running():
                messagebox.showwarning("警告", "手势识别已经在运行中")
                return
            
            # 创建手势控制器
            self.gesture_controller = GestureController()
            
            # 注册设备控制回调函数
            self._register_gesture_callbacks()
            
            # 获取摄像头索引
            camera_index = int(self.camera_index_var.get())
            
            # 启动手势识别
            if self.gesture_controller.start(camera_index):
                self.gesture_enabled = True
                self.gesture_status_label.config(text="手势识别: 运行中", foreground="green")
                self.update_status("手势识别已启动")
                logger.info("手势识别启动成功")
            else:
                messagebox.showerror("错误", "启动手势识别失败，请检查摄像头是否正常")
                
        except ValueError:
            messagebox.showerror("错误", "摄像头索引必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"启动手势识别失败: {str(e)}")
            logger.error(f"启动手势识别失败: {str(e)}")
    
    def stop_gesture_recognition(self):
        """停止手势识别"""
        try:
            if self.gesture_controller:
                self.gesture_controller.stop()
                self.gesture_controller = None
            
            self.gesture_enabled = False
            self.gesture_status_label.config(text="手势识别: 已停止", foreground="red")
            self.update_status("手势识别已停止")
            logger.info("手势识别已停止")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止手势识别失败: {str(e)}")
            logger.error(f"停止手势识别失败: {str(e)}")
    
    def _register_gesture_callbacks(self):
        """注册手势回调函数"""
        if not self.gesture_controller:
            return
        
        # 创建设备控制回调函数
        def create_device_callback(action):
            def callback():
                try:
                    if action == "close_all":
                        result = self.device_controller.turn_off_all()
                        self.update_status(f"关闭所有设备: {result}")
                        logger.info(f"关闭所有设备结果: {result}")
                    elif action == "open_all":
                        result = self.device_controller.turn_on_all()
                        self.update_status(f"打开所有设备: {result}")
                        logger.info(f"打开所有设备结果: {result}")
                    elif action == "toggle_device":
                        # 切换第一个设备的状态
                        devices = self.device_controller.get_all_devices()
                        if devices:
                            device_name = list(devices.keys())[0]
                            device = devices[device_name]
                            if hasattr(device, 'device_info') and device.device_info.power:
                                device.turn_off()
                                self.update_status(f"关闭设备: {device_name}")
                                logger.info(f"关闭设备: {device_name}")
                            else:
                                device.turn_on()
                                self.update_status(f"打开设备: {device_name}")
                                logger.info(f"打开设备: {device_name}")
                    elif action == "max_brightness":
                        devices = self.device_controller.get_all_devices()
                        for device_name, device in devices.items():
                            if device.is_online() and hasattr(device, 'set_brightness'):
                                device.set_brightness(100)
                        self.update_status("设置最大亮度")
                        logger.info("设置最大亮度")
                    elif action == "increase_brightness":
                        brightness_step = int(self.brightness_step_var.get())
                        devices = self.device_controller.get_all_devices()
                        for device_name, device in devices.items():
                            if device.is_online() and hasattr(device, 'adjust_brightness'):
                                device.adjust_brightness(brightness_step)
                        self.update_status(f"增加亮度 {brightness_step}%")
                        logger.info(f"增加亮度 {brightness_step}%")
                    elif action == "decrease_brightness":
                        brightness_step = int(self.brightness_step_var.get())
                        devices = self.device_controller.get_all_devices()
                        for device_name, device in devices.items():
                            if device.is_online() and hasattr(device, 'adjust_brightness'):
                                device.adjust_brightness(-brightness_step)
                        self.update_status(f"降低亮度 {brightness_step}%")
                        logger.info(f"降低亮度 {brightness_step}%")
                    elif action == "min_brightness":
                        devices = self.device_controller.get_all_devices()
                        for device_name, device in devices.items():
                            if device.is_online() and hasattr(device, 'set_brightness'):
                                device.set_brightness(1)
                        self.update_status("设置最小亮度")
                        logger.info("设置最小亮度")
                    elif action == "increase_color_temp":
                        result = self.device_controller.adjust_color_temp_all(200)
                        self.update_status(f"提高色温(冷光): {result}")
                        logger.info(f"提高色温结果: {result}")
                    elif action == "decrease_color_temp":
                        result = self.device_controller.adjust_color_temp_all(-200)
                        self.update_status(f"降低色温(暖光): {result}")
                        logger.info(f"降低色温结果: {result}")
                    elif action == "set_cool_color_temp":
                        result = self.device_controller.set_color_temp_all(6500)
                        self.update_status(f"设置冷光色温: {result}")
                        logger.info(f"设置冷光色温结果: {result}")
                    elif action == "set_warm_color_temp":
                        result = self.device_controller.set_color_temp_all(2700)
                        self.update_status(f"设置暖光色温: {result}")
                        logger.info(f"设置暖光色温结果: {result}")
                    
                    # 刷新设备状态
                    self.refresh_device_status()
                    
                except Exception as e:
                    error_msg = f"执行手势操作失败: {str(e)}"
                    self.update_status(error_msg)
                    logger.error(error_msg)
            return callback
        
        # 注册左右手手势回调
        # 左手特定手势
        for gesture_type, command in self.gesture_controller.left_hand_commands.items():
            callback_key = f"left_{gesture_type.value}"
            self.gesture_controller.register_gesture_callback(
                callback_key, create_device_callback(command.action)
            )
        
        # 右手特定手势
        for gesture_type, command in self.gesture_controller.right_hand_commands.items():
            callback_key = f"right_{gesture_type.value}"
            self.gesture_controller.register_gesture_callback(
                callback_key, create_device_callback(command.action)
            )
        
        # 通用手势（左右手都适用）
        for hand in ["left", "right"]:
            for gesture_type, command in self.gesture_controller.gesture_commands.items():
                # 跳过已经在左右手特定映射中的手势
                if (hand == "left" and gesture_type in self.gesture_controller.left_hand_commands) or \
                   (hand == "right" and gesture_type in self.gesture_controller.right_hand_commands):
                    continue
                callback_key = f"{hand}_{gesture_type.value}"
                self.gesture_controller.register_gesture_callback(
                    callback_key, create_device_callback(command.action)
                )
        
        # 注册通用手势回调（不区分左右手）
        for gesture_type, command in self.gesture_controller.gesture_commands.items():
            self.gesture_controller.register_gesture_callback(
                gesture_type.value, create_device_callback(command.action)
            )
        
        logger.info("手势回调函数注册完成")
    
    def refresh_device_status(self):
        """刷新设备状态"""
        try:
            # 清空现有项目
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            # 获取设备状态
            devices = self.device_controller.get_all_devices()
            status_dict = self.device_controller.get_all_status()
            
            online_count = 0
            for name, device in devices.items():
                status = status_dict.get(name, {})
                
                # 使用缓存的在线状态，避免频繁网络请求
                is_online = device.device_info.online
                if is_online:
                    online_count += 1
                
                # 插入到树形控件
                checkbox_state = '☑' if self.device_checked.get(name, False) else '☐'
                self.device_tree.insert('', tk.END, values=(
                    checkbox_state,
                    name,
                    device.device_info.device_type.value,
                    "在线" if is_online else "离线",
                    f"{status.get('brightness', 0)}%",
                    f"{status.get('color_temp', 0)}K",
                    device.device_info.ip
                ))
            
            # 更新统计信息
            self.device_count_label.config(text=str(len(devices)))
            self.online_count_label.config(text=str(online_count))
            
            self.update_status(f"设备状态已刷新 - 总计: {len(devices)}, 在线: {online_count}")
            logger.info(f"设备状态已刷新 - 总计: {len(devices)}, 在线: {online_count}")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新设备状态失败: {str(e)}")
            logger.error(f"刷新设备状态失败: {str(e)}")

    def check_devices_online(self):
        """检查所有设备的在线状态"""
        try:
            self.update_status("正在检查设备在线状态...")
            devices = self.device_controller.get_all_devices()
            
            # 在后台线程中检查设备状态，避免阻塞UI
            def check_online_status():
                online_count = 0
                for name, device in devices.items():
                    try:
                        is_online = device.is_online()
                        if is_online:
                            online_count += 1
                    except Exception as e:
                        logger.warning(f"检查设备 {name} 在线状态失败: {str(e)}")
                
                # 在主线程中更新UI
                self.root.after(0, lambda: [
                    self.refresh_device_status(),
                    self.update_status(f"设备在线状态检查完成 - 总计: {len(devices)}, 在线: {online_count}")
                ])
            
            # 启动后台线程
            threading.Thread(target=check_online_status, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("错误", f"检查设备在线状态失败: {str(e)}")
            logger.error(f"检查设备在线状态失败: {str(e)}")

    def _on_device_tree_click(self, event):
        """处理设备列表点击事件"""
        region = self.device_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.device_tree.identify_column(event.x)
            if column == '#1':  # 选择列
                item = self.device_tree.identify_row(event.y)
                if item:
                    device_name = self.device_tree.item(item)['values'][1]  # 名称在第二列
                    # 切换选中状态
                    self.device_checked[device_name] = not self.device_checked.get(device_name, False)
                    # 更新显示
                    self._update_device_checkbox_display(item, device_name)
    
    def _update_device_checkbox_display(self, item, device_name):
        """更新设备复选框显示"""
        values = list(self.device_tree.item(item)['values'])
        values[0] = '☑' if self.device_checked.get(device_name, False) else '☐'
        self.device_tree.item(item, values=values)
    
    def turn_on_selected(self):
        """打开选中的设备"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'turn_on'):
                    device.turn_on()
            
            self.update_status(f"已打开选中的设备: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"打开设备失败: {str(e)}")
    
    def turn_off_selected(self):
        """关闭选中的设备"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'turn_off'):
                    device.turn_off()
            
            self.update_status(f"已关闭选中的设备: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"关闭设备失败: {str(e)}")
    
    def increase_brightness(self):
        """增加选中设备的亮度"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            brightness_step = int(self.brightness_step_var.get())
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'adjust_brightness'):
                    device.adjust_brightness(brightness_step)
            
            self.update_status(f"已增加选中设备亮度 {brightness_step}%: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except ValueError:
            messagebox.showerror("错误", "亮度步长必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"调整亮度失败: {str(e)}")
    
    def decrease_brightness(self):
        """减少选中设备的亮度"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            brightness_step = int(self.brightness_step_var.get())
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'adjust_brightness'):
                    device.adjust_brightness(-brightness_step)
            
            self.update_status(f"已减少选中设备亮度 {brightness_step}%: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except ValueError:
            messagebox.showerror("错误", "亮度步长必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"调整亮度失败: {str(e)}")
    
    def increase_color_temp(self):
        """提高选中设备的色温"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'adjust_color_temp'):
                    device.adjust_color_temp(200)
            
            self.update_status(f"已提高选中设备色温 200K: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"调整色温失败: {str(e)}")
    
    def decrease_color_temp(self):
        """降低选中设备的色温"""
        selected_devices = [name for name, checked in self.device_checked.items() if checked]
        if not selected_devices:
            messagebox.showwarning("警告", "请先勾选要控制的设备")
            return
        
        try:
            for device_name in selected_devices:
                device = self.device_controller.get_device(device_name)
                if device and hasattr(device, 'adjust_color_temp'):
                    device.adjust_color_temp(-200)
            
            self.update_status(f"已降低选中设备色温 200K: {', '.join(selected_devices)}")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"调整色温失败: {str(e)}")
    
    def turn_on_all_devices(self):
        """打开所有设备"""
        try:
            results = self.device_controller.turn_on_all()
            success_count = sum(1 for success in results.values() if success)
            self.update_status(f"已打开 {success_count}/{len(results)} 个设备")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"打开所有设备失败: {str(e)}")
    
    def turn_off_all_devices(self):
        """关闭所有设备"""
        try:
            results = self.device_controller.turn_off_all()
            success_count = sum(1 for success in results.values() if success)
            self.update_status(f"已关闭 {success_count}/{len(results)} 个设备")
            self.refresh_device_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"关闭所有设备失败: {str(e)}")
    
    def import_device_config(self):
        """导入设备配置"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择设备配置文件",
                filetypes=[("JSON文件", "*.json"), ("YAML文件", "*.yaml"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                return
            
            if file_path.endswith('.json'):
                if self.config_manager.load_from_json(file_path):
                    self.config_manager.save_config()
                    self._load_devices_to_controller()
                    self.refresh_device_status()
                    messagebox.showinfo("成功", "设备配置导入成功")
                else:
                    messagebox.showerror("错误", "导入设备配置失败")
            else:
                messagebox.showwarning("警告", "暂时只支持JSON格式的配置文件")
                
        except Exception as e:
            messagebox.showerror("错误", f"导入配置失败: {str(e)}")
    
    def export_device_config(self):
        """导出设备配置"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="保存设备配置文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                return
            
            if self.config_manager.export_to_json(file_path):
                messagebox.showinfo("成功", "设备配置导出成功")
            else:
                messagebox.showerror("错误", "导出设备配置失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出配置失败: {str(e)}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 更新手势配置
            self.config_manager.update_gesture_config(
                camera_index=int(self.camera_index_var.get()),
                brightness_step=int(self.brightness_step_var.get())
            )
            
            # 更新系统配置
            self.config_manager.update_system_config(
                log_level=self.log_level_var.get()
            )
            
            # 保存配置文件
            if self.config_manager.save_config():
                messagebox.showinfo("成功", "设置已保存")
                self.update_status("设置已保存")
            else:
                messagebox.showerror("错误", "保存设置失败")
                
        except ValueError as e:
            messagebox.showerror("错误", "设置值格式错误，请检查输入")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def show_gesture_help(self):
        """显示手势帮助"""
        help_text = """
手势控制说明:

通用手势（左右手通用）:
🤛 拳头 (Fist) - 关闭所有设备
✋ 张开手掌 (Open Palm) - 打开所有设备
✌️ V手势 (Peace) - 切换设备状态

右手专用手势:
👍 右手拇指向上 - 增加亮度 (+20%)
☝️ 右手食指向上 - 设置最大亮度 (100%)
🤟 右手三指 - 提高色温(冷光) (+200K)
✌️ 右手两指 - 设置冷光色温 (6500K)

左手专用手势:
👍 左手拇指向上 - 降低亮度 (-20%)
☝️ 左手食指向上 - 设置最小亮度 (1%)
🤟 左手三指 - 降低色温(暖光) (-200K)
✌️ 左手两指 - 设置暖光色温 (2700K)

使用提示:
1. 确保摄像头正常工作
2. 在光线充足的环境下使用
3. 手势需要保持稳定几秒钟
4. 左右手功能不同，请注意区分
5. 色温范围: 1700K-6500K (暖光到冷光)
6. 按 'q' 键退出手势识别窗口
        """
        
        messagebox.showinfo("手势控制说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """
米家设备整合控制系统 v1.0.0

功能特性:
• 设备发现与配置管理
• 手势识别控制
• 设备状态监控
• 图形化用户界面

支持设备:
• Yeelight系列灯具
• 小米智能灯泡
• 米家台灯

开发者: AI Assistant
版权所有 © 2025
        """
        
        messagebox.showinfo("关于", about_text)
    
    def update_status(self, message: str):
        """更新状态栏和日志"""
        try:
            # 更新状态栏
            self.status_bar.config(text=message)
            
            # 添加到日志
            if self.status_text:
                timestamp = time.strftime("%H:%M:%S")
                log_message = f"[{timestamp}] {message}\n"
                self.status_text.insert(tk.END, log_message)
                self.status_text.see(tk.END)
                
                # 限制日志行数
                lines = self.status_text.get("1.0", tk.END).split("\n")
                if len(lines) > 1000:
                    self.status_text.delete("1.0", "100.0")
                    
        except Exception as e:
            logger.error(f"更新状态失败: {str(e)}")
    
    def clear_log(self):
        """清空日志"""
        if self.status_text:
            self.status_text.delete("1.0", tk.END)
            self.update_status("日志已清空")
    
    def start_status_update_thread(self):
        """启动状态更新线程"""
        def update_loop():
            while self.is_running:
                try:
                    # 定期刷新设备状态
                    if hasattr(self, 'device_tree') and self.device_tree:
                        self.root.after(0, self.refresh_device_status)
                    
                    time.sleep(60)  # 每60秒更新一次，减少频率
                    
                except Exception as e:
                    logger.error(f"状态更新线程错误: {str(e)}")
                    time.sleep(10)  # 错误时等待更长时间
        
        self.status_update_thread = threading.Thread(target=update_loop, daemon=True)
        self.status_update_thread.start()
    
    def run(self):
        """运行应用程序"""
        try:
            self.is_running = True
            
            # 创建GUI
            self.create_gui()
            
            # 初始化界面数据
            self.refresh_device_status()
            
            # 启动状态更新线程
            self.start_status_update_thread()
            
            # 显示启动信息
            self.update_status("米家设备整合控制系统已启动")
            
            logger.info("应用程序启动成功")
            
            # 运行GUI主循环
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"运行应用程序失败: {str(e)}")
            messagebox.showerror("错误", f"启动应用程序失败: {str(e)}")
    
    def on_closing(self):
        """关闭应用程序"""
        try:
            # 停止手势识别
            if self.gesture_controller:
                self.gesture_controller.stop()
            
            # 停止状态更新
            self.is_running = False
            
            # 保存配置
            self.config_manager.save_config()
            
            logger.info("应用程序正常退出")
            
            # 关闭窗口
            if self.root:
                self.root.destroy()
                
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {str(e)}")
        
        finally:
            sys.exit(0)

def main():
    """主函数"""
    try:
        # 创建应用程序实例
        app = MiHomeControlApp()
        
        # 运行应用程序
        app.run()
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")
        print(f"错误: {str(e)}")
    finally:
        logger.info("程序结束")

if __name__ == "__main__":
    main()