#!/usr/bin/env python3
from picamera2 import Picamera2
import time


def main():
    # カメラを初期化
    picam2 = Picamera2()
    picam2.start()

    # カメラの調整時間（2秒待機）
    time.sleep(2)

    # 写真を撮影して保存
    picam2.capture_file("photo.jpg")
    print("写真を保存しました: photo.jpg")

    # カメラを停止
    picam2.stop()


if __name__ == "__main__":
    main()
