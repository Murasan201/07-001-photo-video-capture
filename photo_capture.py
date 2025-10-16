from picamera2 import Picamera2, Preview
import time

# カメラオブジェクトを初期化
picam2 = Picamera2()

# 静止画撮影用の設定を作成
config = picam2.create_still_configuration()
picam2.configure(config)

# プレビューを開始
picam2.start_preview(Preview.QTGL)
picam2.start()

# カメラの調整時間を確保
time.sleep(2)

# 写真を撮影
picam2.capture_file("test_photo.jpg")

# カメラとプレビューを停止
picam2.stop_preview()
picam2.stop()

print("写真 'test_photo.jpg' が保存されました")
