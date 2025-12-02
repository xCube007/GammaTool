# GammaTool 使用说明

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python src/main.py
```

## 功能说明

### 基础调节

- **亮度调节** (0-200%)
  - 默认值：100%
  - 拖动滑块或输入数值调节
  - 支持热键快速调节

- **对比度调节** (0-200%)
  - 默认值：100%
  - 增强画面层次感

- **灰度调节** (0-100%)
  - 默认值：0% (无灰度)
  - 护眼模式，减少色彩刺激

### RGB 通道调节

- **红色通道** (0-255)
- **绿色通道** (0-255)
- **蓝色通道** (0-255)

可以通过调节 RGB 通道实现色温调节效果。

### 热键功能

默认热键：

| 热键 | 功能 |
|------|------|
| `Ctrl+Alt+Up` | 增加亮度 (+5%) |
| `Ctrl+Alt+Down` | 降低亮度 (-5%) |
| `Ctrl+Alt+Right` | 增加对比度 (+5%) |
| `Ctrl+Alt+Left` | 降低对比度 (-5%) |
| `Ctrl+Alt+R` | 恢复默认设置 |
| `Ctrl+Alt+G` | 显示/隐藏主窗口 |

**注意**：热键功能需要管理员权限才能在某些应用程序中生效。

### 系统托盘

- **双击托盘图标**：显示主窗口
- **右键菜单**：
  - 显示主窗口
  - 快速调节（亮度预设）
  - 恢复默认
  - 退出程序

## 配置文件

配置文件位置：`%APPDATA%/GammaTool/config.json`

配置文件会自动保存，包含：
- 显示设置（亮度、对比度、灰度、RGB）
- 热键设置
- UI 设置
- 系统设置

## 测试功能

运行测试脚本验证核心功能：

```bash
python tests/test_gamma_engine.py
```

测试脚本会：
1. 创建 Gamma 引擎
2. 测试亮度调节
3. 测试对比度调节
4. 测试灰度调节
5. 测试 RGB 通道
6. 恢复默认设置

每个步骤会暂停 2 秒，让你看到效果。

## 打包程序

### 安装打包工具

```bash
pip install pyinstaller
```

### 打包为可执行文件

```bash
pyinstaller build.spec
```

打包后的文件位于 `dist/GammaTool.exe`

### 打包选项

- **单文件模式**：所有内容打包到一个 exe 文件
- **UPX 压缩**：减小文件体积
- **无控制台**：不显示命令行窗口

如需调试，可以修改 `build.spec` 中的 `console=True`

## 常见问题

### Q: 程序无法启动？

A: 检查以下几点：
1. 是否安装了所有依赖：`pip install -r requirements.txt`
2. Python 版本是否为 3.8+
3. 是否在 Windows 系统上运行

### Q: 热键不生效？

A: 可能的原因：
1. 热键与其他程序冲突
2. 需要管理员权限
3. keyboard 库未正确安装

解决方法：
- 尝试更换热键组合
- 以管理员身份运行程序
- 重新安装 keyboard 库

### Q: 设置没有保存？

A: 检查配置文件目录是否有写入权限：
- 配置目录：`%APPDATA%/GammaTool`
- 确保该目录可写

### Q: 程序退出后屏幕没有恢复？

A: 默认情况下程序退出时会恢复默认设置。如果没有恢复：
1. 手动运行程序并点击"恢复默认"
2. 重启计算机
3. 检查配置文件中的 `system.restore_on_exit` 设置

### Q: 如何卸载？

A: 程序是绿色软件，直接删除即可：
1. 删除程序文件夹
2. 删除配置目录：`%APPDATA%/GammaTool`
3. 如果设置了开机自启，取消勾选

## 开发调试

### 启用调试日志

日志文件位置：`%APPDATA%/GammaTool/logs/gammatool.log`

查看日志可以帮助诊断问题。

### 修改日志级别

在 `src/utils.py` 的 `setup_logging` 函数中修改：

```python
logger.setLevel(logging.DEBUG)  # 改为 DEBUG 级别
```

### 控制台输出

打包时设置 `console=True` 可以看到控制台输出：

```python
# build.spec
exe = EXE(
    ...
    console=True,  # 改为 True
    ...
)
```

## 技术支持

如有问题或建议，请：
1. 查看日志文件
2. 查看 GitHub Issues
3. 提交问题报告

## 许可证

本项目采用 MIT 许可证。