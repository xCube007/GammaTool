# GammaTool 项目配置指南

## 项目结构

以下是完整的项目目录结构：

```
GammaTool/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── gamma_engine.py
│   ├── main_window.py
│   ├── hotkey_manager.py
│   ├── config_manager.py
│   ├── tray_icon.py
│   └── utils.py
├── resources/
│   ├── icons/
│   │   ├── app_icon.ico
│   │   ├── tray_icon.png
│   │   ├── tray_icon_dark.png
│   │   └── tray_icon_light.png
│   └── styles/
│       ├── dark_theme.qss
│       └── light_theme.qss
├── config/
│   └── default_config.json
├── tests/
│   ├── __init__.py
│   ├── test_gamma_engine.py
│   ├── test_config_manager.py
│   └── test_hotkey_manager.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── CHANGELOG.md
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── build.spec
├── .gitignore
├── LICENSE
└── README.md
```

## 依赖清单

### requirements.txt

```txt
# GUI 框架
PyQt5>=5.15.0
PyQt5-Qt5>=5.15.2
PyQt5-sip>=12.8.1

# Windows API 支持
pywin32>=305

# 全局热键
keyboard>=0.13.5

# 配置文件处理
# 使用 Python 内置的 json 模块，无需额外依赖

# 日志记录
# 使用 Python 内置的 logging 模块，无需额外依赖
```

### requirements-dev.txt

```txt
# 包含所有运行时依赖
-r requirements.txt

# 测试框架
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-qt>=4.0.0

# 代码质量
pylint>=2.12.0
black>=22.0.0
flake8>=4.0.0
mypy>=0.930

# 打包工具
pyinstaller>=5.0.0
pyinstaller-hooks-contrib>=2022.0

# 文档生成
sphinx>=4.3.0
sphinx-rtd-theme>=1.0.0
```

## 配置文件

### default_config.json

```json
{
  "version": "1.0.0",
  "display": {
    "brightness": 100,
    "contrast": 100,
    "grayscale": 0,
    "rgb": {
      "red": 255,
      "green": 255,
      "blue": 255
    }
  },
  "hotkeys": {
    "increase_brightness": "ctrl+alt+up",
    "decrease_brightness": "ctrl+alt+down",
    "increase_contrast": "ctrl+alt+right",
    "decrease_contrast": "ctrl+alt+left",
    "reset": "ctrl+alt+r",
    "toggle_window": "ctrl+alt+g"
  },
  "ui": {
    "theme": "dark",
    "window_opacity": 0.95,
    "always_on_top": false,
    "start_minimized": false
  },
  "system": {
    "auto_start": false,
    "minimize_to_tray": true,
    "close_to_tray": true,
    "restore_on_exit": true
  },
  "advanced": {
    "adjustment_step": 5,
    "smooth_transition": true,
    "transition_duration": 200,
    "debounce_delay": 100
  }
}
```

## PyInstaller 打包配置

### build.spec

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'win32api',
        'win32con',
        'win32gui',
        'pywintypes',
        'keyboard',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GammaTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',
    version='version_info.txt'
)
```

### version_info.txt

```txt
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Your Company'),
        StringStruct(u'FileDescription', u'GammaTool - Screen Brightness Adjustment Tool'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'GammaTool'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'GammaTool.exe'),
        StringStruct(u'ProductName', u'GammaTool'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

## Git 配置

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# 测试
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
Thumbs.db

# 项目特定
config/user_config.json
*.log
temp/
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/GammaTool.git
cd GammaTool
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# 或使用 conda
conda create -n gammatool python=3.9
conda activate gammatool
```

### 3. 安装依赖

```bash
# 安装运行时依赖
pip install -r requirements.txt

# 如果需要开发，安装开发依赖
pip install -r requirements-dev.txt
```

### 4. 运行程序

```bash
python src/main.py
```

## 开发工作流

### 代码格式化

```bash
# 使用 black 格式化代码
black src/

# 使用 flake8 检查代码风格
flake8 src/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_gamma_engine.py
```

### 类型检查

```bash
# 使用 mypy 进行类型检查
mypy src/
```

### 构建可执行文件

```bash
# 使用 PyInstaller 打包
pyinstaller build.spec

# 输出文件位于 dist/GammaTool.exe
```

## 调试技巧

### 启用控制台输出

在开发时，可以修改 `build.spec` 中的 `console=True` 来查看控制台输出：

```python
exe = EXE(
    ...
    console=True,  # 改为 True
    ...
)
```

### 日志配置

程序使用 Python 的 logging 模块，日志文件位于：
- Windows: `%APPDATA%/GammaTool/logs/gammatool.log`

可以在 `src/utils.py` 中配置日志级别：

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # 开发时使用 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 性能优化建议

1. **减小打包体积**
   - 使用 UPX 压缩
   - 排除不必要的模块
   - 使用虚拟环境避免打包无关依赖

2. **提升运行性能**
   - 使用缓存机制
   - 实现防抖和节流
   - 异步处理耗时操作

3. **降低资源占用**
   - 及时释放系统资源
   - 使用事件驱动而非轮询
   - 优化 UI 更新频率

## 常见问题

### Q: 打包后程序无法运行？

A: 检查以下几点：
1. 确保所有依赖都在 `hiddenimports` 中
2. 检查资源文件路径是否正确
3. 查看是否有杀毒软件拦截

### Q: 热键不生效？

A: 可能需要以管理员权限运行，或者检查是否与其他程序冲突。

### Q: 界面显示异常？

A: 检查 QSS 样式文件是否正确加载，确认 PyQt5 版本兼容性。

## 发布检查清单

- [ ] 所有测试通过
- [ ] 代码格式化完成
- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 构建可执行文件
- [ ] 测试可执行文件
- [ ] 准备发布说明
- [ ] 创建 GitHub Release
- [ ] 上传安装包

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。