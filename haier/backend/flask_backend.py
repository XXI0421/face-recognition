# app.py  （方案3：更强模型 + 人脸对齐 + 光照归一化）
from flask import Flask, request, jsonify
import cv2, base64, numpy as np, os, pickle
import insightface
from threading import Lock

app = Flask(__name__)

# -------- 1. 加载模型（优先 buffalo_m，fallback buffalo_l） --------
MODEL = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
MODEL.prepare(ctx_id=-1, det_thresh=0.6)
# --------------------------------------------------------------------

DB_FILE   = "face_db.pkl"
gallery   = {}          # {pid: {"center": ndarray, "buffer: deque}}
next_id   = 1
lock      = Lock()

if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        gallery, next_id = pickle.load(f)

def save_db():
    with open(DB_FILE, "wb") as f:
        pickle.dump((gallery, next_id), f)

latest_frame = None
latest_lock  = Lock()

# -------------- 2. 光照增强 --------------
def enhance_light(img, gamma=0.8):
    # Gamma 校正
    table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(256)]).astype("uint8")
    img = cv2.LUT(img, table)
    # CLAHE 局部直方图均衡
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
# ----------------------------------------

# -------------- 3. 人脸对齐 --------------
def align_face(img, face, size=112):
    src = np.array([
        [38.2946, 51.6963],   # 标准正脸 5 点坐标（112x112）
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041]
    ], dtype=np.float32)
    # InsightFace 返回的 kps 顺序：左右眼、鼻尖、左右嘴角
    kps = face.kps.astype(np.float32)
    # 对应顺序：左眼→左眼，右眼→右眼，鼻尖→鼻尖... 直接对齐
    M = cv2.getAffineTransform(kps[:3], src[:3])
    warped = cv2.warpAffine(img, M, (size, size), borderValue=0.0)
    return warped
# ----------------------------------------

# -------------- 4. 在线聚类（滑动平均） --------------
from collections import deque
BUFFER_LEN = 10
ALPHA = 0.1

def update_cluster(pid, emb):
    item = gallery[pid]
    item["center"] = (1 - ALPHA) * item["center"] + ALPHA * emb

def find_or_register(emb, threshold):
    global next_id
    if not gallery:
        pid = next_id; next_id += 1
        gallery[pid] = {"center": emb, "buffer": deque([emb], maxlen=BUFFER_LEN)}
        return pid

    dists = [(1 - np.dot(emb, v["center"]), pid) for pid, v in gallery.items()]
    min_d, best_pid = min(dists, key=lambda x: x[0])
    if min_d < threshold:
        update_cluster(best_pid, emb)
        return best_pid
    else:
        pid = next_id; next_id += 1
        gallery[pid] = {"center": emb, "buffer": deque([emb], maxlen=BUFFER_LEN)}
        return pid
# -------------------------------------------------------

# ============== 5. 路由保持不变 ==============
DEFAULT_CONFIG = {"scale": 1.1, "minNeigh": 5, "threshold": 0.45}

@app.route("/api/config", methods=["GET", "POST"])
def config():
    if request.method == "GET":
        return jsonify(DEFAULT_CONFIG)
    else:
        data = request.get_json(force=True)
        DEFAULT_CONFIG.update(data)
        return jsonify({"status": "ok"})

@app.route("/api/detect", methods=["POST"])
def detect():
    global next_id, latest_frame
    data = request.json
    img = cv2.imdecode(np.frombuffer(base64.b64decode(data["image"]), np.uint8),
                       cv2.IMREAD_COLOR)
    img = enhance_light(img)

    with latest_lock:
        latest_frame = img.copy()

    faces = MODEL.get(img, max_num=0)
    boxes, ids = [], []
    threshold = float(data.get("threshold", DEFAULT_CONFIG["threshold"]))

    # 在 /api/detect 里替换对应代码
    for f in faces:
        if f.det_score < 0.6:
            continue

        aligned = align_face(img, f)
        small_faces = MODEL.get(aligned, max_num=1)

        # 如果对齐后检测不到，直接沿用原始 embedding
        if len(small_faces) == 0:
            new_emb = f.normed_embedding.astype(np.float32)
        else:
            new_emb = small_faces[0].normed_embedding.astype(np.float32)

        pid = find_or_register(new_emb, threshold)

        x1, y1, x2, y2 = map(int, f.bbox)
        boxes.append([x1, y1, x2 - x1, y2 - y1])
        ids.append(pid)

    save_db()
    return jsonify({"boxes": boxes, "ids": ids})

@app.route("/api/snapshot", methods=["GET"])
def snapshot():
    with latest_lock:
        if latest_frame is None:
            return jsonify({"img": ""}), 204
        _, buf = cv2.imencode(".jpg", latest_frame)
        b64 = base64.b64encode(buf).decode()
    return jsonify({"img": b64})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)