# streamlit_control.py
import streamlit as st, requests, base64, time

st.set_page_config(page_title="海康 Demo", layout="wide")
st.title("🎮 海康威视软件工程实验班 Demo")

# 读取当前配置
cfg = requests.get("http://127.0.0.1:5000/api/config").json()
scale = st.sidebar.slider("scaleFactor", 1.0, 2.0, cfg.get("scale", 1.1), 0.1)
minN = st.sidebar.slider("minNeighbors", 1, 10, cfg.get("minNeigh", 5))
th = st.sidebar.slider("人脸去重阈值", 0.3, 1.0, cfg.get("threshold", 0.6), 0.05)

if st.sidebar.button("保存配置"):
    r = requests.post("http://127.0.0.1:5000/api/config",
                      json={"scale": scale, "minNeigh": minN, "threshold": th})
    if r.ok:
        st.sidebar.success("已更新")
    else:
        st.sidebar.error("配置失败")

btn_snap = st.sidebar.button("下载当前帧")
if btn_snap:
    resp = requests.get("http://127.0.0.1:5000/api/snapshot")
    if resp.status_code == 200:
        st.sidebar.download_button(
            label="保存图片",
            data=base64.b64decode(resp.json()["img"]),
            file_name=f"{int(time.time())}.jpg",
            mime="image/jpeg"
        )
    else:
        st.sidebar.warning("暂无快照")