# トラブルシューティングガイド

このドキュメントでは、写真／動画キャプチャアプリの実行時に発生した問題と解決方法を記録します。

## 実行日時
- **日付**: 2025年7月29日
- **環境**: Raspberry Pi 5
- **OS**: Linux 6.12.25+rpt-rpi-2712
- **Python**: 3.11

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

### 3. カメラデバイスの確認方法

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

## 参考リンク
- [Picamera2公式ドキュメント](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi Camera Module Documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)

---
最終更新: 2025-07-29