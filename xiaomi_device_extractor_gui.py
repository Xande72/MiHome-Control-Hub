import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import base64
from PIL import Image, ImageTk
import io
import requests
from token_extractor import XiaomiCloudConnector, SERVERS

class XiaomiDeviceExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("小米设备Token提取器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 数据存储
        self.connector = None
        self.devices_data = []
        self.selected_devices = []
        
        # 创建主界面
        self.create_main_interface()
        
    def create_main_interface(self):
        """创建主界面"""
        # 创建notebook用于标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 登录标签页
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="账户登录")
        self.create_login_interface()
        
        # 设备列表标签页
        self.devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.devices_frame, text="设备列表")
        self.create_devices_interface()
        
        # 日志标签页
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="操作日志")
        self.create_log_interface()
        
    def create_login_interface(self):
        """创建登录界面"""
        # 主框架
        main_frame = ttk.Frame(self.login_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="小米账户登录", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 登录表单框架
        form_frame = ttk.LabelFrame(main_frame, text="登录信息", padding=20)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 用户名
        ttk.Label(form_frame, text="用户名 (邮箱/手机号/用户ID):").pack(anchor=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=50)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 密码
        ttk.Label(form_frame, text="密码:").pack(anchor=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=50)
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # 服务器选择
        ttk.Label(form_frame, text="服务器区域:").pack(anchor=tk.W, pady=(0, 5))
        self.server_var = tk.StringVar(value="cn")
        server_frame = ttk.Frame(form_frame)
        server_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.server_combo = ttk.Combobox(server_frame, textvariable=self.server_var, 
                                        values=SERVERS, state="readonly", width=20)
        self.server_combo.pack(side=tk.LEFT)
        
        ttk.Label(server_frame, text="  (留空检查所有可用服务器)").pack(side=tk.LEFT)
        
        # 登录按钮
        self.login_button = ttk.Button(form_frame, text="开始登录", command=self.start_login)
        self.login_button.pack(pady=(10, 0))
        
        # 状态显示
        self.status_var = tk.StringVar(value="请输入登录信息")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.pack(pady=(10, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
    def create_devices_interface(self):
        """创建设备列表界面"""
        # 主框架
        main_frame = ttk.Frame(self.devices_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题和操作按钮
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="发现的设备列表", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # 操作按钮
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.refresh_button = ttk.Button(button_frame, text="刷新设备", command=self.refresh_devices)
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="导出选中设备", command=self.export_selected_devices)
        self.export_button.pack(side=tk.LEFT)
        
        # 设备列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('选择', '名称', 'ID', 'IP', 'Token', '型号')
        self.devices_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        self.devices_tree.heading('选择', text='选择')
        self.devices_tree.heading('名称', text='设备名称')
        self.devices_tree.heading('ID', text='设备ID')
        self.devices_tree.heading('IP', text='IP地址')
        self.devices_tree.heading('Token', text='Token')
        self.devices_tree.heading('型号', text='设备型号')
        
        self.devices_tree.column('选择', width=60, anchor=tk.CENTER)
        self.devices_tree.column('名称', width=150)
        self.devices_tree.column('ID', width=120)
        self.devices_tree.column('IP', width=120)
        self.devices_tree.column('Token', width=200)
        self.devices_tree.column('型号', width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.devices_tree.yview)
        self.devices_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.devices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.devices_tree.bind('<Double-1>', self.toggle_device_selection)
        
        # 底部信息
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.devices_info_var = tk.StringVar(value="请先登录获取设备列表")
        ttk.Label(info_frame, textvariable=self.devices_info_var).pack(side=tk.LEFT)
        
    def create_log_interface(self):
        """创建日志界面"""
        # 主框架
        main_frame = ttk.Frame(self.log_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ttk.Label(main_frame, text="操作日志", font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 清除按钮
        clear_button = ttk.Button(main_frame, text="清除日志", command=self.clear_log)
        clear_button.pack(pady=(10, 0))
        
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
        
    def update_status(self, message, color="blue"):
        """更新状态信息"""
        self.status_var.set(message)
        self.status_label.config(foreground=color)
        self.log_message(f"状态: {message}")
        
    def start_login(self):
        """开始登录流程"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return
            
        # 禁用登录按钮，显示进度条
        self.login_button.config(state="disabled")
        self.progress.start()
        self.update_status("正在登录...", "blue")
        
        # 在新线程中执行登录
        threading.Thread(target=self.login_thread, args=(username, password), daemon=True).start()
        
    def login_thread(self, username, password):
        """登录线程"""
        try:
            self.connector = XiaomiCloudConnector(username, password)
            
            # 执行登录步骤
            self.root.after(0, lambda: self.update_status("正在验证账户信息...", "blue"))
            
            if self.connector.login_step_1():
                self.root.after(0, lambda: self.update_status("正在进行身份验证...", "blue"))
                
                # 修改login_step_2以支持GUI交互
                if self.login_step_2_gui():
                    self.root.after(0, lambda: self.update_status("正在获取服务令牌...", "blue"))
                    
                    if self.connector.login_step_3():
                        self.root.after(0, lambda: self.update_status("登录成功！正在获取设备列表...", "green"))
                        self.root.after(0, self.get_devices)
                    else:
                        self.root.after(0, lambda: self.login_failed("无法获取服务令牌"))
                else:
                    self.root.after(0, lambda: self.login_failed("身份验证失败"))
            else:
                self.root.after(0, lambda: self.login_failed("无效的用户名"))
                
        except Exception as e:
            self.root.after(0, lambda: self.login_failed(f"登录过程中发生错误: {str(e)}"))
            
    def login_failed(self, message):
        """登录失败处理"""
        self.update_status(f"登录失败: {message}", "red")
        self.progress.stop()
        self.login_button.config(state="normal")
        
    def get_devices(self):
        """获取设备列表"""
        threading.Thread(target=self.get_devices_thread, daemon=True).start()
        
    def get_devices_thread(self):
        """获取设备列表线程"""
        try:
            self.devices_data = []
            server = self.server_var.get() if self.server_var.get() else "cn"
            
            self.root.after(0, lambda: self.update_status(f"正在从服务器 {server} 获取设备...", "blue"))
            
            # 获取家庭列表
            all_homes = []
            homes = self.connector.get_homes(server)
            if homes is not None:
                for h in homes['result']['homelist']:
                    all_homes.append({'home_id': h['id'], 'home_owner': self.connector.userId})
                    
            dev_cnt = self.connector.get_dev_cnt(server)
            if dev_cnt is not None:
                for h in dev_cnt["result"]["share"]["share_family"]:
                    all_homes.append({'home_id': h['home_id'], 'home_owner': h['home_owner']})
                    
            if len(all_homes) == 0:
                self.root.after(0, lambda: self.update_status(f"在服务器 {server} 上未找到家庭", "orange"))
                return
                
            # 获取每个家庭的设备
            total_devices = 0
            for home in all_homes:
                devices = self.connector.get_devices(server, home['home_id'], home['home_owner'])
                if devices is not None and devices["result"]["device_info"] is not None:
                    for device in devices["result"]["device_info"]:
                        device_data = {
                            'name': device.get('name', '未知设备'),
                            'did': device.get('did', ''),
                            'mac': device.get('mac', ''),
                            'localip': device.get('localip', ''),
                            'token': device.get('token', ''),
                            'model': device.get('model', ''),
                            'server': server,
                            'home_id': home['home_id'],
                            'selected': False
                        }
                        self.devices_data.append(device_data)
                        total_devices += 1
                        
            self.root.after(0, lambda: self.update_devices_display())
            self.root.after(0, lambda: self.update_status(f"成功获取 {total_devices} 个设备", "green"))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.login_button.config(state="normal"))
            
        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"获取设备失败: {str(e)}", "red"))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.login_button.config(state="normal"))
            
    def update_devices_display(self):
        """更新设备显示"""
        # 清空现有数据
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
            
        # 添加设备数据
        for i, device in enumerate(self.devices_data):
            selected = "✓" if device['selected'] else ""
            self.devices_tree.insert('', tk.END, iid=i, values=(
                selected,
                device['name'],
                device['did'],
                device['localip'],
                device['token'][:20] + '...' if len(device['token']) > 20 else device['token'],
                device['model']
            ))
            
        # 更新信息
        total = len(self.devices_data)
        selected = sum(1 for d in self.devices_data if d['selected'])
        self.devices_info_var.set(f"总共 {total} 个设备，已选择 {selected} 个")
        
        # 切换到设备列表标签页
        self.notebook.select(self.devices_frame)
        
    def toggle_device_selection(self, event):
        """切换设备选择状态"""
        item = self.devices_tree.selection()[0]
        index = int(item)
        
        # 切换选择状态
        self.devices_data[index]['selected'] = not self.devices_data[index]['selected']
        
        # 更新显示
        self.update_devices_display()
        
    def refresh_devices(self):
        """刷新设备列表"""
        if self.connector is None:
            messagebox.showwarning("警告", "请先登录")
            return
            
        self.get_devices()
        
    def export_selected_devices(self):
        """导出选中的设备"""
        selected_devices = [d for d in self.devices_data if d['selected']]
        
        if not selected_devices:
            messagebox.showwarning("警告", "请先选择要导出的设备")
            return
            
        # 创建导出窗口
        self.show_export_dialog(selected_devices)
        
    def show_export_dialog(self, devices):
        """显示导出对话框"""
        export_window = tk.Toplevel(self.root)
        export_window.title("导出设备配置")
        export_window.geometry("600x400")
        export_window.transient(self.root)
        export_window.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(export_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ttk.Label(main_frame, text="设备配置信息", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # 配置文本
        config_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15)
        config_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 生成配置内容
        config_content = self.generate_config_content(devices)
        config_text.insert(tk.END, config_content)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 保存到文件按钮
        def save_to_file():
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(config_content)
                    messagebox.showinfo("成功", f"配置已保存到: {filename}")
                    export_window.destroy()
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {str(e)}")
                    
        ttk.Button(button_frame, text="保存到文件", command=save_to_file).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="关闭", command=export_window.destroy).pack(side=tk.LEFT)
        
    def generate_config_content(self, devices):
        """生成配置文件内容"""
        config = {
            "devices": {},
            "extraction_info": {
                "total_devices": len(devices),
                "server": self.server_var.get() or "cn",
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
        }
        
        for device in devices:
            device_name = device['name'] or f"Device_{device['did'][:8]}"
            config["devices"][device_name] = {
                "type": "light" if "light" in device['model'].lower() else "unknown",
                "ip": device['localip'],
                "token": device['token'],
                "model": device['model'],
                "did": device['did'],
                "mac": device['mac']
            }
            
        return json.dumps(config, indent=4, ensure_ascii=False)
    
    def login_step_2_gui(self):
        """GUI版本的login_step_2，支持验证码和2FA"""
        import hashlib
        
        url = "https://account.xiaomi.com/pass/serviceLoginAuth2"
        headers = {
            "User-Agent": self.connector._agent,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        fields = {
            "sid": "xiaomiio",
            "hash": hashlib.md5(str.encode(self.connector._password)).hexdigest().upper(),
            "callback": "https://sts.api.io.mi.com/sts",
            "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
            "user": self.connector._username,
            "_sign": self.connector._sign,
            "_json": "true"
        }
        
        response = self.connector._session.post(url, headers=headers, params=fields, allow_redirects=False)
        
        if response is not None and response.status_code == 200:
            json_resp = self.connector.to_json(response.text)
            
            # 处理验证码
            if "captchaUrl" in json_resp and json_resp["captchaUrl"] is not None:
                captcha_code = self.handle_captcha_gui(json_resp["captchaUrl"])
                if not captcha_code:
                    return False
                    
                fields["captCode"] = captcha_code
                response = self.connector._session.post(url, headers=headers, params=fields, allow_redirects=False)
                if response is not None and response.status_code == 200:
                    json_resp = self.connector.to_json(response.text)
                else:
                    return False
                    
                if "code" in json_resp and json_resp["code"] == 87001:
                    self.root.after(0, lambda: messagebox.showerror("错误", "验证码错误"))
                    return False
            
            # 检查是否需要2FA
            if "notificationUrl" in json_resp:
                return self.handle_2fa_gui(json_resp["notificationUrl"])
            
            # 正常登录成功
            if "ssecurity" in json_resp and len(str(json_resp["ssecurity"])) > 4:
                self.connector._ssecurity = json_resp["ssecurity"]
                self.connector.userId = json_resp.get("userId", None)
                self.connector._cUserId = json_resp.get("cUserId", None)
                self.connector._passToken = json_resp.get("passToken", None)
                self.connector._location = json_resp.get("location", None)
                self.connector._code = json_resp.get("code", None)
                return True
                
        return False
    
    def handle_captcha_gui(self, captcha_url):
        """GUI版本的验证码处理"""
        if captcha_url.startswith("/"):
            captcha_url = "https://account.xiaomi.com" + captcha_url
            
        try:
            response = self.connector._session.get(captcha_url, stream=False)
            if response.status_code != 200:
                return None
                
            # 在主线程中显示验证码对话框
            result = [None]  # 使用列表来存储结果，因为需要在闭包中修改
            
            def show_captcha():
                result[0] = self.show_captcha_dialog(response.content)
                
            self.root.after(0, show_captcha)
            
            # 等待用户输入
            while result[0] is None:
                self.root.update()
                __import__('time').sleep(0.1)
                
            return result[0]
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"获取验证码失败: {str(e)}"))
            return None
    
    def show_captcha_dialog(self, image_data):
        """显示验证码对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("验证码验证")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = [None]
        
        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ttk.Label(main_frame, text="请输入验证码", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # 显示验证码图片
        try:
            image = Image.open(io.BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)
            image_label = ttk.Label(main_frame, image=photo)
            image_label.image = photo  # 保持引用
            image_label.pack(pady=(0, 20))
        except Exception as e:
            ttk.Label(main_frame, text=f"无法显示验证码图片: {str(e)}").pack(pady=(0, 20))
        
        # 输入框
        ttk.Label(main_frame, text="验证码 (区分大小写):").pack(anchor=tk.W)
        captcha_var = tk.StringVar()
        captcha_entry = ttk.Entry(main_frame, textvariable=captcha_var, width=30)
        captcha_entry.pack(fill=tk.X, pady=(5, 20))
        captcha_entry.focus()
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            result[0] = captcha_var.get().strip()
            dialog.destroy()
            
        def on_cancel():
            result[0] = ""
            dialog.destroy()
        
        ttk.Button(button_frame, text="确认", command=on_confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.LEFT)
        
        # 绑定回车键
        captcha_entry.bind('<Return>', lambda e: on_confirm())
        
        # 等待对话框关闭
        dialog.wait_window()
        
        return result[0] if result[0] else None
    
    def handle_2fa_gui(self, verify_url):
        """GUI版本的2FA处理"""
        # 在主线程中显示2FA对话框
        result = [None]
        
        def show_2fa():
            result[0] = self.show_2fa_dialog(verify_url)
            
        self.root.after(0, show_2fa)
        
        # 等待用户输入
        while result[0] is None:
            self.root.update()
            __import__('time').sleep(0.1)
            
        if result[0]:
            # 验证2FA代码
            json_resp = self.connector.verify_ticket(verify_url, result[0])
            if json_resp:
                location = json_resp["location"]
                self.connector._session.get(location, allow_redirects=True)
                self.connector.login_step_1()
                return True
                
        return False
    
    def show_2fa_dialog(self, verify_url):
        """显示2FA对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("双因子认证")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        result = [None]
        
        # 主框架
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        ttk.Label(main_frame, text="双因子认证", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # 说明文本
        info_text = (
            "需要进行双因子认证。\n\n"
            "请使用以下URL获取2FA验证码："
        )
        
        info_label = ttk.Label(main_frame, text=info_text, wraplength=450, justify=tk.LEFT)
        info_label.pack(pady=(0, 10))
        
        # URL显示和操作按钮框架
        url_frame = ttk.LabelFrame(main_frame, text="验证链接", padding=10)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        # URL文本框
        url_text = tk.Text(url_frame, height=3, wrap=tk.WORD, font=("Arial", 9))
        url_text.pack(fill=tk.X, pady=(0, 10))
        url_text.insert(tk.END, verify_url)
        url_text.config(state=tk.DISABLED)
        
        # 操作按钮框架
        url_button_frame = ttk.Frame(url_frame)
        url_button_frame.pack(fill=tk.X)
        
        # 复制链接按钮
        def copy_url():
            dialog.clipboard_clear()
            dialog.clipboard_append(verify_url)
            messagebox.showinfo("提示", "链接已复制到剪贴板")
        
        copy_button = ttk.Button(url_button_frame, text="📋 复制链接", command=copy_url)
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 打开浏览器按钮
        def open_browser():
            import webbrowser
            try:
                webbrowser.open(verify_url)
                messagebox.showinfo("提示", "已在默认浏览器中打开链接")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开浏览器：{str(e)}")
        
        browser_button = ttk.Button(url_button_frame, text="🌐 在浏览器中打开", command=open_browser)
        browser_button.pack(side=tk.LEFT)
        
        # 警告信息
        warning_label = ttk.Label(main_frame, text="⚠️ 重要：请不要在小米网站上输入验证码！只需获取验证码并在下方输入框中输入。", 
                                 wraplength=450, justify=tk.LEFT, foreground="red")
        warning_label.pack(pady=(0, 20))
        
        # 输入框
        ttk.Label(main_frame, text="2FA验证码:").pack(anchor=tk.W)
        code_var = tk.StringVar()
        code_entry = ttk.Entry(main_frame, textvariable=code_var, width=30)
        code_entry.pack(fill=tk.X, pady=(5, 20))
        code_entry.focus()
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def on_confirm():
            result[0] = code_var.get().strip()
            dialog.destroy()
            
        def on_cancel():
            result[0] = ""
            dialog.destroy()
        
        ttk.Button(button_frame, text="确认", command=on_confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.LEFT)
        
        # 绑定回车键
        code_entry.bind('<Return>', lambda e: on_confirm())
        
        # 等待对话框关闭
        dialog.wait_window()
        
        return result[0] if result[0] else None

def main():
    root = tk.Tk()
    app = XiaomiDeviceExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()