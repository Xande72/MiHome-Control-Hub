import miio
import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """设备类型枚举"""
    LIGHT = "light"
    CEILING_LIGHT = "ceiling_light"
    DESK_LAMP = "desk_lamp"
    BULB = "bulb"
    STRIP = "strip"
    UNKNOWN = "unknown"

@dataclass
class DeviceInfo:
    """设备信息数据类"""
    name: str
    device_type: DeviceType
    ip: str
    token: str
    model: str = ""
    did: str = ""
    mac: str = ""
    online: bool = False
    brightness: int = 0
    power: bool = False
    color_temp: int = 0

class MiHomeDevice:
    """米家设备基类"""
    
    def __init__(self, device_info: DeviceInfo):
        self.device_info = device_info
        self.device = None
        self._connect()
    
    def _connect(self):
        """连接设备"""
        try:
            self.device = miio.Device(self.device_info.ip, self.device_info.token)
            self.device_info.online = True
            logger.info(f"成功连接设备: {self.device_info.name}")
        except Exception as e:
            self.device_info.online = False
            logger.error(f"连接设备失败 {self.device_info.name}: {str(e)}")
    
    def is_online(self) -> bool:
        """检查设备是否在线"""
        try:
            if self.device:
                # 设置较短的超时时间避免卡顿
                import socket
                original_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(3)  # 3秒超时
                
                try:
                    info = self.device.info()
                    self.device_info.online = True
                    return True
                finally:
                    socket.setdefaulttimeout(original_timeout)
        except Exception as e:
            self.device_info.online = False
            logger.warning(f"设备 {self.device_info.name} 离线: {str(e)}")
        return False
    
    def send_command(self, command: str, parameters: List = None) -> Any:
        """发送命令到设备"""
        if not self.device:
            logger.error(f"设备 {self.device_info.name} 未连接")
            return None
        
        try:
            if parameters:
                result = self.device.send(command, parameters)
            else:
                result = self.device.send(command)
            logger.info(f"命令发送成功 {self.device_info.name}: {command}")
            return result
        except Exception as e:
            logger.error(f"命令发送失败 {self.device_info.name}: {str(e)}")
            return None

class LightDevice(MiHomeDevice):
    """灯具设备类"""
    
    def turn_on(self) -> bool:
        """打开设备"""
        result = self.send_command("set_power", ["on"])
        if result and result[0] == "ok":
            self.device_info.power = True
            logger.info(f"设备 {self.device_info.name} 已打开")
            return True
        return False
    
    def turn_off(self) -> bool:
        """关闭设备"""
        result = self.send_command("set_power", ["off"])
        if result and result[0] == "ok":
            self.device_info.power = False
            logger.info(f"设备 {self.device_info.name} 已关闭")
            return True
        return False
    
    def set_brightness(self, brightness: int) -> bool:
        """设置亮度 (1-100)"""
        if not 1 <= brightness <= 100:
            logger.error(f"亮度值无效: {brightness}，应在1-100之间")
            return False
        
        # 对于Yeelight设备，使用set_scene命令设置亮度
        # 参数：['color', RGB颜色值, 亮度]
        # 使用白色(16777215)作为默认颜色
        result = self.send_command("set_scene", ["color", 16777215, brightness])
        if result and result[0] == "ok":
            self.device_info.brightness = brightness
            logger.info(f"设备 {self.device_info.name} 亮度设置为 {brightness}%")
            return True
        return False
    
    def adjust_brightness(self, delta: int) -> bool:
        """调整亮度"""
        current_brightness = self.get_brightness()
        if current_brightness is None:
            return False
        
        new_brightness = max(1, min(100, current_brightness + delta))
        return self.set_brightness(new_brightness)
    
    def get_brightness(self) -> Optional[int]:
        """获取当前亮度"""
        try:
            result = self.send_command("get_prop", ["bright"])
            if result:
                brightness = int(result[0])  # 确保转换为整数
                self.device_info.brightness = brightness
                return brightness
        except Exception as e:
            logger.error(f"获取亮度失败 {self.device_info.name}: {str(e)}")
        return None
    
    def set_color_temp(self, temp: int) -> bool:
        """设置色温 (1700-6500K)"""
        if not 1700 <= temp <= 6500:
            logger.error(f"色温值无效: {temp}，应在1700-6500之间")
            return False
        
        result = self.send_command("set_ct_abx", [temp, "smooth", 500])
        if result and result[0] == "ok":
            self.device_info.color_temp = temp
            logger.info(f"设备 {self.device_info.name} 色温设置为 {temp}K")
            return True
        return False
    
    def adjust_color_temp(self, delta: int) -> bool:
        """调整色温"""
        try:
            # 获取当前色温
            result = self.send_command("get_prop", ["ct"])
            if result:
                current_temp = int(result[0])
                # 如果当前色温值异常（如65535），使用默认值3000K
                if current_temp > 6500 or current_temp < 1700:
                    logger.warning(f"设备 {self.device_info.name} 色温值异常: {current_temp}，使用默认值3000K")
                    current_temp = 3000
                
                new_temp = max(1700, min(6500, current_temp + delta))
                return self.set_color_temp(new_temp)
        except Exception as e:
            logger.error(f"调整色温失败 {self.device_info.name}: {str(e)}")
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取设备状态"""
        try:
            result = self.send_command("get_prop", ["power", "bright", "ct"])
            if result and len(result) >= 3:
                self.device_info.power = result[0] == "on"
                self.device_info.brightness = int(result[1])  # 确保转换为整数
                self.device_info.color_temp = int(result[2])  # 确保转换为整数
                
                return {
                    "power": self.device_info.power,
                    "brightness": self.device_info.brightness,
                    "color_temp": self.device_info.color_temp,
                    "online": self.device_info.online
                }
        except Exception as e:
            logger.error(f"获取状态失败 {self.device_info.name}: {str(e)}")
        
        return {
            "power": False,
            "brightness": 0,
            "color_temp": 0,
            "online": False
        }

class DeviceController:
    """设备控制器主类"""
    
    def __init__(self):
        self.devices: Dict[str, MiHomeDevice] = {}
        self.config_file = "config.yaml"
    
    def load_config(self, config_file: str = None) -> bool:
        """加载配置文件"""
        if config_file:
            self.config_file = config_file
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if 'devices' not in config:
                logger.error("配置文件中未找到设备信息")
                return False
            
            self._load_devices_from_config(config['devices'])
            logger.info(f"成功加载 {len(self.devices)} 个设备")
            return True
            
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_file}")
            return False
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return False
    
    def load_from_json(self, json_file: str) -> bool:
        """从JSON文件加载设备配置"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'devices' not in data:
                logger.error("JSON文件中未找到设备信息")
                return False
            
            self._load_devices_from_json(data['devices'])
            logger.info(f"成功从JSON加载 {len(self.devices)} 个设备")
            return True
            
        except FileNotFoundError:
            logger.error(f"JSON文件未找到: {json_file}")
            return False
        except Exception as e:
            logger.error(f"加载JSON文件失败: {str(e)}")
            return False
    
    def _load_devices_from_config(self, devices_config: Dict):
        """从配置加载设备"""
        for name, config in devices_config.items():
            try:
                device_type = DeviceType(config.get('type', 'light'))
                device_info = DeviceInfo(
                    name=name,
                    device_type=device_type,
                    ip=config['ip'],
                    token=config['token'],
                    model=config.get('model', ''),
                    did=config.get('did', ''),
                    mac=config.get('mac', '')
                )
                
                # 根据设备类型创建相应的设备对象
                if device_type in [DeviceType.LIGHT, DeviceType.CEILING_LIGHT, 
                                 DeviceType.DESK_LAMP, DeviceType.BULB]:
                    device = LightDevice(device_info)
                    self.devices[name] = device
                elif device_type == DeviceType.UNKNOWN:
                    # 对于未知类型的设备，创建基础设备对象
                    device = MiHomeDevice(device_info)
                    self.devices[name] = device
                    
            except Exception as e:
                logger.error(f"加载设备失败 {name}: {str(e)}")
    
    def _load_devices_from_json(self, devices_data: Dict):
        """从JSON数据加载设备"""
        for name, data in devices_data.items():
            try:
                device_type = DeviceType(data.get('type', 'light'))
                device_info = DeviceInfo(
                    name=name,
                    device_type=device_type,
                    ip=data['ip'],
                    token=data['token'],
                    model=data.get('model', ''),
                    did=data.get('did', ''),
                    mac=data.get('mac', '')
                )
                
                # 根据设备类型创建相应的设备对象
                if device_type in [DeviceType.LIGHT, DeviceType.CEILING_LIGHT, 
                                 DeviceType.DESK_LAMP, DeviceType.BULB]:
                    device = LightDevice(device_info)
                    self.devices[name] = device
                elif device_type == DeviceType.UNKNOWN:
                    # 对于未知类型的设备，创建基础设备对象
                    device = MiHomeDevice(device_info)
                    self.devices[name] = device
                    
            except Exception as e:
                logger.error(f"加载设备失败 {name}: {str(e)}")
    
    def get_device(self, name: str) -> Optional[MiHomeDevice]:
        """获取指定设备"""
        return self.devices.get(name)
    
    def get_all_devices(self) -> Dict[str, MiHomeDevice]:
        """获取所有设备"""
        return self.devices
    
    def turn_on_all(self) -> Dict[str, bool]:
        """打开所有设备"""
        results = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                results[name] = device.turn_on()
        logger.info("执行打开所有设备命令")
        return results
    
    def turn_off_all(self) -> Dict[str, bool]:
        """关闭所有设备"""
        results = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                results[name] = device.turn_off()
        logger.info("执行关闭所有设备命令")
        return results
    
    def adjust_brightness_all(self, delta: int) -> Dict[str, bool]:
        """调整所有设备亮度"""
        results = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                results[name] = device.adjust_brightness(delta)
        logger.info(f"执行调整所有设备亮度命令: {delta:+d}%")
        return results
    
    def set_color_temp_all(self, temp: int) -> Dict[str, bool]:
        """设置所有设备色温"""
        results = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                results[name] = device.set_color_temp(temp)
        logger.info(f"执行设置所有设备色温命令: {temp}K")
        return results
    
    def adjust_color_temp_all(self, delta: int) -> Dict[str, bool]:
        """调整所有设备色温"""
        results = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                # 获取当前色温
                current_temp = device.device_info.color_temp
                if current_temp == 0:  # 如果没有当前色温信息，先获取状态
                    device.get_status()
                    current_temp = device.device_info.color_temp
                
                # 计算新色温，确保在有效范围内
                new_temp = max(1700, min(6500, current_temp + delta))
                results[name] = device.set_color_temp(new_temp)
        logger.info(f"执行调整所有设备色温命令: {delta:+d}K")
        return results
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有设备状态"""
        status = {}
        for name, device in self.devices.items():
            if isinstance(device, LightDevice):
                status[name] = device.get_status()
        return status
    
    def check_all_online(self) -> Dict[str, bool]:
        """检查所有设备在线状态"""
        online_status = {}
        for name, device in self.devices.items():
            online_status[name] = device.is_online()
        return online_status

# 测试代码
if __name__ == "__main__":
    # 创建设备控制器
    controller = DeviceController()
    
    # 从JSON文件加载设备
    if controller.load_from_json("light.json"):
        print("设备加载成功")
        
        # 获取所有设备状态
        status = controller.get_all_status()
        print("设备状态:", status)
        
        # 测试控制命令
        print("\n测试打开所有设备...")
        controller.turn_on_all()
        
        print("\n测试调整亮度...")
        controller.adjust_brightness_all(20)
        
        print("\n测试关闭所有设备...")
        controller.turn_off_all()
    else:
        print("设备加载失败")