import yaml
import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DeviceConfig:
    """设备配置数据类"""
    name: str
    type: str
    ip: str
    token: str
    model: str = ""
    did: str = ""
    mac: str = ""
    enabled: bool = True
    room: str = "默认房间"
    description: str = ""

@dataclass
class GestureConfig:
    """手势配置数据类"""
    enabled: bool = True
    camera_index: int = 0
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    gesture_stability_frames: int = 5
    brightness_step: int = 20

@dataclass
class SystemConfig:
    """系统配置数据类"""
    log_level: str = "INFO"
    auto_discovery: bool = True
    discovery_timeout: int = 30
    device_timeout: int = 5
    ui_theme: str = "light"
    language: str = "zh_CN"

@dataclass
class AppConfig:
    """应用配置主类"""
    devices: Dict[str, DeviceConfig]
    gesture: GestureConfig
    system: SystemConfig
    version: str = "1.0.0"

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.config: Optional[AppConfig] = None
        self._default_config = self._create_default_config()
    
    def _create_default_config(self) -> AppConfig:
        """创建默认配置"""
        return AppConfig(
            devices={},
            gesture=GestureConfig(),
            system=SystemConfig()
        )
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_file}")
                self.config = self._default_config
                return self.save_config()  # 创建默认配置文件
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning("配置文件为空，使用默认配置")
                self.config = self._default_config
                return True
            
            # 解析配置
            self.config = self._parse_config(data)
            logger.info(f"成功加载配置文件: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self.config = self._default_config
            return False
    
    def _parse_config(self, data: Dict) -> AppConfig:
        """解析配置数据"""
        try:
            # 解析设备配置
            devices = {}
            if 'devices' in data:
                for name, device_data in data['devices'].items():
                    devices[name] = DeviceConfig(
                        name=name,
                        type=device_data.get('type', 'light'),
                        ip=device_data.get('ip', ''),
                        token=device_data.get('token', ''),
                        model=device_data.get('model', ''),
                        did=device_data.get('did', ''),
                        mac=device_data.get('mac', ''),
                        enabled=device_data.get('enabled', True),
                        room=device_data.get('room', '默认房间'),
                        description=device_data.get('description', '')
                    )
            
            # 解析手势配置
            gesture_data = data.get('gesture', {})
            gesture = GestureConfig(
                enabled=gesture_data.get('enabled', True),
                camera_index=gesture_data.get('camera_index', 0),
                min_detection_confidence=gesture_data.get('min_detection_confidence', 0.7),
                min_tracking_confidence=gesture_data.get('min_tracking_confidence', 0.5),
                gesture_stability_frames=gesture_data.get('gesture_stability_frames', 5),
                brightness_step=gesture_data.get('brightness_step', 20)
            )
            
            # 解析系统配置
            system_data = data.get('system', {})
            system = SystemConfig(
                log_level=system_data.get('log_level', 'INFO'),
                auto_discovery=system_data.get('auto_discovery', True),
                discovery_timeout=system_data.get('discovery_timeout', 30),
                device_timeout=system_data.get('device_timeout', 5),
                ui_theme=system_data.get('ui_theme', 'light'),
                language=system_data.get('language', 'zh_CN')
            )
            
            return AppConfig(
                devices=devices,
                gesture=gesture,
                system=system,
                version=data.get('version', '1.0.0')
            )
            
        except Exception as e:
            logger.error(f"解析配置数据失败: {str(e)}")
            return self._default_config
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            if not self.config:
                logger.error("没有配置数据可保存")
                return False
            
            # 转换为字典格式
            config_dict = self._config_to_dict()
            
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logger.info(f"配置文件已保存: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _config_to_dict(self) -> Dict:
        """将配置转换为字典格式"""
        if not self.config:
            return {}
        
        config_dict = {
            'version': self.config.version,
            'devices': {},
            'gesture': asdict(self.config.gesture),
            'system': asdict(self.config.system)
        }
        
        # 转换设备配置
        for name, device in self.config.devices.items():
            config_dict['devices'][name] = asdict(device)
            # 移除name字段（已经是key了）
            del config_dict['devices'][name]['name']
        
        return config_dict
    
    def load_from_json(self, json_file: str) -> bool:
        """从JSON文件导入设备配置"""
        try:
            json_path = Path(json_file)
            if not json_path.exists():
                logger.error(f"JSON文件不存在: {json_file}")
                return False
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'devices' not in data:
                logger.error("JSON文件中未找到设备信息")
                return False
            
            # 确保配置已初始化
            if not self.config:
                self.config = self._default_config
            
            # 导入设备配置
            imported_count = 0
            for name, device_data in data['devices'].items():
                try:
                    device_config = DeviceConfig(
                        name=name,
                        type=device_data.get('type', 'light'),
                        ip=device_data.get('ip', ''),
                        token=device_data.get('token', ''),
                        model=device_data.get('model', ''),
                        did=device_data.get('did', ''),
                        mac=device_data.get('mac', ''),
                        enabled=True,
                        room=device_data.get('room', '默认房间'),
                        description=f"从{json_file}导入"
                    )
                    
                    self.config.devices[name] = device_config
                    imported_count += 1
                    
                except Exception as e:
                    logger.warning(f"导入设备失败 {name}: {str(e)}")
            
            logger.info(f"成功从JSON导入 {imported_count} 个设备")
            return imported_count > 0
            
        except Exception as e:
            logger.error(f"从JSON导入失败: {str(e)}")
            return False
    
    def add_device(self, device_config: DeviceConfig) -> bool:
        """添加设备配置"""
        try:
            if not self.config:
                self.config = self._default_config
            
            self.config.devices[device_config.name] = device_config
            logger.info(f"已添加设备配置: {device_config.name}")
            return True
            
        except Exception as e:
            logger.error(f"添加设备配置失败: {str(e)}")
            return False
    
    def remove_device(self, device_name: str) -> bool:
        """移除设备配置"""
        try:
            if not self.config or device_name not in self.config.devices:
                logger.warning(f"设备不存在: {device_name}")
                return False
            
            del self.config.devices[device_name]
            logger.info(f"已移除设备配置: {device_name}")
            return True
            
        except Exception as e:
            logger.error(f"移除设备配置失败: {str(e)}")
            return False
    
    def update_device(self, device_name: str, **kwargs) -> bool:
        """更新设备配置"""
        try:
            if not self.config or device_name not in self.config.devices:
                logger.warning(f"设备不存在: {device_name}")
                return False
            
            device = self.config.devices[device_name]
            for key, value in kwargs.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            
            logger.info(f"已更新设备配置: {device_name}")
            return True
            
        except Exception as e:
            logger.error(f"更新设备配置失败: {str(e)}")
            return False
    
    def get_device_config(self, device_name: str) -> Optional[DeviceConfig]:
        """获取设备配置"""
        if self.config and device_name in self.config.devices:
            return self.config.devices[device_name]
        return None
    
    def get_all_devices(self) -> Dict[str, DeviceConfig]:
        """获取所有设备配置"""
        if self.config:
            return self.config.devices
        return {}
    
    def get_enabled_devices(self) -> Dict[str, DeviceConfig]:
        """获取启用的设备配置"""
        if not self.config:
            return {}
        
        return {name: device for name, device in self.config.devices.items() 
                if device.enabled}
    
    def get_gesture_config(self) -> GestureConfig:
        """获取手势配置"""
        if self.config:
            return self.config.gesture
        return GestureConfig()
    
    def update_gesture_config(self, **kwargs) -> bool:
        """更新手势配置"""
        try:
            if not self.config:
                self.config = self._default_config
            
            for key, value in kwargs.items():
                if hasattr(self.config.gesture, key):
                    setattr(self.config.gesture, key, value)
            
            logger.info("已更新手势配置")
            return True
            
        except Exception as e:
            logger.error(f"更新手势配置失败: {str(e)}")
            return False
    
    def get_system_config(self) -> SystemConfig:
        """获取系统配置"""
        if self.config:
            return self.config.system
        return SystemConfig()
    
    def update_system_config(self, **kwargs) -> bool:
        """更新系统配置"""
        try:
            if not self.config:
                self.config = self._default_config
            
            for key, value in kwargs.items():
                if hasattr(self.config.system, key):
                    setattr(self.config.system, key, value)
            
            logger.info("已更新系统配置")
            return True
            
        except Exception as e:
            logger.error(f"更新系统配置失败: {str(e)}")
            return False
    
    def export_to_json(self, json_file: str) -> bool:
        """导出配置到JSON文件"""
        try:
            if not self.config:
                logger.error("没有配置数据可导出")
                return False
            
            export_data = {
                'version': self.config.version,
                'devices': {}
            }
            
            # 导出设备配置
            for name, device in self.config.devices.items():
                export_data['devices'][name] = {
                    'type': device.type,
                    'ip': device.ip,
                    'token': device.token,
                    'model': device.model,
                    'did': device.did,
                    'mac': device.mac,
                    'room': device.room,
                    'description': device.description
                }
            
            json_path = Path(json_file)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置已导出到: {json_file}")
            return True
            
        except Exception as e:
            logger.error(f"导出配置失败: {str(e)}")
            return False
    
    def validate_config(self) -> List[str]:
        """验证配置有效性"""
        errors = []
        
        if not self.config:
            errors.append("配置未加载")
            return errors
        
        # 验证设备配置
        for name, device in self.config.devices.items():
            if not device.ip:
                errors.append(f"设备 {name} 缺少IP地址")
            if not device.token:
                errors.append(f"设备 {name} 缺少Token")
            if not device.type:
                errors.append(f"设备 {name} 缺少设备类型")
        
        # 验证手势配置
        gesture = self.config.gesture
        if gesture.camera_index < 0:
            errors.append("摄像头索引不能为负数")
        if not 0 <= gesture.min_detection_confidence <= 1:
            errors.append("检测置信度应在0-1之间")
        if not 0 <= gesture.min_tracking_confidence <= 1:
            errors.append("跟踪置信度应在0-1之间")
        
        return errors
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        if not self.config:
            return {'error': '配置未加载'}
        
        return {
            'version': self.config.version,
            'total_devices': len(self.config.devices),
            'enabled_devices': len(self.get_enabled_devices()),
            'gesture_enabled': self.config.gesture.enabled,
            'camera_index': self.config.gesture.camera_index,
            'log_level': self.config.system.log_level,
            'ui_theme': self.config.system.ui_theme,
            'language': self.config.system.language
        }

# 测试代码
if __name__ == "__main__":
    # 创建配置管理器
    config_manager = ConfigManager("config.yaml")
    
    # 加载配置
    if config_manager.load_config():
        print("配置加载成功")
    
    # 从JSON导入设备
    if config_manager.load_from_json("light.json"):
        print("从JSON导入设备成功")
    
    # 保存配置
    if config_manager.save_config():
        print("配置保存成功")
    
    # 显示配置摘要
    summary = config_manager.get_config_summary()
    print("配置摘要:", summary)
    
    # 验证配置
    errors = config_manager.validate_config()
    if errors:
        print("配置错误:", errors)
    else:
        print("配置验证通过")