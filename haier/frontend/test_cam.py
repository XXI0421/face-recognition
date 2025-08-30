# quick_cam.py —— 最小可运行摄像头+PyQt
import sys, cv2, threading
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer

WIN_W, WIN_H = 720, 1280

class Cam(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WIN_W, WIN_H)
        self.label = QLabel(self)
        self.label.setFixedSize(WIN_W, WIN_H)

        # 打开摄像头
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("❌ 摄像头打开失败！")
            sys.exit()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # 定时读帧
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_frame)
        self.timer.start(30)

    def show_frame(self):
        ok, frame = self.cap.read()
        if ok:
            frame = cv2.flip(frame, 1)                          # 镜像
            rgb = cv2.resize(frame, (WIN_W, WIN_H))
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, w * ch, QImage.Format.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, e):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Cam()
    w.setWindowTitle("Quick Cam")
    w.show()
    sys.exit(app.exec())