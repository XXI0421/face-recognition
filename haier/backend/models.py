import cv2, os
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def face_detector(img, scale=1.1, minNeigh=5):
    """返回 list: [[x,y,w,h], ...]"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scale, minNeigh)
    return [[int(v) for v in f] for f in faces]