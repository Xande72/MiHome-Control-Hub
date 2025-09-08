# 贡献指南

感谢您对米家设备整合控制系统的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 开始之前

在开始贡献之前，请确保您已经：

1. 阅读了项目的 [README.md](README.md)
2. 了解了项目的基本架构和功能
3. 检查了现有的 [Issues](../../issues) 和 [Pull Requests](../../pulls)

## 报告Bug

如果您发现了Bug，请创建一个Issue并包含以下信息：

### Bug报告模板

```markdown
**Bug描述**
简洁明了地描述Bug的现象

**复现步骤**
1. 执行步骤1
2. 执行步骤2
3. 看到错误

**期望行为**
描述您期望发生的行为

**实际行为**
描述实际发生的行为

**环境信息**
- 操作系统: [例如 Windows 11]
- Python版本: [例如 3.9.0]
- 项目版本: [例如 v1.2.0]
- 相关设备: [例如 米家台灯Pro]

**附加信息**
- 错误日志
- 截图（如适用）
- 其他相关信息
```

## 功能建议

我们欢迎新功能建议！请创建一个Issue并包含：

### 功能建议模板

```markdown
**功能描述**
简洁明了地描述您希望添加的功能

**使用场景**
描述这个功能的使用场景和价值

**实现建议**
如果您有实现思路，请简要描述

**替代方案**
是否考虑过其他解决方案？
```

## 代码贡献

### 开发环境设置

1. **Fork项目**
   ```bash
   # 克隆您fork的仓库
   git clone https://github.com/YOUR_USERNAME/mihome-gesture-control.git
   cd mihome-gesture-control
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 代码规范

请遵循以下代码规范：

#### Python代码风格
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用4个空格进行缩进
- 行长度不超过88字符
- 使用有意义的变量和函数名

#### 注释规范
- 为复杂的逻辑添加注释
- 使用中文注释（项目主要面向中文用户）
- 为公共函数和类添加文档字符串

#### 示例代码
```python
class DeviceController:
    """设备控制器类
    
    负责管理和控制米家设备的连接、状态监控和指令发送。
    """
    
    def __init__(self, config_path: str):
        """初始化设备控制器
        
        Args:
            config_path: 配置文件路径
        """
        self.devices = []
        self.config_path = config_path
        
    def connect_device(self, device_info: dict) -> bool:
        """连接设备
        
        Args:
            device_info: 设备信息字典
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 连接逻辑
            return True
        except Exception as e:
            logger.error(f"设备连接失败: {e}")
            return False
```

### 提交规范

使用清晰的提交信息：

```bash
# 格式: <类型>: <简短描述>
# 
# <详细描述（可选）>

# 示例
git commit -m "feat: 添加设备状态缓存功能

- 实现设备在线状态缓存机制
- 减少不必要的网络请求
- 提升界面响应速度"
```

#### 提交类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### Pull Request流程

1. **确保代码质量**
   - 代码能够正常运行
   - 遵循项目的代码规范
   - 添加必要的注释和文档

2. **测试您的更改**
   - 在本地测试所有功能
   - 确保没有破坏现有功能
   - 如果可能，添加相关测试

3. **创建Pull Request**
   - 使用清晰的标题和描述
   - 引用相关的Issue（如果有）
   - 说明更改的内容和原因

4. **Pull Request模板**
   ```markdown
   ## 更改描述
   简要描述此PR的更改内容
   
   ## 更改类型
   - [ ] Bug修复
   - [ ] 新功能
   - [ ] 文档更新
   - [ ] 性能优化
   - [ ] 代码重构
   
   ## 测试
   - [ ] 本地测试通过
   - [ ] 功能测试完成
   - [ ] 回归测试通过
   
   ## 相关Issue
   Fixes #(issue编号)
   
   ## 截图（如适用）
   
   ## 其他说明
   ```

## 文档贡献

文档改进同样重要！您可以：

- 修复文档中的错误
- 改进现有文档的清晰度
- 添加使用示例
- 翻译文档到其他语言

## 社区准则

请遵循以下准则：

- **友善和尊重**: 对所有参与者保持友善和尊重
- **建设性反馈**: 提供建设性的反馈和建议
- **耐心**: 对新贡献者保持耐心
- **包容性**: 欢迎不同背景和经验水平的贡献者

## 获得帮助

如果您需要帮助，可以：

- 查看现有的文档和Issue
- 在Issue中提问
- 联系项目维护者

## 致谢

感谢所有为项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

再次感谢您的贡献！🎉