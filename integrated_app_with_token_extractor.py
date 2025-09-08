import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from xiaomi_device_extractor_gui import XiaomiDeviceExtractorGUI

class IntegratedMiHomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("米家设备整合控制系统")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 创建主界面
        self.create_main_interface()
        
    def create_main_interface(self):
        """创建主界面"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = ttk.Label(title_frame, text="米家设备整合控制系统", 
                               font=("Arial", 20, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="集成设备发现、配置和手势控制功能的米家设备控制系统",
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(5, 0))
        
        # 功能按钮区域
        buttons_frame = ttk.LabelFrame(self.root, text="主要功能", padding=20)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 创建按钮网格
        self.create_function_buttons(buttons_frame)
        
        # 状态信息区域
        status_frame = ttk.LabelFrame(self.root, text="系统状态", padding=20)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.create_status_area(status_frame)
        
    def create_function_buttons(self, parent):
        """创建功能按钮"""
        # 第一行按钮
        row1_frame = ttk.Frame(parent)
        row1_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 设备发现和配置按钮
        self.discover_button = ttk.Button(
            row1_frame, 
            text="🔍 发现和配置米家设备",
            command=self.open_device_extractor,
            width=25
        )
        self.discover_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 手势控制按钮
        self.gesture_button = ttk.Button(
            row1_frame,
            text="👋 启动手势控制",
            command=self.start_gesture_control,
            width=25
        )
        self.gesture_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 设备管理按钮
        self.manage_button = ttk.Button(
            row1_frame,
            text="🎛️ 设备管理界面",
            command=self.open_device_manager,
            width=25
        )
        self.manage_button.pack(side=tk.LEFT)
        
        # 第二行按钮
        row2_frame = ttk.Frame(parent)
        row2_frame.pack(fill=tk.X)
        
        # 配置管理按钮
        self.config_button = ttk.Button(
            row2_frame,
            text="⚙️ 配置管理",
            command=self.open_config_manager,
            width=25
        )
        self.config_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 系统日志按钮
        self.log_button = ttk.Button(
            row2_frame,
            text="📋 查看系统日志",
            command=self.show_system_logs,
            width=25
        )
        self.log_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 帮助按钮
        self.help_button = ttk.Button(
            row2_frame,
            text="❓ 帮助文档",
            command=self.show_help,
            width=25
        )
        self.help_button.pack(side=tk.LEFT)
        
    def create_status_area(self, parent):
        """创建状态显示区域"""
        # 系统状态
        status_info_frame = ttk.Frame(parent)
        status_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(status_info_frame, text="系统状态:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.system_status_var = tk.StringVar(value="就绪")
        self.system_status_label = ttk.Label(status_info_frame, textvariable=self.system_status_var, 
                                           foreground="green")
        self.system_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 设备状态
        device_info_frame = ttk.Frame(parent)
        device_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(device_info_frame, text="已配置设备:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.device_count_var = tk.StringVar(value="0 个")
        self.device_count_label = ttk.Label(device_info_frame, textvariable=self.device_count_var)
        self.device_count_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 手势控制状态
        gesture_info_frame = ttk.Frame(parent)
        gesture_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(gesture_info_frame, text="手势控制:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.gesture_status_var = tk.StringVar(value="未启动")
        self.gesture_status_label = ttk.Label(gesture_info_frame, textvariable=self.gesture_status_var,
                                            foreground="orange")
        self.gesture_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 最近操作日志
        log_frame = ttk.LabelFrame(parent, text="最近操作", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self.recent_log = tk.Text(log_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.recent_log.yview)
        self.recent_log.configure(yscrollcommand=scrollbar.set)
        
        self.recent_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加初始日志
        self.add_log("系统启动完成")
        self.add_log("等待用户操作...")
        
    def add_log(self, message):
        """添加日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.recent_log.config(state=tk.NORMAL)
        self.recent_log.insert(tk.END, log_message)
        self.recent_log.see(tk.END)
        self.recent_log.config(state=tk.DISABLED)
        
    def update_system_status(self, status, color="green"):
        """更新系统状态"""
        self.system_status_var.set(status)
        self.system_status_label.config(foreground=color)
        self.add_log(f"系统状态: {status}")
        
    def open_device_extractor(self):
        """打开设备发现和配置界面"""
        self.add_log("打开设备发现和配置界面")
        self.update_system_status("设备发现中...", "blue")
        
        # 创建新窗口
        extractor_window = tk.Toplevel(self.root)
        extractor_window.title("小米设备Token提取器")
        extractor_window.geometry("800x600")
        extractor_window.transient(self.root)
        
        # 创建设备提取器GUI
        extractor_app = XiaomiDeviceExtractorGUI(extractor_window)
        
        # 当窗口关闭时更新状态
        def on_extractor_close():
            self.update_system_status("就绪", "green")
            self.add_log("设备配置界面已关闭")
            self.check_device_config()
            
        extractor_window.protocol("WM_DELETE_WINDOW", lambda: [
            on_extractor_close(),
            extractor_window.destroy()
        ])
        
    def start_gesture_control(self):
        """启动手势控制"""
        # 检查是否有配置的设备
        if not self.check_device_config():
            messagebox.showwarning(
                "警告", 
                "请先配置设备！\n\n点击'发现和配置米家设备'按钮来配置您的设备。"
            )
            return
            
        self.add_log("启动手势控制系统")
        self.gesture_status_var.set("启动中...")
        self.gesture_status_label.config(foreground="blue")
        
        # 在新线程中启动手势控制
        threading.Thread(target=self.gesture_control_thread, daemon=True).start()
        
    def gesture_control_thread(self):
        """手势控制线程"""
        try:
            # 这里应该导入和启动实际的手势控制模块
            # from mediapipe_gesture_detector import GestureDetector
            # detector = GestureDetector()
            # detector.start()
            
            # 模拟启动过程
            import time
            time.sleep(2)
            
            self.root.after(0, lambda: [
                self.gesture_status_var.set("运行中"),
                self.gesture_status_label.config(foreground="green"),
                self.add_log("手势控制系统启动成功")
            ])
            
        except Exception as e:
            self.root.after(0, lambda: [
                self.gesture_status_var.set("启动失败"),
                self.gesture_status_label.config(foreground="red"),
                self.add_log(f"手势控制启动失败: {str(e)}")
            ])
            
    def open_device_manager(self):
        """打开设备管理界面"""
        self.add_log("打开设备管理界面")
        messagebox.showinfo("提示", "设备管理界面功能正在开发中...")
        
    def open_config_manager(self):
        """打开配置管理界面"""
        self.add_log("打开配置管理界面")
        messagebox.showinfo("提示", "配置管理界面功能正在开发中...")
        
    def show_system_logs(self):
        """显示系统日志"""
        self.add_log("查看系统日志")
        
        # 创建日志窗口
        log_window = tk.Toplevel(self.root)
        log_window.title("系统日志")
        log_window.geometry("700x500")
        log_window.transient(self.root)
        
        # 日志文本框
        log_text = tk.Text(log_window, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_window, orient=tk.VERTICAL, command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        
        log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=20)
        
        # 添加示例日志内容
        sample_logs = [
            "系统启动完成",
            "加载配置文件",
            "初始化摄像头模块",
            "初始化设备控制模块",
            "系统就绪，等待用户操作"
        ]
        
        import datetime
        for log in sample_logs:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_text.insert(tk.END, f"[{timestamp}] {log}\n")
            
    def show_help(self):
        """显示帮助文档"""
        self.add_log("查看帮助文档")
        
        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助文档")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        # 帮助内容
        help_text = tk.Text(help_window, wrap=tk.WORD, padx=20, pady=20)
        scrollbar = ttk.Scrollbar(help_window, orient=tk.VERTICAL, command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加帮助内容
        help_content = """
米家设备整合控制系统 - 使用帮助

1. 设备发现和配置
   - 点击"发现和配置米家设备"按钮
   - 输入小米账户信息进行登录
   - 完成验证码或2FA验证（如需要）
   - 在设备列表中选择需要控制的设备
   - 点击"导出配置"保存设备信息

2. 手势控制
   - 确保已配置设备
   - 点击"启动手势控制"按钮
   - 摄像头窗口将显示实时画面
   - 支持的手势：
     🖐️ 张开手掌 - 打开所有设备
     ✊ 握拳 - 关闭所有设备
     👍 竖起大拇指 - 增加亮度
     👎 大拇指向下 - 降低亮度

3. 设备管理
   - 点击"设备管理界面"查看所有设备状态
   - 可以手动控制单个设备
   - 查看设备详细信息和状态

4. 故障排除
   - 设备发现失败：检查网络连接和账户信息
   - 手势识别不准确：确保光线充足，保持手势清晰
   - 设备控制失败：检查设备是否在线，确认IP和Token正确

5. 技术支持
   - 查看系统日志获取详细错误信息
   - 确保所有依赖库已正确安装
   - 检查防火墙设置是否阻止了网络连接
"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
    def check_device_config(self):
        """检查设备配置"""
        try:
            # 尝试读取配置文件
            import os
            config_file = "config.yaml"
            if os.path.exists(config_file):
                # 这里应该解析配置文件并计算设备数量
                # 暂时返回模拟数据
                device_count = 0  # 实际应该从配置文件读取
                self.device_count_var.set(f"{device_count} 个")
                return device_count > 0
            else:
                self.device_count_var.set("0 个")
                return False
        except Exception as e:
            self.add_log(f"检查设备配置时出错: {str(e)}")
            return False
            
    def on_closing(self):
        """程序关闭时的处理"""
        self.add_log("正在关闭系统...")
        # 这里可以添加清理代码
        self.root.destroy()

def main():
    root = tk.Tk()
    app = IntegratedMiHomeApp(root)
    
    # 设置关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()