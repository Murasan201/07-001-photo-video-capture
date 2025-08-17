#!/usr/bin/env python3
"""
写真／動画キャプチャアプリ
Raspberry PiカメラモジュールまたはUSBカメラを用いて静止画および動画を撮影するアプリケーション

文書番号: 07-001
作成日: 2025-07-17
"""

import argparse
import os
import sys
import time
import datetime
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    # Picamera2を優先的に使用
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FileOutput
    PICAMERA_AVAILABLE = True
except (ImportError, ValueError) as e:
    # ImportErrorまたはnumpy互換性エラーをキャッチ
    print(f"Picamera2利用不可: {e}")
    PICAMERA_AVAILABLE = False

try:
    # OpenCVをフォールバックとして使用
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class CameraError(Exception):
    """カメラ関連のエラー"""
    pass


class PhotoVideoCapture:
    """写真・動画キャプチャクラス"""
    
    def __init__(self, use_picamera: bool = True):
        """
        初期化
        
        Args:
            use_picamera: Picamera2を使用するかどうか
        """
        self.camera = None
        self.use_picamera = use_picamera and PICAMERA_AVAILABLE
        self.output_dir = Path.cwd()
        
        # カメラライブラリの選択
        if self.use_picamera:
            print("デバイス検出: Picamera2を使用します")
        elif OPENCV_AVAILABLE:
            print("デバイス検出: OpenCVを使用します")
        else:
            raise CameraError("利用可能なカメラライブラリがありません")
    
    def detect_camera(self) -> bool:
        """
        カメラデバイスの検出
        
        Returns:
            bool: カメラが検出された場合True
        """
        try:
            if self.use_picamera:
                # Picamera2でのデバイス検出
                self.camera = Picamera2()
                camera_properties = self.camera.camera_properties
                print(f"検出されたカメラ: {camera_properties.get('Model', 'Unknown')}")
                return True
            else:
                # OpenCVでのデバイス検出
                for i in range(10):  # 最大10個のデバイスをチェック
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        print(f"検出されたUSBカメラ: デバイス{i}")
                        cap.release()
                        return True
                return False
        except Exception as e:
            print(f"カメラ検出エラー: {e}")
            return False
    
    def initialize_camera(self, width: int = 1920, height: int = 1080) -> bool:
        """
        カメラの初期化
        
        Args:
            width: 画像幅
            height: 画像高さ
            
        Returns:
            bool: 初期化成功時True
        """
        try:
            if self.use_picamera:
                if self.camera is None:
                    self.camera = Picamera2()
                
                # 設定の構築
                config = self.camera.create_still_configuration(
                    main={"size": (width, height)}
                )
                self.camera.configure(config)
                self.camera.start()
                print(f"Picamera2初期化完了: {width}x{height}")
                return True
            else:
                self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    return False
                
                # カメラの初期化を待つ
                time.sleep(2)
                
                # 解像度設定
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                print(f"OpenCV初期化完了: {width}x{height}")
                return True
        except Exception as e:
            print(f"カメラ初期化エラー: {e}")
            return False
    
    def capture_photo(self, width: int, height: int, format_type: str, output_dir: str) -> Optional[str]:
        """
        静止画撮影
        
        Args:
            width: 画像幅
            height: 画像高さ
            format_type: ファイル形式 (jpg/png)
            output_dir: 保存ディレクトリ
            
        Returns:
            str: 保存されたファイルパス（失敗時None）
        """
        try:
            # 保存ディレクトリの作成
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # ファイル名生成（タイムスタンプ付き）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.{format_type}"
            filepath = output_path / filename
            
            print(f"静止画撮影開始: {width}x{height}, 形式: {format_type}")
            
            if self.use_picamera:
                # Picamera2での撮影
                if not self.initialize_camera(width, height):
                    return None
                
                # 撮影実行
                self.camera.capture_file(str(filepath))
                print(f"静止画撮影完了: {filepath}")
                
            else:
                # OpenCVでの撮影
                if not self.initialize_camera(width, height):
                    return None
                
                # フレーム取得（複数回試行）
                ret, frame = False, None
                for attempt in range(5):
                    ret, frame = self.camera.read()
                    if ret:
                        break
                    time.sleep(0.5)
                
                if not ret:
                    print("フレーム取得失敗（5回試行）")
                    return None
                
                # ファイル保存
                cv2.imwrite(str(filepath), frame)
                print(f"静止画撮影完了: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            print(f"静止画撮影エラー: {e}")
            return None
    
    def record_video(self, width: int, height: int, fps: int, duration: int, output_dir: str) -> Optional[str]:
        """
        動画録画
        
        Args:
            width: 動画幅
            height: 動画高さ
            fps: フレームレート
            duration: 録画時間（秒）
            output_dir: 保存ディレクトリ
            
        Returns:
            str: 保存されたファイルパス（失敗時None）
        """
        try:
            # 保存ディレクトリの作成
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # ファイル名生成（タイムスタンプ付き）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            filepath = output_path / filename
            
            print(f"動画録画開始: {width}x{height}, FPS: {fps}, 時間: {duration}秒")
            
            if self.use_picamera:
                # Picamera2での録画
                if not self.initialize_camera(width, height):
                    return None
                
                # エンコーダーとアウトプット設定
                encoder = H264Encoder(bitrate=10000000)
                output = FileOutput(str(filepath))
                
                # 録画開始
                self.camera.start_recording(encoder, output)
                time.sleep(duration)
                self.camera.stop_recording()
                
                print(f"動画録画完了: {filepath}")
                
            else:
                # OpenCVでの録画
                if not self.initialize_camera(width, height):
                    return None
                
                # VideoWriter設定
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
                
                start_time = time.time()
                while time.time() - start_time < duration:
                    ret, frame = self.camera.read()
                    if ret:
                        out.write(frame)
                    else:
                        break
                
                out.release()
                print(f"動画録画完了: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            print(f"動画録画エラー: {e}")
            return None
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        try:
            if self.camera is not None:
                if self.use_picamera:
                    self.camera.stop()
                    self.camera.close()
                else:
                    self.camera.release()
                print("カメラリソースを解放しました")
        except Exception as e:
            print(f"クリーンアップエラー: {e}")


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(
        description="写真／動画キャプチャアプリ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 静止画撮影（1920x1080、JPG形式）
  python photo_video_capture.py photo --width 1920 --height 1080 --format jpg

  # 動画録画（1280x720、30fps、10秒間）
  python photo_video_capture.py video --width 1280 --height 720 --fps 30 --duration 10

  # 保存先指定
  python photo_video_capture.py photo --output ./captures
        """
    )
    
    # サブコマンド
    subparsers = parser.add_subparsers(dest="mode", help="動作モード")
    
    # 静止画撮影
    photo_parser = subparsers.add_parser("photo", help="静止画撮影")
    photo_parser.add_argument("--width", type=int, default=1920, help="画像幅（デフォルト: 1920）")
    photo_parser.add_argument("--height", type=int, default=1080, help="画像高さ（デフォルト: 1080）")
    photo_parser.add_argument("--format", choices=["jpg", "png"], default="jpg", help="ファイル形式（デフォルト: jpg）")
    
    # 動画録画
    video_parser = subparsers.add_parser("video", help="動画録画")
    video_parser.add_argument("--width", type=int, default=1280, help="動画幅（デフォルト: 1280）")
    video_parser.add_argument("--height", type=int, default=720, help="動画高さ（デフォルト: 720）")
    video_parser.add_argument("--fps", type=int, default=30, help="フレームレート（デフォルト: 30）")
    video_parser.add_argument("--duration", type=int, default=10, help="録画時間（秒、デフォルト: 10）")
    
    # 共通オプション
    parser.add_argument("--output", type=str, default="./", help="保存ディレクトリ（デフォルト: ./）")
    parser.add_argument("--use-opencv", action="store_true", help="OpenCVを強制使用")
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    # モードが指定されていない場合はヘルプを表示
    if args.mode is None:
        print("エラー: モードを指定してください（photo または video）")
        print("使用方法: python photo_video_capture.py {photo|video} [オプション]")
        sys.exit(1)
    
    # カメラライブラリの選択
    use_picamera = not args.use_opencv
    
    # カメラオブジェクト作成
    try:
        capture = PhotoVideoCapture(use_picamera=use_picamera)
        
        # カメラ検出
        if not capture.detect_camera():
            print("エラー: カメラが検出されませんでした")
            sys.exit(1)
        
        # 撮影実行
        result = None
        if args.mode == "photo":
            result = capture.capture_photo(
                width=args.width,
                height=args.height,
                format_type=args.format,
                output_dir=args.output
            )
        elif args.mode == "video":
            result = capture.record_video(
                width=args.width,
                height=args.height,
                fps=args.fps,
                duration=args.duration,
                output_dir=args.output
            )
        
        if result:
            print(f"成功: ファイルが保存されました - {result}")
        else:
            print("エラー: 撮影に失敗しました")
            sys.exit(1)
            
    except CameraError as e:
        print(f"カメラエラー: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n撮影が中断されました")
    except Exception as e:
        print(f"予期しないエラー: {e}")
        sys.exit(1)
    finally:
        # リソースのクリーンアップ
        if 'capture' in locals():
            capture.cleanup()


if __name__ == "__main__":
    main()