#!/usr/bin/env python3
"""
カメラプレビューアプリ
リアルタイムでカメラ映像をデスクトップに表示する

文書番号: 07-001
作成日: 2025-07-29
"""

import sys
import time
import signal
from datetime import datetime

try:
    from picamera2 import Picamera2, Preview
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class CameraPreview:
    """カメラプレビュークラス"""
    
    def __init__(self, use_picamera=True, flip_horizontal=False, flip_vertical=False, rotate_180=False):
        """初期化
        
        Args:
            use_picamera: Picamera2を使用するかどうか
            flip_horizontal: 水平反転するかどうか
            flip_vertical: 垂直反転するかどうか
            rotate_180: 180度回転するかどうか（逆さま設置用）
        """
        self.camera = None
        self.use_picamera = use_picamera and PICAMERA_AVAILABLE
        self.running = False
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        self.rotate_180 = rotate_180
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        print("\n終了処理を開始します...")
        self.running = False
    
    def start_picamera_preview(self):
        """Picamera2でプレビュー開始（OpenCV使用）"""
        try:
            print("Picamera2を初期化中...")
            self.camera = Picamera2()
            
            # カメラ情報を表示
            camera_info = self.camera.camera_properties
            print(f"検出されたカメラ: {camera_info.get('Model', 'Unknown')}")
            
            # プレビュー設定（OpenCV用にRGB888形式を指定）
            preview_config = self.camera.create_preview_configuration(
                main={"size": (1920, 1080), "format": "RGB888"}
            )
            self.camera.configure(preview_config)
            
            # カメラ開始
            self.camera.start()
            print("プレビューを開始します（Qキーまたは×ボタンで終了）")
            
            self.running = True
            
            # ウィンドウ作成
            window_name = "Camera Preview - Press Q to quit"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 960, 540)  # 初期ウィンドウサイズ
            
            # FPS計算用
            fps_time = time.time()
            frame_count = 0
            
            while self.running:
                # フレームをNumPy配列として取得
                frame = self.camera.capture_array()
                
                # RGB888からBGRに変換（OpenCV用）
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # 映像の反転・回転処理
                frame_bgr = self._apply_transformations(frame_bgr)
                
                # FPS計算と表示
                frame_count += 1
                if frame_count % 30 == 0:
                    current_time = time.time()
                    fps = 30 / (current_time - fps_time)
                    fps_time = current_time
                    
                    # フレームにFPSを表示
                    cv2.putText(frame_bgr, f"FPS: {fps:.1f}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 現在時刻を表示
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame_bgr, timestamp, (10, frame_bgr.shape[0] - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # フレーム表示
                cv2.imshow(window_name, frame_bgr)
                
                # キー入力チェック
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nキー入力により終了します...")
                    self.running = False
                    break
                
                # ウィンドウが閉じられたかチェック
                try:
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                        print("\nウィンドウが閉じられました...")
                        self.running = False
                        break
                except:
                    # ウィンドウが既に閉じられている場合
                    self.running = False
                    break
                    
        except Exception as e:
            print(f"Picamera2エラー: {e}")
            raise
        finally:
            self._cleanup()
    
    def start_opencv_preview(self):
        """OpenCVでプレビュー開始"""
        try:
            print("OpenCVを初期化中...")
            
            # カメラ検出
            camera_index = 0
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                raise Exception("カメラを開けませんでした")
            
            # 解像度設定
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            print(f"USBカメラ（デバイス{camera_index}）でプレビュー開始")
            print("プレビューを開始します（Qキーまたは×ボタンで終了）")
            
            self.running = True
            
            # ウィンドウ作成
            window_name = "Camera Preview - Press Q to quit"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 960, 540)  # 初期ウィンドウサイズ
            
            # FPS計算用
            fps_time = time.time()
            frame_count = 0
            
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    print("フレーム取得エラー")
                    break
                
                # 映像の反転・回転処理
                frame = self._apply_transformations(frame)
                
                # FPS計算と表示
                frame_count += 1
                if frame_count % 30 == 0:
                    current_time = time.time()
                    fps = 30 / (current_time - fps_time)
                    fps_time = current_time
                    
                    # フレームにFPSを表示
                    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 現在時刻を表示
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10, frame.shape[0] - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # フレーム表示
                cv2.imshow(window_name, frame)
                
                # キー入力チェック
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nキー入力により終了します...")
                    self.running = False
                    break
                
                # ウィンドウが閉じられたかチェック
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    print("\nウィンドウが閉じられました...")
                    self.running = False
                    break
                    
        except Exception as e:
            print(f"OpenCVエラー: {e}")
            raise
        finally:
            self._cleanup()
    
    def _apply_transformations(self, frame):
        """映像の反転・回転処理を適用
        
        Args:
            frame: 入力フレーム
            
        Returns:
            変換後のフレーム
        """
        # 180度回転（逆さま設置対応）
        if self.rotate_180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        
        # 水平反転（左右反転）
        if self.flip_horizontal:
            frame = cv2.flip(frame, 1)
        
        # 垂直反転（上下反転）
        if self.flip_vertical:
            frame = cv2.flip(frame, 0)
        
        return frame
    
    def _cleanup(self):
        """クリーンアップ処理"""
        if self.use_picamera and self.camera:
            try:
                self.camera.stop()
                self.camera.close()
                cv2.destroyAllWindows()
                print("Picamera2を解放しました")
            except:
                pass
        elif not self.use_picamera and self.camera:
            try:
                self.camera.release()
                cv2.destroyAllWindows()
                print("OpenCVリソースを解放しました")
            except:
                pass
    
    def start(self):
        """プレビュー開始"""
        if self.use_picamera:
            print("Picamera2を使用してプレビューを開始します")
            self.start_picamera_preview()
        else:
            print("OpenCVを使用してプレビューを開始します")
            self.start_opencv_preview()


def main():
    """メイン関数"""
    # 利用可能なライブラリチェック
    if not PICAMERA_AVAILABLE and not OPENCV_AVAILABLE:
        print("エラー: 利用可能なカメラライブラリがありません")
        print("Picamera2またはOpenCVをインストールしてください")
        sys.exit(1)
    
    # コマンドライン引数解析
    use_opencv = '--opencv' in sys.argv or '--use-opencv' in sys.argv
    flip_horizontal = '--flip-h' in sys.argv or '--flip-horizontal' in sys.argv
    flip_vertical = '--flip-v' in sys.argv or '--flip-vertical' in sys.argv
    rotate_180 = '--rotate-180' in sys.argv or '--upside-down' in sys.argv
    
    if use_opencv and not OPENCV_AVAILABLE:
        print("エラー: OpenCVがインストールされていません")
        sys.exit(1)
    
    # Picamera2が使えない場合は自動的にOpenCVを使用
    if not PICAMERA_AVAILABLE:
        use_opencv = True
    
    # ヘルプ表示
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
カメラプレビューアプリ - 使用方法

基本実行:
  python3 camera_preview.py

オプション:
  --opencv, --use-opencv    OpenCVバックエンドを使用（USBカメラ用）
  --flip-h, --flip-horizontal  水平反転（左右反転）
  --flip-v, --flip-vertical    垂直反転（上下反転）
  --rotate-180, --upside-down  180度回転（逆さま設置用）
  --help, -h                   このヘルプを表示

使用例:
  # 基本実行
  export DISPLAY=:0
  python3 camera_preview.py
  
  # 逆さま設置のカメラ用（推奨）
  python3 camera_preview.py --rotate-180
  
  # 水平反転
  python3 camera_preview.py --flip-h
  
  # 複数の変換を組み合わせ
  python3 camera_preview.py --rotate-180 --flip-h

操作:
  Q キー         - 終了
  × ボタン       - 終了
        """)
        sys.exit(0)
    
    try:
        preview = CameraPreview(
            use_picamera=not use_opencv,
            flip_horizontal=flip_horizontal,
            flip_vertical=flip_vertical,
            rotate_180=rotate_180
        )
        
        # 適用された変換を表示
        transforms = []
        if rotate_180:
            transforms.append("180度回転")
        if flip_horizontal:
            transforms.append("水平反転")
        if flip_vertical:
            transforms.append("垂直反転")
        
        if transforms:
            print(f"適用された変換: {', '.join(transforms)}")
        
        preview.start()
    except KeyboardInterrupt:
        print("\n終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()