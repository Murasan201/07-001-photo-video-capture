# セットアップガイド

Raspberry Piで写真・動画キャプチャアプリを動作させるための環境構築手順です。

## 動作環境

- Raspberry Pi 4/5
- Raspberry Pi OS (Bookworm以降推奨)
- Raspberry Pi カメラモジュール v2/v3 または互換カメラ

## 1. カメラモジュールの接続

1. Raspberry Piの電源を切る
2. カメラモジュールのフラットケーブルをカメラポートに接続
3. ケーブルの向きに注意（青いテープ側がイーサネットポート側）
4. Raspberry Piの電源を入れる

## 2. カメラの動作確認

ターミナルを開き、以下のコマンドを実行します：

```bash
libcamera-hello --list-cameras
```

カメラが検出されると、以下のような出力が表示されます：

```
Available cameras
-----------------
0 : imx219 [3280x2464 10-bit RGGB] (/base/soc/i2c0mux/i2c@1/imx219@10)
```

## 3. パッケージリストの更新

```bash
sudo apt update
```

## 4. Picamera2のインストール

```bash
sudo apt install -y python3-picamera2
```

## 5. 仮想環境の作成

作業用ディレクトリに移動します：

```bash
cd ~/photo_video_capture
```

仮想環境を作成します：

```bash
python3 -m venv --system-site-packages venv
```

`--system-site-packages`オプションにより、システムにインストールしたPicamera2を仮想環境内から使用できます。

## 6. 仮想環境の有効化

```bash
source venv/bin/activate
```

プロンプトの先頭に`(venv)`が表示されれば成功です：

```
(venv) pi@raspberrypi:~/photo_video_capture $
```

## 7. インストールの確認

```bash
python3 -c "from picamera2 import Picamera2; print('OK')"
```

「OK」と表示されれば準備完了です。

## 仮想環境の終了

作業が終わったら、以下のコマンドで仮想環境を終了できます：

```bash
deactivate
```

## トラブルシューティング

### カメラが認識されない

カメラの接続状態を確認します：

```bash
vcgencmd get_camera
```

`supported=1 detected=1`と表示されれば正常です。表示されない場合は、ケーブルの接続を確認してください。

### Picamera2のインポートエラー

仮想環境を`--system-site-packages`オプションなしで作成した場合に発生します。仮想環境を作り直してください：

```bash
rm -rf venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
```
