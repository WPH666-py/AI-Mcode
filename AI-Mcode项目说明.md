# AI-Mcode 项目说明文档

## 一、项目简介

AI-Mcode，全称 **AI Mathmodel and Code of Local Agent**，即“AI 数学建模与本地编程智能体”。

本项目面向数学建模场景，围绕常规建模工作流程，提供从赛题/附件解析、数据清洗、建模分析、代码生成、说明文档生成到结果导出的本地化智能体工具。

项目采用：

- 前端：React + Vite + Ant Design
- 后端：Python + Django + Django REST Framework + Channels
- 通信：HTTP API + WebSocket
- 打包：PyInstaller 单文件 exe
- 数据库：SQLite
- 本地数据目录：`%LOCALAPPDATA%\AI-Mcode`

当前版本已经支持打包为一个独立的 Windows 可执行文件：

```text
AI-Mcode.exe
```

用户无需安装 Python、Node.js、React、Django 或 C 编译器即可运行。

---

## 二、主要功能

### 1. 项目管理

- 新建数学建模项目
- 查看已有项目
- 上传题目文件和附件
- 自动保存项目状态

### 2. 文件解析

支持对建模题目和附件进行解析，包括：

- PDF
- Word
- Excel
- 图片/文本类附件

### 3. 数据清洗

系统会对上传文件中的文本、表格和附件内容进行预处理，方便后续建模分析。

### 4. AI 建模分析

根据题目内容和附件数据，自动完成：

- 问题拆解
- 建模思路生成
- 方法选择
- 公式说明
- 求解流程设计

### 5. Python 代码生成

系统会根据每一问的建模思路生成对应 Python 代码。

当前版本默认策略是：

> 只生成代码，不自动执行代码，不进行无限修复循环。

这样可以避免打包版在不同电脑上因为环境差异导致代码执行异常。

### 6. 导出结果

每一问支持选择以下格式导出：

- `TXT + PY`
- `LaTeX + PY`
- `Markdown + PY`

用户选择格式后，可以另存为到本机指定位置。

### 7. API 设置

用户可以在前端配置大模型 API 信息，例如：

- DeepSeek
- 通义千问
- OpenAI
- Claude

需要填写可用的 API Key 后，AI 生成功能才能正常工作。

### 8. 作者信息模块

顶部导航栏中提供“作者信息”模块，用于展示作者说明、联系方式和收款码。

---

## 三、项目目录结构

核心目录如下：

```text
math_model_generator/
├── apps/                         # Django 应用模块
│   ├── accounts/                 # 用户与自动登录相关逻辑
│   ├── agent/                    # AI 智能体与建模流程
│   ├── core/                     # 核心数学工具与加速模块
│   ├── files/                    # 文件解析与清洗模块
│   └── projects/                 # 项目、问题、任务和 WebSocket 逻辑
│
├── config/                       # Django 配置
│   ├── settings.py               # 项目配置
│   ├── urls.py                   # HTTP 路由
│   ├── asgi.py                   # ASGI / WebSocket 入口
│   └── wsgi.py                   # WSGI 入口
│
├── frontend/                     # React 前端
│   ├── public/                   # 前端静态资源
│   ├── src/                      # 前端源码
│   └── dist/                     # 前端构建产物
│
├── desktop_launcher.py           # PyInstaller 桌面启动器
├── AI-Mcode.spec                 # PyInstaller 打包配置
├── build-exe.ps1                 # 一键构建 exe 脚本
├── AI-Mcode-installer.iss        # Inno Setup 安装包配置
├── manage.py                     # Django 管理入口
├── requirements.txt              # Python 依赖
└── dist/                         # 打包输出目录
```

---

## 四、运行方式

## 方式一：运行打包后的 exe

当前推荐普通用户使用此方式。

运行：

```powershell
.\dist\AI-Mcode.exe
```

程序会自动启动：

| 服务 | 地址 |
|---|---|
| 前端页面 | `http://127.0.0.1:3030/` |
| API 服务 | `http://127.0.0.1:3032/` |
| WebSocket | `ws://127.0.0.1:3031/` |

启动后会自动打开浏览器。

### 日志位置

```text
%LOCALAPPDATA%\AI-Mcode\launcher.log
```

### 用户数据位置

```text
%LOCALAPPDATA%\AI-Mcode
```

这里保存：

- SQLite 数据库
- 上传文件
- 生成结果
- 运行日志

---

## 方式二：开发环境运行

### 1. 安装前端依赖

```powershell
cd frontend
npm install
```

### 2. 启动前端

```powershell
npm run dev
```

### 3. 安装 Python 依赖

```powershell
pip install -r requirements.txt
```

### 4. 数据库迁移

```powershell
python manage.py migrate
```

### 5. 启动后端 API

```powershell
python manage.py runserver 127.0.0.1:3018
```

### 6. 启动 WebSocket 服务

```powershell
set DJANGO_SETTINGS_MODULE=config.settings
python -m daphne -b 127.0.0.1 -p 3031 config.asgi:application
```

> 说明：开发环境端口可根据 `frontend/vite.config.js` 和后端启动参数调整；打包版固定使用 `3030 / 3031 / 3032`。

---

## 五、打包方式

项目使用 PyInstaller 进行单文件打包。

### 一键打包

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build-exe.ps1
```

构建流程包括：

1. 停止旧的 `AI-Mcode.exe` 进程
2. 构建 React 前端
3. 安装/检查 PyInstaller
4. 生成单文件 `AI-Mcode.exe`
5. 复制便携版到 `dist/app/`
6. 如果检测到 Inno Setup，则自动生成安装包

### 打包输出

```text
dist/AI-Mcode.exe
```

便携版：

```text
dist/app/AI-Mcode.exe
```

如果安装了 Inno Setup 6，还会生成：

```text
installer-dist/AI-Mcode-Setup.exe
```

---

## 六、打包版端口说明

打包版由 `desktop_launcher.py` 统一启动三个本地服务：

| 服务 | 端口 | 说明 |
|---|---:|---|
| React 静态页面 | `3030` | 内置 HTTP 静态服务 |
| WebSocket | `3031` | Daphne + Channels |
| Django API | `3032` | WSGI 本地 API 服务 |

浏览器访问：

```text
http://127.0.0.1:3030/
```

前端会自动连接：

```text
http://127.0.0.1:3032/api
ws://127.0.0.1:3031/ws
```

---

## 七、分发说明

普通用户只需要拿到：

```text
AI-Mcode.exe
```

即可运行。

用户无需安装：

- Python
- Node.js
- npm
- React
- Django
- C 编译器
- Visual Studio Build Tools

但用户电脑需要满足：

1. Windows 10 / Windows 11 64 位
2. 本地端口 `3030`、`3031`、`3032` 未被占用
3. 防火墙/杀毒软件没有阻止本地服务
4. 能访问所配置的大模型 API
5. 用户填写了正确 API Key

---

## 八、常见问题

### 1. 页面打不开

检查 exe 是否正在运行，并查看日志：

```text
%LOCALAPPDATA%\AI-Mcode\launcher.log
```

也可以检查端口：

```powershell
Get-NetTCPConnection -LocalPort 3030,3031,3032
```

### 2. API 请求失败

可能原因：

- `3032` 端口被占用
- 防火墙拦截
- 后端启动失败
- CORS 配置异常

查看日志：

```text
%LOCALAPPDATA%\AI-Mcode\launcher.log
```

### 3. WebSocket 无法连接

可能原因：

- `3031` 端口被占用
- Daphne 启动失败
- 杀毒软件拦截本地网络服务

### 4. AI 不能生成内容

可能原因：

- API Key 未填写
- API Key 错误
- 模型服务网络不可达
- 账户余额不足
- 当前网络无法访问对应模型服务

### 5. 杀毒软件提示风险

PyInstaller 单文件 exe 可能被部分杀毒软件误报。

正式分发时建议：

- 使用安装包
- 添加数字签名
- 提供官方网站或可信下载来源

---

## 九、作者信息

作者：水哥  
学校：青岛理工大学 2022 级学生  
联系邮箱：943050454@qq.com

项目名称：AI-Mcode  
全称：AI Mathmodel and Code of Local Agent  
中文含义：AI 数学建模与本地编程智能体

---

## 十、当前状态

当前项目已经具备：

- React 前端页面
- Django API 服务
- WebSocket 实时通信
- AI 建模流程
- 代码生成能力
- 多格式导出能力
- 作者信息模块
- PyInstaller 单 exe 打包能力

当前推荐交付物：

```text
dist/AI-Mcode.exe
```

或：

```text
dist/app/AI-Mcode.exe
```

如果需要安装包，请安装 Inno Setup 后重新执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build-exe.ps1
```
