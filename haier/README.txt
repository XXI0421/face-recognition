一.项目介绍
“海康 Demo” 是一个轻量级、开箱即用的人脸识别原型。核心流程：
摄像头 → Flask API（InsightFace+buffalo_l）→ 在线聚类 → 返回人脸框+ID → PyQt6 渲染。
Streamlit 作为远程控制台，可动态调参和下载图片。全链路本地运行，无需 GPU。

二.使用方法
1.克隆或解压工程到任意文件夹（下文用 <project> 指代）。

2.安装依赖
cd <project>
python -m pip install -r requirements.txt

3.一键启动
双击 run_demo.bat（已提供）
或者 命令行： .\run_demo.bat + 回车
启动顺序：Flask → PyQt6 → Streamlit，脚本已自动完成。

4.使用
• PyQt6 窗口（720×720）实时预览，绿框+ID。
• Streamlit 侧边栏调阈值、scale、保存配置、下载当前帧。
• 所有参数实时生效，无需重启。

三.特色
1.高精度：buffalo_l 模型 + 人脸对齐 + CLAHE 光照归一化。

2.在线聚类：滑动平均中心，10 帧缓冲，抗抖动。

3.低耦合：Flask REST API，任何前端（PyQt、Web、移动端）均可调用。

4.一键启动：bat/sh 自动拉起 3 个进程，关闭终端即全部结束。

5.零配置：所有参数在 Streamlit 实时调节，效果立竿见影。

四.可拓展方向
可拓展方向
• 多路摄像头：在 /api/detect 增加 camera_id 字段，前端支持 Tab 页切换。
• 人脸库持久化：将 face_db.pkl 换成 SQLite/MySQL，支持增删改查。
• 活体检测 / 口罩检测：在 enhance_light 后级联额外模型。
• 多 GPU 推理：insightface 支持 ctx_id=0/1/…，配合 gunicorn + gevent 并发。
• WebRTC：用 streamlit-webrtc 或 simple-peer 直接在浏览器推流，无需 PyQt6。
• 移动端：把 PyQt 换成 Kivy 或 React-Native，通过 HTTP 调用相同 API。
• 人脸搜索：将 gallery 转成 Faiss 索引，支持百万级底库秒级查询。
