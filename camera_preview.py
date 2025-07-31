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
    
    def __init__(self, use_picamera=True):
        """初期化"""
        self.camera = None
        self.use_picamera = use_picamera and PICAMERA_AVAILABLE
        self.running = False
        
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
    
    # 引数でライブラリを選択可能
    use_opencv = '--opencv' in sys.argv or '--use-opencv' in sys.argv
    
    if use_opencv and not OPENCV_AVAILABLE:
        print("エラー: OpenCVがインストールされていません")
        sys.exit(1)
    
    # Picamera2が使えない場合は自動的にOpenCVを使用
    if not PICAMERA_AVAILABLE:
        use_opencv = True
    
    try:
        preview = CameraPreview(use_picamera=not use_opencv)
        preview.start()
    except KeyboardInterrupt:
        print("\n終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()