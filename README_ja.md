# 動画圧縮ツール - クロスプラットフォーム対応版

[English](README.md) | [中文](README_zh.md) | [한국어](README_ko.md) | [ไทย](README_th.md)

Windows、macOS、Linux対応の動画圧縮CLIツール。目標ファイルサイズを指定して、画質モード（音質優先/画質優先/バランス）を選択しながら動画を圧縮できます。

## 特徴

- **クロスプラットフォーム対応**: Windows、macOS、Linuxで動作
- **目標サイズを正確に指定**: MB単位で目標サイズを指定可能(小数点可)
- **画質モード選択**: 音質優先、画質優先、バランスから選択
  - 音質優先(192kbps): 音楽、講演、ASMR向け
  - 画質優先(128kbps): アニメ、映画、ゲーム実況向け
  - バランス(160kbps): 一般的な動画向け
- **リアルタイム進捗表示**: プログレスバーと残り時間を表示
- **2パスエンコーディング**: 高品質な圧縮を実現
- **バッチ処理対応**: ディレクトリ内の全動画を一括処理
- **ドライランモード**: 実際の圧縮前に結果をプレビュー
- **処理履歴ログ**: `~/.video-compressor/history.log` に自動保存
- **拡張子変換対応**: MP4, MOV, AVI, MKV, WebM, FLV
- **わかりやすいエラー表示**: 想定されるエラーを明確に通知

## 必須要件

### 対応OS
- **Windows**: Windows 10以降
- **macOS**: macOS 10.14以降
- **Linux**: Ubuntu 18.04+, Debian 10+, Fedora 30+, Arch Linux

### ソフトウェア
- Python 3.8以上
- ffmpeg

## インストール

### 1. ffmpegのインストール

#### Windows

**方法1: Chocolatey (推奨)**
```bash
choco install ffmpeg
```

**方法2: Scoop**
```bash
scoop install ffmpeg
```

**方法3: 手動インストール**
1. https://www.gyan.dev/ffmpeg/builds/ からダウンロード
2. C:\ffmpegに解凍
3. システム環境変数PATHにC:\ffmpeg\binを追加

#### macOS

```bash
brew install ffmpeg
```

#### Linux

**Ubuntu/Debian**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Fedora**
```bash
sudo dnf install ffmpeg
```

**Arch Linux**
```bash
sudo pacman -S ffmpeg
```

### 2. スクリプトのダウンロード

```bash
# GitHubからクローン
git clone https://github.com/hiroki-abe-58/video-compressor.git
cd video-compressor

# または、直接ダウンロード
curl -O https://raw.githubusercontent.com/hiroki-abe-58/video-compressor/main/compress_video.py
```

### 3. 実行権限付与 (macOS/Linux のみ)

```bash
chmod +x compress_video.py
```

## 使い方

### 基本的な使い方

**Windows**
```bash
python compress_video.py
# または
py compress_video.py
```

**macOS/Linux**
```bash
python3 compress_video.py
# または
./compress_video.py
```

### コマンドラインオプション

```bash
# 通常モード
python compress_video.py

# ドライランモード(実際の圧縮はせずプレビューのみ)
python compress_video.py --dry-run

# バージョンとプラットフォーム表示
python compress_video.py --version

# ヘルプ表示
python compress_video.py --help
```

### 実行フロー

#### フェーズ1: 動画パス入力
```
動画ファイルまたはディレクトリのパスを入力し、エンターを押してください:
> /path/to/video.mp4
```

**Windows例**: `C:\Users\username\Videos\video.mp4`
**macOS/Linux例**: `/home/username/Videos/video.mp4`

**ヒント**: エクスプローラー(Windows)やFinder(macOS)からドラッグ&ドロップでもOK

#### フェーズ2: 目標サイズ入力
```
ファイル名: video.mp4
現在のファイル容量: 150.50 MB
動画の長さ: 00:05:30

この動画を何MBまで圧縮しますか？数字を入力しエンターを押してください。(小数点可):
> 50
```

#### フェーズ2.5: 画質モード選択
```
【フェーズ2.5】画質モード選択
どのモードで圧縮しますか？

  1. 音質優先 (音声192kbps)
     音楽、講演、ASMR などの音が重要なコンテンツ向け

  2. 画質優先 (音声128kbps)
     アニメ、映画、ゲーム実況 などの映像が重要なコンテンツ向け

  3. バランス (音声160kbps)
     一般的な動画向け。音質と画質のバランスが取れた設定

番号を選択してください (デフォルト: 1):
```

#### フェーズ3: 拡張子変換(オプション)
```
拡張子は変換しますか？ (y/何も入力せずEnter):
```

#### フェーズ4: 圧縮実行
プログレスバーと残り時間が表示されます。

#### フェーズ5: 完了
```
圧縮が完了し、圧縮した動画ファイルは保存されました!
============================================================
画質モード: 画質優先
ファイル名: video--compressed--50.0MB--2025-11-03-15-30-45.mp4
目標サイズ: 50.00 MB
実際のサイズ: 49.85 MB
差分: 0.15 MB
圧縮率: 66.9%
処理時間: 00:10:21
============================================================
```

## 画質モード

### 目標50MBでの比較（5分の1080p動画の場合）

| モード | ビデオビットレート | 音声ビットレート | 適した用途 |
|--------|-------------------|-----------------|-----------|
| 音質優先 | 1145 kbps | 192 kbps | 音楽動画、コンサート、講演、ASMR |
| バランス | 1241 kbps | 160 kbps | Vlog、チュートリアル、一般的なコンテンツ |
| 画質優先 | 1337 kbps | 128 kbps | アニメ、映画、ゲーム実況、アクション動画 |

**画質優先モードは音質優先モードと比べて、ビデオに17%多くのビットレートを割り当てます！**

## プラットフォーム固有の注意事項

### Windows
- PowerShellまたはコマンドプロンプトを使用
- ファイルパスはバックスラッシュ (C:\Users\...)
- エクスプローラーからのドラッグ&ドロップ対応

### macOS
- ターミナルを使用
- ファイルパスはスラッシュ (/Users/...)
- Finderからのドラッグ&ドロップ対応

### Linux
- 任意のターミナルエミュレータを使用
- ファイルパスはスラッシュ (/home/...)
- 最新のターミナルでフルUnicode対応

## 処理履歴

全ての処理は以下に自動記録されます:
- **Windows**: `C:\Users\username\.video-compressor\history.log`
- **macOS**: `/Users/username/.video-compressor/history.log`
- **Linux**: `/home/username/.video-compressor/history.log`

### ログの確認方法

**Windows (PowerShell)**
```powershell
Get-Content ~\.video-compressor\history.log -Tail 20
```

**Windows (コマンドプロンプト)**
```cmd
type %USERPROFILE%\.video-compressor\history.log
```

**macOS/Linux**
```bash
tail -n 20 ~/.video-compressor/history.log
```

## ドライランモード

実際の圧縮を行わず、結果をプレビューできます:

```bash
python compress_video.py --dry-run
```

## バッチ処理

ディレクトリ内の全動画ファイルを一括処理:

```bash
python compress_video.py

# ディレクトリパスを入力
> /path/to/videos/
```

## 出力ファイル名の形式

```
[元ファイル名]--compressed--[目標サイズ]MB--[yyyy-mm-dd-hh-mm-ss].[拡張子]
```

## エラーハンドリング

このツールは以下のエラーを検出して、わかりやすく表示します:

- ffmpegが未インストール
- ファイルが存在しない
- サポートされていないファイル形式
- 目標サイズが現在のサイズより大きい
- 目標サイズが小さすぎる
- 無効な入力値
- エンコード中のエラー

## 技術詳細

### 圧縮アルゴリズム

1. **動画の長さを取得** (ffprobe使用)
2. **画質モードを選択** (音質優先/画質優先/バランス)
3. **目標サイズから必要なビデオビットレートを逆算**
4. **2パスエンコーディングで高品質圧縮**

### サポートファイル形式

**入力**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`, `.webm`, `.m4v`, `.mpeg`, `.mpg`

**出力**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`

## トラブルシューティング

### ffmpegが見つからない

**Windows**
```bash
# ffmpegがPATHにあるか確認
where ffmpeg

# 見つからない場合は再インストールまたはPATHに追加
```

**macOS**
```bash
brew install ffmpeg
```

**Linux**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
```

### 圧縮に時間がかかりすぎる
- 2パスエンコーディングは時間がかかる
- 長い動画だと数十分かかることもある
- プログレスバーで進捗確認できる

### 権限エラー (macOS/Linux)
```bash
chmod +x compress_video.py
```

### Pythonコマンドが見つからない

**Windows**: `python` の代わりに `py` を試す
**macOS/Linux**: `python` の代わりに `python3` を試す

## バージョン履歴

### v1.5.0
- Windows、Linux対応を追加
- プラットフォーム別のffmpegインストール手順
- クロスプラットフォームのパス処理

### v1.4.0
- 画質モード選択機能を追加（音質優先/画質優先/バランス）
- ログに画質モード情報を追加

### v1.3.0
- 処理履歴ログ機能を追加
- ログローテーション対応（10MB、5世代）

### v1.2.0
- ドライランモードを追加
- 画質レベル推定機能を追加

### v1.1.0
- バッチ処理機能を追加
- ディレクトリ入力対応

### v1.0.0
- 初期リリース (macOSのみ)
- 音質優先での基本的な圧縮機能

## ライセンス

MIT License

## 作者

[hiroki-abe-58](https://github.com/hiroki-abe-58)

## 謝辞

参考: https://note.com/genelab_999/n/n5db5c3a80793
