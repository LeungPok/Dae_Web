<div align="center">

# DAE Config Manager

**一个轻量、专注的 dae 核心网页配置与日志管理器**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

[开发背景](#-开发背景-why-i-built-this) •  [截图](#-截图-screenshots) • [快速开始](#-快速开始-quick-start) • 

</div>

---

## 💡 开发背景 (Why I built this)

如果你和我一样，为了追求稳定，从 `daed` 迁移到了纯粹的 `dae` 核心，你一定深有体会：

1. **逃离 `daed` 的内存泄漏与停更**：`daed` 在长时间运行后存在明显的内存泄漏问题，且官方已停止积极迭代。为了家里网络的极致稳定，我们选择回归轻量、高性能的纯净 `dae` 核心。

2. **但迎来了原生核心的“硬核”运维痛点**：纯净的核心完全依赖本地配置文件，没有任何 UI。每次家里网络策略变更、或者节点失效需要微调时，都必须雷打不动地打开终端 SSH 连上设备。由于没有即时反馈，万一不小心改错了一个字母，往往还得跨窗口去翻系统底层的滚动日志来排障。这种每次改配置都要“全副武装”进黑乎乎终端的原始交互，对于日常只想安安静静冲个浪的个人用户来说，确实有些过于繁琐了。

于是，我利用业余时间反复“鞭打”AI，合力搓出了这个 `DAE Config Manager`。它不追求大而全，拒绝功能臃肿，只专注于保障个人用户最核心的两个高频诉求：

👉 **提供一个优雅、秒开的界面来更新配置文件。**

👉 **提供一个实时的终端来查看核心日志。**

---


## 📸 截图 (Screenshots)
![](\images\1.png)
![](\images\2.png)


## 🛠️ 快速开始 (Quick Start)

### 步骤 1：克隆项目
```bash
git clone https://github.com/LeungPok/Dae_Web.git
cd Dae_Web
```

### 步骤 2：创建并激活虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (Linux/macOS)
source venv/bin/activate
```

### 步骤 3：安装依赖
```bash
pip install fastapi uvicorn
```

### 步骤 4：启动服务
```bash
# 直接运行
uvicorn main:app --host 0.0.0.0 --port 8000

# 或者使用后台运行 (推荐)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > output.log 2>&1 &
```

访问 `http://你的服务器IP:8000` 即可进入控制台。


---

## 🙏 致谢 (Acknowledgements)

- 感谢 [dae](https://github.com/daeuniverse/dae) 官方团队开发了如此高性能的路由内核。
- 感谢 [Tailwind CSS](https://tailwindcss.com/) 和 [Element Plus](https://element-plus.org/) 提供优秀的 UI 基础。

---

## 📜 开源协议 (License)

本项目基于 [MIT License](LICENSE) 开源。你可以自由地使用、修改和分发它，但请保留原作者的版权声明。

