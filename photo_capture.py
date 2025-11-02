#!/usr/bin/env python3
"""
写真キャプチャアプリ
Raspberry Piに接続されたカメラで静止画を撮影するPythonアプリケーション
要件定義書: 07-001_写真動画キャプチャアプリ_要件定義書.md
"""

# サードパーティライブラリ
from picamera2 import Picamera2, Preview
import time


# 定数
CAMERA_WARMUP_TIME = 2  # カメラの調整時間（秒）
DEFAULT_OUTPUT_FILE = "test_photo.jpg"


def setup_camera():
    """
    カメラを初期化して静止画撮影用に設定する

    Returns:
        Picamera2: 初期化されたカメラオブジェクト
    """
    # カメラオブジェクトを初期化
    picam2 = Picamera2()

    # 静止画撮影用の設定を作成
    config = picam2.create_still_configuration()
    picam2.configure(config)

    return picam2


def capture_photo(picam2, output_file=DEFAULT_OUTPUT_FILE):
    """
    静止画を撮影してファイルに保存する

    Args:
        picam2 (Picamera2): カメラオブジェクト
        output_file (str): 保存するファイル名（デフォルト: test_photo.jpg）
    """
    # プレビューを開始
    picam2.start_preview(Preview.QTGL)
    picam2.start()

    # カメラの調整時間を確保（ホワイトバランスと露出の自動調整）
    time.sleep(CAMERA_WARMUP_TIME)

    # 写真を撮影
    picam2.capture_file(output_file)

    print(f"写真 '{output_file}' が保存されました")


def cleanup_camera(picam2):
    """
    カメラとプレビューを停止してリソースを解放する

    Args:
        picam2 (Picamera2): カメラオブジェクト
    """
    try:
        # プレビューを停止
        picam2.stop_preview()
    except Exception:
        # プレビューが開始されていない場合のエラーを無視
        pass

    # カメラを停止
    picam2.stop()


def main():
    """
    メイン関数：カメラを初期化して静止画を撮影
    """
    # カメラの初期化
    picam2 = setup_camera()

    try:
        # 写真撮影
        capture_photo(picam2)

    except KeyboardInterrupt:
        print("\n\n割り込み信号を受信しました。終了処理を実行中...")

    except Exception as e:
        print(f"写真撮影エラー: {e}")
        print("対処方法: カメラの接続を確認してください")

    finally:
        # 必ずリソースをクリーンアップ
        cleanup_camera(picam2)


if __name__ == "__main__":
    main()
