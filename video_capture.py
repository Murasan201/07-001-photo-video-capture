#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import time
import os

# カメラオブジェクトを初期化
picam2 = Picamera2()

# 動画撮影用の設定を作成（解像度を明示的に指定）
video_config = picam2.create_video_configuration(
    main={"size": (1920, 1080)},  # フルHD解像度
    encode="main"
)
picam2.configure(video_config)

# エンコーダーを設定
encoder = H264Encoder(bitrate=10000000)  # 10Mbps
output = FileOutput("test_video.h264")

try:
    # プレビューを開始（QT_QPA_PLATFORMを確認）
    if os.environ.get('DISPLAY') or os.environ.get('QT_QPA_PLATFORM'):
        picam2.start_preview(Preview.QTGL)
        print("プレビューを開始しました")
    else:
        print("ディスプレイが検出されないため、プレビューなしで実行します")
    
    # カメラを開始
    picam2.start()
    
    print("10秒間の動画録画を開始します...")
    
    # エンコーダーを開始して録画
    picam2.start_encoder(encoder, output)
    time.sleep(10)  # 10秒間録画
    picam2.stop_encoder()
    
    print("動画録画が完了しました")
    
    # H.264をMP4に変換
    print("MP4形式に変換中...")
    os.system("ffmpeg -i test_video.h264 -c:v copy test_video.mp4 -y")
    
    # 元のH.264ファイルを削除
    if os.path.exists("test_video.mp4"):
        os.remove("test_video.h264")
        print("動画 'test_video.mp4' が保存されました")
    
except Exception as e:
    print(f"エラーが発生しました: {e}")
    
finally:
    # プレビューとカメラを停止
    try:
        picam2.stop_preview()
    except:
        pass
    picam2.stop()
    print("カメラを停止しました")
