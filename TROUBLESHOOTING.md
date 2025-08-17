# トラブルシューティングガイド

このドキュメントでは、写真／動画キャプチャアプリとカメラプレビューアプリの実行時に発生した問題と解決方法を記録します。

## 実行環境
- **初回実行日**: 2025年7月29日
- **最終更新日**: 2025年8月3日
- **環境**: Raspberry Pi 5
- **OS**: Linux 6.12.25+rpt-rpi-2712
- **Python**: 3.11
- **カメラ**: imx708_noir (NoIRカメラモジュール)

## 発生した問題と解決方法

### 1. 仮想環境でのPicamera2インポートエラー

#### 問題
```bash
source venv/bin/activate && python photo_video_capture.py photo
```
実行時に以下のエラーが発生：
```
カメラエラー: 利用可能なカメラライブラリがありません
```

仮想環境内でPicamera2をインポートしようとすると：
```python
ModuleNotFoundError: No module named 'picamera2'
```

#### 原因
Picamera2はシステムパッケージとしてインストールされるため、仮想環境からは直接アクセスできない。

#### 解決方法
1. システムパッケージのPicamera2をインストール：
   ```bash
   sudo apt update
   sudo apt install python3-picamera2
   ```

2. 仮想環境を使わずに直接実行：
   ```bash
   python3 photo_video_capture.py photo
   ```

### 2. OpenCVでのフレーム取得失敗

#### 問題
OpenCVバックエンドを使用した際にフレーム取得に失敗：
```
フレーム取得失敗
エラー: 撮影に失敗しました
```

#### 原因
- Raspberry Piカメラモジュールが接続されている場合、OpenCVではなくPicamera2を使用する必要がある
- OpenCVはUSBカメラ用のフォールバックオプション

#### 解決方法
Raspberry Piカメラが接続されている場合は、Picamera2を使用する（デフォルト動作）。

### 3. numpy互換性エラー（追加：2025年8月3日）

#### 問題
Picamera2インポート時に以下のエラーが発生：
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

#### 原因
numpy 2.2.6とPicamera2 0.3.30の間にバイナリ互換性の問題がある。Picamera2が古いnumpyバージョンでコンパイルされているため、新しいnumpyでは動作しない。

#### 解決方法
numpyを互換性のあるバージョン（1.24.2）にダウングレード：
```bash
# システムパッケージマネージャを上書きする必要があるため、--break-system-packagesを使用
pip3 install --break-system-packages --force-reinstall numpy==1.24.2
```

#### 確認方法
```bash
# numpyバージョン確認
python3 -c "import numpy; print('numpy version:', numpy.__version__)"

# カメラ動作確認
rpicam-still -o test.jpg -t 1

# カメラプレビュー実行
export DISPLAY=:0
python3 camera_preview.py
```

#### 注意事項
- 他のパッケージ（scipy、opencv-python等）との依存関係に影響する可能性がある
- システム更新時にnumpyが自動更新される可能性があるため、定期的に確認が必要

### 4. Qt platform plugin "xcb" エラー（カメラプレビュー）

#### 問題
カメラプレビューアプリ実行時に以下のエラーが発生：
```
qt.qpa.xcb: could not connect to display 
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

#### 原因
1. **DISPLAY環境変数の未設定**: SSH接続やターミナル環境でDISPLAY変数が設定されていない
2. **Qt platform plugin競合**: Picamera2のQTGLプレビューとOpenCVライブラリ間の競合

#### 解決方法

**方法1: DISPLAY環境変数の設定**
```bash
export DISPLAY=:0
python3 camera_preview.py
```

**方法2: Picamera2 + OpenCVアプローチ（実装済み）**
- Picamera2でRGB888形式のフレームを取得
- OpenCVの`cv2.imshow()`で表示
- QTGLプレビューの代わりにOpenCVウィンドウを使用

### 5. 暗い環境での映像確認問題（カメラプレビュー）

#### 問題
カメラプレビューウィンドウは表示されるが、画面が真っ暗で映像内容が確認できない。

#### 原因
部屋の照明が消灯しており、カメラが暗い環境を正しく撮影していた。

#### 解決方法
1. **部屋の照明を点灯**: 十分な照明を確保
2. **カメラの向き調整**: 明るい場所にカメラを向ける
3. **露出設定の調整**（上級者向け）:
   ```python
   picam2.set_controls({"ExposureTime": 10000, "AnalogueGain": 1.0})
   ```

### 6. カメラデバイスの確認方法

#### 利用可能なカメラの確認
1. V4L2デバイスの一覧表示：
   ```bash
   v4l2-ctl --list-devices
   ```

2. libcameraでカメラを確認：
   ```bash
   libcamera-hello --list-cameras
   ```

#### 検出されたデバイス
- **Raspberry Piカメラ**: imx708_noir (NoIRカメラモジュール)
- **解像度**: 4608x2592 (最大)
- **インターフェース**: CSI

## 成功した実行例

### 写真撮影
```bash
python3 photo_video_capture.py photo
```

出力：
```
デバイス検出: Picamera2を使用します
検出されたカメラ: imx708_noir
静止画撮影開始: 1920x1080, 形式: jpg
Picamera2初期化完了: 1920x1080
静止画撮影完了: photo_20250729_225609.jpg
成功: ファイルが保存されました - photo_20250729_225609.jpg
カメラリソースを解放しました
```

### カメラプレビュー
```bash
export DISPLAY=:0
python3 camera_preview.py
```

出力：
```
Picamera2を使用してプレビューを開始します
Picamera2を初期化中...
検出されたカメラ: imx708_noir
プレビューを開始します（Qキーまたは×ボタンで終了）
```

表示される機能：
- **リアルタイムプレビュー**: 1920x1080解像度
- **FPS表示**: 30フレーム毎に更新
- **タイムスタンプ**: 現在時刻を画面下部に表示
- **画像変換**: --rotate-180、--flip-h、--flip-vオプション対応

## 推奨事項

### 1. ライブラリの使い分け
- **Raspberry Piカメラモジュール**: Picamera2を使用（推奨）
- **USBカメラ**: OpenCVを使用（`--use-opencv`オプション）

### 2. 仮想環境の制限
- Picamera2はシステムパッケージのため、仮想環境では使用できない
- OpenCVは仮想環境にインストール可能：
  ```bash
  source venv/bin/activate
  pip install opencv-python
  ```

### 3. 依存関係の管理
- **requirements.txt**: OpenCV用（pip install可能）
- **システムパッケージ**: Picamera2用（apt install必要）

## よくある質問

### Q: 仮想環境でPicamera2を使いたい
A: 現時点では、Picamera2はシステムパッケージとしてのみ提供されているため、仮想環境での直接使用はできません。システムのPython3を使用するか、仮想環境にシステムサイトパッケージへのアクセスを許可する必要があります。

### Q: USBカメラを使用したい
A: `--use-opencv`オプションを使用してください：
```bash
python3 photo_video_capture.py photo --use-opencv
```

### Q: カメラが検出されない
A: 以下を確認してください：
1. カメラの物理的な接続
2. カメラインターフェースの有効化（`sudo raspi-config`）
3. 必要なドライバーのインストール
4. `libcamera-hello --list-cameras`でカメラの認識確認

### Q: カメラプレビューが表示されない
A: 以下を試してください：
1. DISPLAY環境変数の設定：`export DISPLAY=:0`
2. OpenCVのインストール確認：`sudo apt install python3-opencv`
3. 十分な照明の確保
4. SSH経由の場合はX11転送を有効化：`ssh -X pi@raspberrypi.local`

### Q: プレビューが逆さまに表示される
A: カメラが逆さまに設置されている場合：
```bash
python3 camera_preview.py --rotate-180
```

その他の画像変換オプション：
- `--flip-h`: 水平反転（鏡像）
- `--flip-v`: 垂直反転
- 複数組み合わせ可能：`--rotate-180 --flip-h`

## 参考リンク
- [Picamera2公式ドキュメント](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi Camera Module Documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)

---
最終更新: 2025-08-03