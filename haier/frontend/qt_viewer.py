# qt_viewer.py  —— 固定 720× 窗口，人脸绿框+编号
import sys, cv2, numpy as np, base64, requests, threading, queue
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QFont
from PyQt6.QtCore import Qt, QTimer

WIN_W, WIN_H = 720,720
URL = "http://127.0.0.1:5000/api/detect"

# 摄像头线程
frame_q = queue.Queue(maxsize=2)
stop_flag = threading.Event()

def grabber():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FPS, 30)
    while not stop_flag.is_set():
        ok, frame = cap.read()
        if not ok:
            continue
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.flip(frame, 1)          # 镜像
        frame_q.put(frame)

threading.Thread(target=grabber, daemon=True).start()

class CameraWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WIN_W, WIN_H)
        self.label = QLabel(self)
        self.label.setFixedSize(WIN_W, WIN_H)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        try:
            frame = frame_q.get_nowait()
        except queue.Empty:
            return

        _, buf = cv2.imencode(".jpg", frame)
        try:
            boxes_ids = requests.post(
                URL,
                json={"image": base64.b64encode(buf).decode()},
                timeout=0.3
            ).json()
        except Exception:
            boxes_ids = {"boxes": [], "ids": []}

        # 画框
        for (x, y, w, h), pid in zip(boxes_ids["boxes"], boxes_ids["ids"]):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(frame, str(pid), (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 转 QPixmap
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
        self.label.setPixmap(QPixmap.fromImage(qt_img))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = CameraWidget()
    w.setWindowTitle("Haier Face Demo")
    w.show()
    sys.exit(app.exec())