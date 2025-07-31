# カメラプレビュー トラブルシューティングガイド

このドキュメントでは、カメラプレビューアプリ（`camera_preview.py`）の実行時に発生した問題と解決方法を詳細に記録します。

## 実行日時
- **日付**: 2025年7月29日
- **環境**: Raspberry Pi 5
- **OS**: Linux 6.12.25+rpt-rpi-2712
- **Python**: 3.11
- **カメラ**: imx708_noir (NoIRカメラモジュール)

## 発生した問題と解決方法

### 1. Qt platform plugin "xcb" エラー

#### 問題
カメラプレビューアプリ実行時に以下のエラーが発生し、アプリケーションが中止される：

```
qt.qpa.xcb: could not connect to display 
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, xcb.
```

#### 原因
1. **DISPLAY環境変数の未設定**: SSH接続やターミナル環境でDISPLAY変数が設定されていない
2. **Qt platform plugin競合**: Picamera2のQTGLプレビューとOpenCVライブラリ間の競合
3. **権限問題**: `/run/user/1000`ディレクトリの権限設定（警告レベル）

#### 解決方法

**方法1: DISPLAY環境変数の設定**
```bash
export DISPLAY=:0
python3 camera_preview.py
```

**方法2: Picamera2 + OpenCVアプローチ（推奨・実装済み）**

従来のPicamera2 QTGLプレビューの代わりに、以下のアプローチを採用：

1. **Picamera2でフレーム取得**: RGB888形式でカメラからフレームを取得
2. **OpenCVで表示**: `cv2.imshow()`を使用してフレームを表示

実装コード（抜粋）：
```python
# Picamera2設定（RGB888形式でフレーム取得）
preview_config = self.camera.create_preview_configuration(
    main={"size": (1920, 1080), "format": "RGB888"}
)
self.camera.configure(preview_config)
self.camera.start()

# フレーム取得と表示ループ
while self.running:
    # フレームをNumPy配列として取得
    frame = self.camera.capture_array()
    
    # RGB888からBGRに変換（OpenCV用）
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # フレーム表示
    cv2.imshow("Camera Preview", frame_bgr)
    
    # キー入力チェック（Qで終了）
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == ord('Q'):
        break
```

### 2. 暗い環境での映像確認問題

#### 問題
カメラプレビューウィンドウは表示されるが、画面が真っ暗で映像内容が確認できない。

#### 原因
部屋の照明が消灯しており、カメラが暗い環境を正しく撮影していた。

#### 解決方法
1. **部屋の照明を点灯**: 十分な照明を確保
2. **カメラの向き調整**: 明るい場所にカメラを向ける
3. **露出設定の調整**（上級者向け）:
   ```python
   # カメラの露出設定例
   picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})
   ```

#### 結果
照明を点灯後、カメラプレビューが正常に表示され、リアルタイムでの映像確認が可能になった。

### 3. OpenCVライブラリの依存関係問題

#### 問題
初回実行時にOpenCVがインストールされていないエラー：
```
エラー: OpenCVがインストールされていません
```

#### 原因
システムレベルでのOpenCVライブラリが未インストール。

#### 解決方法
```bash
sudo apt update
sudo apt install -y python3-opencv
```

インストール後の確認：
```bash
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

### 4. GStreamerメモリ割り当てエラー

#### 問題
OpenCVバックエンド使用時にGStreamerのメモリ割り当てに失敗：
```
[ WARN:0@1.830] global ./modules/videoio/src/cap_gstreamer.cpp (2401) handleMessage OpenCV | GStreamer warning: Embedded video playback halted; module v4l2src0 reported: Failed to allocate required memory.
```

#### 原因
Raspberry PiカメラがOpenCVのVideoCapture経由では適切に動作しない。

#### 解決方法
Picamera2を使用する（デフォルト動作）。OpenCVはUSBカメラ用のフォールバックとして位置づける。

## 成功した実行例

### カメラプレビュー起動
```bash
export DISPLAY=:0
python3 camera_preview.py
```

### 成功時の出力
```
Picamera2を使用してプレビューを開始します
Picamera2を初期化中...
検出されたカメラ: imx708_noir
プレビューを開始します（Qキーまたは×ボタンで終了）
```

### 表示される機能
- **リアルタイムプレビュー**: 1920x1080解像度
- **FPS表示**: 30フレーム毎に更新
- **タイムスタンプ**: 現在時刻を画面下部に表示
- **キー操作**: Qキーで終了
- **ウィンドウ操作**: ×ボタンで終了

## 実装上の改善点

### 1. エラーハンドリングの強化
```python
# ウィンドウが閉じられたかチェック
try:
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
        self.running = False
        break
except:
    # ウィンドウが既に閉じられている場合
    self.running = False
    break
```

### 2. リソース管理の改善
```python
def _cleanup(self):
    """クリーンアップ処理"""
    if self.use_picamera and self.camera:
        try:
            self.camera.stop()
            self.camera.close()
            cv2.destroyAllWindows()
        except:
            pass
```

### 3. 色空間変換の最適化
```python
# RGB888からBGRに変換（OpenCV用）
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
```

## 推奨事項

### 1. 開発環境設定
- **システムパッケージ使用**: Picamera2とOpenCVの両方をシステムレベルでインストール
- **DISPLAY変数設定**: GUI使用時は必ず`export DISPLAY=:0`を実行
- **照明環境**: カメラテスト時は十分な照明を確保

### 2. アーキテクチャ選択
- **Raspberry Piカメラ**: Picamera2 + OpenCV組み合わせが最適
- **USBカメラ**: OpenCV単体で使用
- **ヘッドレス運用**: Preview.NULLまたはDRMプレビューを検討

### 3. パフォーマンス最適化
- **解像度調整**: 用途に応じて解像度を下げる（例：1280x720）
- **フレームレート制御**: `cv2.waitKey()`の値を調整
- **メモリ管理**: 定期的なリソース解放

## よくある質問

### Q: SSH経由でプレビューを表示したい
A: X11転送を有効化してください：
```bash
ssh -X pi@raspberrypi.local
export DISPLAY=:0
python3 camera_preview.py
```

### Q: プレビューのフレームレートが遅い
A: 以下を試してください：
1. 解像度を下げる：`{"size": (1280, 720)}`
2. フォーマットを変更：`"format": "YUV420"`
3. `waitKey`の値を調整：`cv2.waitKey(10)`

### Q: カメラの画質を向上させたい
A: Picamera2の制御パラメータを調整：
```python
picam2.set_controls({
    "Brightness": 0.1,
    "Contrast": 1.1,
    "Saturation": 1.2
})
```

### Q: 複数のカメラを使用したい
A: カメラインデックスを指定：
```python
picam2 = Picamera2(camera_num=0)  # 最初のカメラ
# picam2 = Picamera2(camera_num=1)  # 2番目のカメラ
```

## トラブルシューティング手順

### 1. 基本確認
```bash
# カメラ検出確認
libcamera-hello --list-cameras

# 依存関係確認
python3 -c "import picamera2, cv2; print('Libraries OK')"

# 環境変数確認
echo $DISPLAY
```

### 2. 段階的テスト
```bash
# 1. libcameraテスト
libcamera-hello -t 5000

# 2. 写真撮影テスト
python3 photo_video_capture.py photo

# 3. プレビューテスト
export DISPLAY=:0
python3 camera_preview.py
```

### 3. ログ分析
- **Qt警告**: 動作に影響しない警告として無視
- **GStreamerエラー**: OpenCV使用時は正常（Picamera2使用推奨）
- **権限警告**: `/run/user/1000`の権限は動作に影響しない

## 参考リンク
- [Picamera2公式ドキュメント](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [OpenCV Python チュートリアル](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)

---
最終更新: 2025-07-29  
作成者: Claude Code Assistant