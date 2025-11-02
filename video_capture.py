#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画キャプチャアプリ
Raspberry Piに接続されたカメラで動画を録画するPythonアプリケーション
要件定義書: 07-001_写真動画キャプチャアプリ_要件定義書.md
"""

# 標準ライブラリ
import time
import os

# サードパーティライブラリ
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput


# 定数
VIDEO_WIDTH = 1920  # フルHD解像度（幅）
VIDEO_HEIGHT = 1080  # フルHD解像度（高さ）
VIDEO_BITRATE = 10000000  # 10Mbps
RECORDING_DURATION = 10  # 録画時間（秒）
DEFAULT_H264_FILE = "test_video.h264"
DEFAULT_MP4_FILE = "test_video.mp4"


def setup_camera():
    """
    カメラを初期化して動画撮影用に設定する

    Returns:
        Picamera2: 初期化されたカメラオブジェクト
    """
    # カメラオブジェクトを初期化
    picam2 = Picamera2()

    # 動画撮影用の設定を作成（解像度を明示的に指定）
    video_config = picam2.create_video_configuration(
        main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT)},  # フルHD解像度
        encode="main"
    )
    picam2.configure(video_config)

    return picam2


def start_preview(picam2):
    """
    可能であればプレビューを開始する

    Args:
        picam2 (Picamera2): カメラオブジェクト

    Returns:
        bool: プレビューが開始された場合True、それ以外False
    """
    # ディスプレイが利用可能かチェック（QT_QPA_PLATFORMを確認）
    if os.environ.get('DISPLAY') or os.environ.get('QT_QPA_PLATFORM'):
        picam2.start_preview(Preview.QTGL)
        print("プレビューを開始しました")
        return True
    else:
        print("ディスプレイが検出されないため、プレビューなしで実行します")
        return False


def record_video(picam2, h264_file=DEFAULT_H264_FILE, duration=RECORDING_DURATION):
    """
    動画を録画してH.264ファイルに保存する

    Args:
        picam2 (Picamera2): カメラオブジェクト
        h264_file (str): 保存するH.264ファイル名（デフォルト: test_video.h264）
        duration (int): 録画時間（秒、デフォルト: 10秒）
    """
    # エンコーダーを設定
    encoder = H264Encoder(bitrate=VIDEO_BITRATE)
    output = FileOutput(h264_file)

    # カメラを開始
    picam2.start()

    print(f"{duration}秒間の動画録画を開始します...")

    # エンコーダーを開始して録画
    picam2.start_encoder(encoder, output)
    time.sleep(duration)
    picam2.stop_encoder()

    print("動画録画が完了しました")


def convert_to_mp4(h264_file=DEFAULT_H264_FILE, mp4_file=DEFAULT_MP4_FILE):
    """
    H.264ファイルをMP4形式に変換する

    Args:
        h264_file (str): 変換元のH.264ファイル名
        mp4_file (str): 変換後のMP4ファイル名

    Returns:
        bool: 変換に成功した場合True、それ以外False
    """
    print("MP4形式に変換中...")

    # ffmpegを使用してH.264をMP4に変換
    result = os.system(f"ffmpeg -i {h264_file} -c:v copy {mp4_file} -y")

    # 変換が成功した場合、元のH.264ファイルを削除
    if result == 0 and os.path.exists(mp4_file):
        os.remove(h264_file)
        print(f"動画 '{mp4_file}' が保存されました")
        return True
    else:
        print(f"MP4変換に失敗しました（終了コード: {result}）")
        print("ヒント: ffmpegがインストールされているか確認してください")
        return False


def cleanup_camera(picam2):
    """
    カメラとプレビューを停止してリソースを解放する

    Args:
        picam2 (Picamera2): カメラオブジェクト
    """
    # プレビューを停止（開始されていない場合はエラーを無視）
    try:
        picam2.stop_preview()
    except Exception:
        pass

    # カメラを停止
    picam2.stop()
    print("カメラを停止しました")


def main():
    """
    メイン関数：カメラを初期化して動画を録画し、MP4形式に変換
    """
    # カメラの初期化
    picam2 = setup_camera()

    try:
        # プレビューを開始（可能な場合）
        start_preview(picam2)

        # 動画を録画
        record_video(picam2)

        # H.264をMP4に変換
        convert_to_mp4()

    except KeyboardInterrupt:
        print("\n\n割り込み信号を受信しました。終了処理を実行中...")

    except Exception as e:
        print(f"動画録画エラー: {e}")
        print("対処方法: カメラの接続とffmpegのインストールを確認してください")

    finally:
        # 必ずリソースをクリーンアップ
        cleanup_camera(picam2)


if __name__ == "__main__":
    main()
