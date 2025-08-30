```markdown
# 海康 Demo

> 轻量级、开箱即用的人脸识别原型  
> 本地运行 | 无需 GPU | 实时调参 | 一键启动

---

## 一、项目介绍
**海康 Demo** 将人脸识别流程浓缩为一条最简链路：  
**摄像头 → Flask API（InsightFace+buffalo_l）→ 在线聚类 → 返回人脸框+ID → PyQt6 渲染**  
Streamlit 作为远程控制台，可动态调参、下载图片，全链路纯 CPU 即可跑通。

---

## 二、快速开始

### 1. 获取代码
```bash
git clone <仓库地址>   # 或手动解压到任意目录，下文用 <project> 指代
cd <project>
```

### 2. 安装依赖
```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 一键启动
- **Windows**：双击 `run_demo.bat`  
- **Linux/macOS**：
  ```bash
  ./run_demo.sh
  ```
脚本会自动顺序拉起  
`Flask → PyQt6 → Streamlit`，关闭终端即可全部结束。

### 4. 使用
| 组件 | 说明 |
|---|---|
| **PyQt6 预览窗**（720×720） | 实时画面，绿色人脸框 + 聚类 ID |
| **Streamlit 控制台** | 浏览器打开 `http://localhost:8501`<br>• 调阈值 / scale / 保存配置<br>• 一键下载当前帧 |

所有参数 **实时生效，无需重启**。

---

## 三、核心特色
| 特色 | 说明 |
|---|---|
| **高精度** | InsightFace `buffalo_l` + 人脸对齐 + CLAHE 光照归一化 |
| **在线聚类** | 滑动平均中心 + 10 帧缓冲，抗抖动 |
| **低耦合** | Flask REST，前端可替换为 Web / 移动端 |
| **一键启动** | bat/sh 脚本，3 进程并行，关闭终端即回收 |
| **零配置** | 参数全部在 Streamlit 实时可调 |

---

## 四、项目结构（精简版）
```
<project>
├── api/               # Flask 服务
│   ├── app.py
│   └── face_core.py
├── ui/
│   ├── qt_main.py     # PyQt6 预览
│   └── st_main.py     # Streamlit 控制台
├── models/
│   └── buffalo_l.onnx
├── run_demo.bat
├── run_demo.sh
└── requirements.txt
```

---

## 五、可拓展方向
- **多路摄像头**：在 `/api/detect` 增加 `camera_id`，前端 Tab 切换  
- **人脸库持久化**：把 `face_db.pkl` 换成 SQLite / MySQL，支持增删改查  
- **活体 / 口罩检测**：在 `enhance_light` 后级联额外模型  
- **多 GPU 推理**：`ctx_id=0/1/...` + gunicorn + gevent 并发  
- **WebRTC**：`streamlit-webrtc` 直接浏览器推流，无需 PyQt6  
- **移动端**：前端换 Kivy / React-Native，走同一 HTTP API  
- **人脸搜索**：gallery 转 Faiss 索引，百万底库秒级查询

---

## 六、常见问题
| 问题 | 解决 |
|---|---|
| GPU 显存不足 | 默认 CPU 推理，无需 GPU |
| 端口占用 | 修改 `.bat/.sh` 中的 `PORT` 环境变量 |
| 摄像头打不开 | 检查索引号，修改 `config.yaml` 里的 `camera_id` |

---

## 七、License
MIT © 2025 Hik-Demo Team
```
