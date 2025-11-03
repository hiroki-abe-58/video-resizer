#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画圧縮CLIツール - 音質・画質モード選択対応版 (Windows/macOS/Linux対応)
"""

__version__ = "1.5.0"

import os
import sys
import subprocess
import re
import json
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from logging.handlers import RotatingFileHandler


class QualityMode:
    """画質モード定義"""
    AUDIO_PRIORITY = "audio_priority"
    VIDEO_PRIORITY = "video_priority"
    BALANCED = "balanced"
    
    MODES = {
        AUDIO_PRIORITY: {
            "name": "音質優先",
            "audio_bitrate": 192,
            "description": "音声を高品質に保ち、ビデオを調整（音楽、講演、ASMR向け）"
        },
        VIDEO_PRIORITY: {
            "name": "画質優先",
            "audio_bitrate": 128,
            "description": "画質を優先し、音声を最低限に抑える（アニメ、映画、ゲーム実況向け）"
        },
        BALANCED: {
            "name": "バランス",
            "audio_bitrate": 160,
            "description": "音質と画質をバランスよく（一般的な動画向け）"
        }
    }


class VideoCompressor:
    """動画圧縮を管理するクラス"""
    
    # サポートする動画形式
    SUPPORTED_FORMATS = [
        '.mp4', '.avi', '.mov', '.mkv', '.flv', 
        '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'
    ]
    
    # 変換可能な拡張子
    CONVERT_FORMATS = {
        '1': ('mp4', 'MP4 (H.264)'),
        '2': ('mov', 'MOV (QuickTime)'),
        '3': ('avi', 'AVI'),
        '4': ('mkv', 'MKV (Matroska)'),
        '5': ('webm', 'WebM'),
        '6': ('flv', 'FLV (Flash Video)'),
    }
    
    def __init__(self, dry_run: bool = False):
        self.input_files: List[Path] = []
        self.target_size_mb: Optional[float] = None
        self.output_format: Optional[str] = None
        self.quality_mode: Optional[str] = None
        self.batch_mode: bool = False
        self.dry_run: bool = dry_run
        self.logger = self._setup_logger()
        self.start_time: Optional[float] = None
        self.platform = platform.system()
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーのセットアップ"""
        # ログディレクトリ作成（Windows/macOS/Linux対応）
        log_dir = Path.home() / '.video-compressor'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / 'history.log'
        
        logger = logging.getLogger('VideoCompressor')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
        return logger
    
    def check_ffmpeg(self) -> bool:
        """ffmpegがインストールされているか確認"""
        try:
            subprocess.run(
                ['ffmpeg', '-version'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_ffmpeg_install_instructions(self) -> str:
        """プラットフォームに応じたffmpegインストール方法を取得"""
        if self.platform == 'Darwin':  # macOS
            return """以下のコマンドでインストールしてください:
  brew install ffmpeg"""
        elif self.platform == 'Windows':
            return """以下のいずれかの方法でインストールしてください:

方法1: Chocolatey (推奨)
  choco install ffmpeg

方法2: Scoop
  scoop install ffmpeg

方法3: 手動インストール
  1. https://www.gyan.dev/ffmpeg/builds/ から ffmpeg-release-essentials.zip をダウンロード
  2. 解凍してC:\\ffmpegに配置
  3. システム環境変数PATHにC:\\ffmpeg\\binを追加"""
        else:  # Linux
            return """以下のコマンドでインストールしてください:

Ubuntu/Debian:
  sudo apt update && sudo apt install ffmpeg

Fedora:
  sudo dnf install ffmpeg

Arch:
  sudo pacman -S ffmpeg"""
    
    def get_video_files_from_directory(self, directory: Path) -> List[Path]:
        """ディレクトリ内の全動画ファイルを取得"""
        video_files = []
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                video_files.append(file_path)
        return sorted(video_files)
    
    def get_video_info(self, video_path: Path) -> dict:
        """ffprobeで動画情報を取得"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"動画情報取得失敗: {video_path.name}, エラー: {e}")
            raise RuntimeError(f"動画情報の取得に失敗したわ: {e}")
        except json.JSONDecodeError:
            self.logger.error(f"JSON解析失敗: {video_path.name}")
            raise RuntimeError("動画情報のパースに失敗。ファイルが壊れてるかも")
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """ファイルサイズをMB単位で取得"""
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    
    def get_audio_bitrate_for_mode(self, mode: str) -> int:
        """モードに応じた音声ビットレートを取得"""
        return QualityMode.MODES[mode]["audio_bitrate"]
    
    def calculate_bitrate(self, target_size_mb: float, duration: float, audio_bitrate: int) -> int:
        """目標ファイルサイズから必要なビデオビットレートを計算"""
        target_size_bits = target_size_mb * 8 * 1024 * 1024
        audio_bitrate_bps = audio_bitrate * 1000
        audio_total_bits = audio_bitrate_bps * duration
        video_total_bits = target_size_bits - audio_total_bits
        
        if video_total_bits <= 0:
            raise ValueError("目標サイズが小さすぎる。音声だけで容量オーバーするわ")
        
        video_bitrate_bps = video_total_bits / duration
        return int(video_bitrate_bps / 1000 * 0.95)
    
    def estimate_quality_level(self, video_bitrate: int, video_info: dict) -> str:
        """ビットレートから予想画質レベルを判定"""
        video_stream = None
        for stream in video_info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            return "不明"
        
        width = video_stream.get('width', 0)
        height = video_stream.get('height', 0)
        
        if height >= 2160:
            excellent = 35000
            good = 20000
            acceptable = 13000
        elif height >= 1440:
            excellent = 16000
            good = 10000
            acceptable = 6000
        elif height >= 1080:
            excellent = 8000
            good = 5000
            acceptable = 3000
        elif height >= 720:
            excellent = 5000
            good = 2500
            acceptable = 1500
        elif height >= 480:
            excellent = 2500
            good = 1000
            acceptable = 500
        else:
            excellent = 1000
            good = 500
            acceptable = 250
        
        if video_bitrate >= excellent:
            return "最高画質 (ほぼ劣化なし)"
        elif video_bitrate >= good:
            return "高画質 (軽微な劣化)"
        elif video_bitrate >= acceptable:
            return "標準画質 (許容範囲)"
        else:
            return "低画質 (明らかに劣化)"
    
    def compress_video(self, input_path: Path, output_path: Path, video_bitrate: int, 
                      video_info: dict, audio_bitrate: int, current: int = 1, total: int = 1):
        """動画を圧縮(2パスエンコーディング)"""
        
        if total > 1:
            print(f"\n🎬 [{current}/{total}] {input_path.name} を圧縮中...")
        else:
            print(f"\n🎬 圧縮中です...")
        print("=" * 60)
        
        # プラットフォームに応じたnullデバイス
        null_output = 'NUL' if self.platform == 'Windows' else '/dev/null'
        
        # 1パス目
        print("\n[1/2] 1パス目: ビットレート解析中...")
        pass1_cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', f'{video_bitrate}k',
            '-pass', '1',
            '-an',
            '-f', 'null',
            '-y',
            null_output
        ]
        
        try:
            self._run_ffmpeg_with_progress(pass1_cmd, "1パス目", video_info)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"1パス目エンコード失敗: {input_path.name}, エラー: {e}")
            raise RuntimeError(f"1パス目のエンコードに失敗: {e}")
        
        # 2パス目
        print("\n[2/2] 2パス目: 最終エンコード中...")
        pass2_cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', f'{video_bitrate}k',
            '-pass', '2',
            '-c:a', 'aac',
            '-b:a', f'{audio_bitrate}k',
            '-y',
            str(output_path)
        ]
        
        try:
            self._run_ffmpeg_with_progress(pass2_cmd, "2パス目", video_info)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"2パス目エンコード失敗: {input_path.name}, エラー: {e}")
            raise RuntimeError(f"2パス目のエンコードに失敗: {e}")
        
        self._cleanup_ffmpeg_logs()
    
    def _run_ffmpeg_with_progress(self, cmd: list, phase: str, video_info: dict):
        """ffmpegを実行し、進捗を表示"""
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        duration = float(video_info['format']['duration'])
        
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            
            time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
            if time_match:
                hours, minutes, seconds = time_match.groups()
                current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                progress = min(100, (current_time / duration) * 100)
                
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                
                if progress > 0:
                    elapsed = current_time
                    total_estimated = (elapsed / progress) * 100
                    remaining = total_estimated - elapsed
                    remaining_str = self._format_time(remaining)
                else:
                    remaining_str = "計算中..."
                
                print(f'\r{phase}: [{bar}] {progress:5.1f}% | 残り時間: {remaining_str}', end='', flush=True)
        
        print()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)
    
    def _format_time(self, seconds: float) -> str:
        """秒を 'HH:MM:SS' 形式に変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _cleanup_ffmpeg_logs(self):
        """ffmpegの2パスエンコードで生成されるログファイルを削除"""
        log_files = ['ffmpeg2pass-0.log', 'ffmpeg2pass-0.log.mbtree']
        for log_file in log_files:
            try:
                if os.path.exists(log_file):
                    os.remove(log_file)
            except Exception:
                pass
    
    def run(self):
        """メイン処理"""
        self.logger.info("=" * 60)
        self.logger.info(f"動画圧縮ツール v{__version__} 起動 (Platform: {self.platform})")
        if self.dry_run:
            self.logger.info("モード: ドライラン")
        
        # フェーズ1: ファイル/ディレクトリパス入力
        self.input_files = self._phase1_get_input_files()
        
        # バッチモード判定
        self.batch_mode = len(self.input_files) > 1
        
        if self.batch_mode:
            self.logger.info(f"バッチモード: {len(self.input_files)}個のファイル")
            self._run_batch_mode()
        else:
            self.logger.info(f"単体モード: {self.input_files[0].name}")
            self._run_single_mode()
    
    def _run_single_mode(self):
        """単体ファイルモード"""
        input_path = self.input_files[0]
        video_info = self.get_video_info(input_path)
        
        # フェーズ2: 目標サイズ入力
        target_size_mb = self._phase2_get_target_size(input_path, video_info)
        
        # フェーズ2.5: 画質モード選択
        quality_mode = self._phase2_5_select_quality_mode()
        
        # フェーズ3: 拡張子変換
        output_format = self._phase3_convert_format(input_path)
        
        # フェーズ4 & 5: 圧縮実行 or ドライラン
        if self.dry_run:
            self._dry_run_report(input_path, target_size_mb, output_format, video_info, quality_mode)
        else:
            self._compress_and_report(input_path, target_size_mb, output_format, video_info, quality_mode)
    
    def _run_batch_mode(self):
        """バッチ処理モード"""
        print(f"\n📁 {len(self.input_files)}個の動画ファイルが見つかりました:")
        for i, file_path in enumerate(self.input_files, 1):
            size_mb = self.get_file_size_mb(file_path)
            print(f"  {i}. {file_path.name} ({size_mb:.2f} MB)")
        
        # 一括設定 or 個別設定
        print("\n設定方法を選択してください:")
        print("  1. 一括設定 (全てのファイルに同じ設定を適用)")
        print("  2. 個別設定 (ファイルごとに設定)")
        
        while True:
            choice = input("番号を選択: ").strip()
            if choice in ['1', '2']:
                break
            print("❌ エラー: 1 または 2 を入力してください。")
        
        if choice == '1':
            self._batch_mode_uniform()
        else:
            self._batch_mode_individual()
    
    def _batch_mode_uniform(self):
        """一括設定モード"""
        print("\n【一括設定モード】")
        print("全てのファイルに同じ設定を適用します。")
        
        # 目標サイズ(MB)
        while True:
            try:
                target_size_str = input("\n各ファイルを何MBまで圧縮しますか？: ").strip()
                target_size_mb = float(target_size_str)
                if target_size_mb <= 0:
                    print("❌ エラー: 0より大きい値を入力してください。")
                    continue
                break
            except ValueError:
                print("❌ エラー: 数字を入力してください。")
        
        # 画質モード選択
        quality_mode = self._phase2_5_select_quality_mode()
        
        # 拡張子変換
        print("\n全てのファイルの拡張子を変換しますか？")
        convert = input("(y/何も入力せずEnter): ").strip().lower()
        
        if convert == 'y':
            print("\n変換可能な形式:")
            for key, (ext, desc) in self.CONVERT_FORMATS.items():
                print(f"  {key}. {desc}")
            
            while True:
                format_choice = input("番号を選択: ").strip()
                if format_choice in self.CONVERT_FORMATS:
                    output_format = self.CONVERT_FORMATS[format_choice][0]
                    break
                print("❌ エラー: 正しい番号を入力してください。")
        else:
            output_format = None
        
        # 全ファイルを処理
        total = len(self.input_files)
        success_count = 0
        fail_count = 0
        
        for i, input_path in enumerate(self.input_files, 1):
            try:
                video_info = self.get_video_info(input_path)
                current_format = output_format if output_format else input_path.suffix[1:]
                
                if self.dry_run:
                    self._dry_run_report(input_path, target_size_mb, current_format, 
                                        video_info, quality_mode, current=i, total=total)
                    success_count += 1
                else:
                    self._compress_and_report(input_path, target_size_mb, current_format, 
                                            video_info, quality_mode, current=i, total=total)
                    success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"\n❌ エラー: {input_path.name} の処理に失敗: {e}")
                self.logger.error(f"処理失敗: {input_path.name}, エラー: {e}")
                if not self.dry_run:
                    continue_choice = input("続けますか？ (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        break
        
        if self.dry_run:
            print(f"\n✅ ドライラン完了! {total}個のファイルをシミュレートしました。")
            self.logger.info(f"ドライラン完了: 成功 {success_count}, 失敗 {fail_count}")
        else:
            print(f"\n🎉 バッチ処理完了! 成功: {success_count}, 失敗: {fail_count}")
            self.logger.info(f"バッチ処理完了: 成功 {success_count}, 失敗 {fail_count}")
    
    def _batch_mode_individual(self):
        """個別設定モード"""
        print("\n【個別設定モード】")
        
        total = len(self.input_files)
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        for i, input_path in enumerate(self.input_files, 1):
            try:
                print(f"\n{'='*60}")
                print(f"[{i}/{total}] {input_path.name}")
                print('='*60)
                
                video_info = self.get_video_info(input_path)
                
                # スキップオプション
                skip = input("このファイルをスキップしますか？ (y/n): ").strip().lower()
                if skip == 'y':
                    print("⏭️  スキップしました。")
                    skip_count += 1
                    self.logger.info(f"スキップ: {input_path.name}")
                    continue
                
                # 目標サイズ入力
                target_size_mb = self._phase2_get_target_size(input_path, video_info)
                
                # 画質モード選択
                quality_mode = self._phase2_5_select_quality_mode()
                
                # 拡張子変換
                output_format = self._phase3_convert_format(input_path)
                
                # 圧縮実行 or ドライラン
                if self.dry_run:
                    self._dry_run_report(input_path, target_size_mb, output_format, 
                                        video_info, quality_mode, current=i, total=total)
                    success_count += 1
                else:
                    self._compress_and_report(input_path, target_size_mb, output_format, 
                                            video_info, quality_mode, current=i, total=total)
                    success_count += 1
                
            except Exception as e:
                fail_count += 1
                print(f"\n❌ エラー: {input_path.name} の処理に失敗: {e}")
                self.logger.error(f"処理失敗: {input_path.name}, エラー: {e}")
                if not self.dry_run:
                    continue_choice = input("続けますか？ (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        break
        
        if self.dry_run:
            print(f"\n✅ ドライラン完了! 成功: {success_count}, スキップ: {skip_count}, 失敗: {fail_count}")
            self.logger.info(f"ドライラン完了: 成功 {success_count}, スキップ {skip_count}, 失敗 {fail_count}")
        else:
            print(f"\n🎉 バッチ処理完了! 成功: {success_count}, スキップ: {skip_count}, 失敗: {fail_count}")
            self.logger.info(f"バッチ処理完了: 成功 {success_count}, スキップ {skip_count}, 失敗 {fail_count}")
    
    def _dry_run_report(self, input_path: Path, target_size_mb: float, 
                       output_format: str, video_info: dict, quality_mode: str,
                       current: int = 1, total: int = 1):
        """ドライラン結果レポート"""
        current_size = self.get_file_size_mb(input_path)
        duration = float(video_info['format']['duration'])
        audio_bitrate = self.get_audio_bitrate_for_mode(quality_mode)
        
        try:
            video_bitrate = self.calculate_bitrate(target_size_mb, duration, audio_bitrate)
        except ValueError as e:
            print(f"\n❌ エラー: {e}")
            self.logger.warning(f"ドライラン: {input_path.name}, エラー: {e}")
            return
        
        quality_level = self.estimate_quality_level(video_bitrate, video_info)
        compression_ratio = (1 - target_size_mb / current_size) * 100
        
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        stem = input_path.stem
        output_name = f"{stem}--compressed--{target_size_mb:.1f}MB--{timestamp}.{output_format}"
        
        mode_info = QualityMode.MODES[quality_mode]
        
        if total > 1:
            print(f"\n📋 [{current}/{total}] ドライラン結果: {input_path.name}")
        else:
            print(f"\n📋 ドライラン結果")
        print("=" * 60)
        print(f"入力ファイル: {input_path.name}")
        print(f"現在のサイズ: {current_size:.2f} MB")
        print(f"目標サイズ: {target_size_mb:.2f} MB")
        print(f"圧縮率: {compression_ratio:.1f}%")
        print(f"動画の長さ: {self._format_time(duration)}")
        print()
        print("【画質モード】")
        print(f"  {mode_info['name']}: {mode_info['description']}")
        print()
        print("【エンコード設定】")
        print(f"  ビデオビットレート: {video_bitrate} kbps")
        print(f"  音声ビットレート: {audio_bitrate} kbps (AAC)")
        print(f"  コーデック: H.264 (libx264)")
        print()
        print("【予想画質】")
        print(f"  {quality_level}")
        print()
        print("【出力ファイル】")
        print(f"  ファイル名: {output_name}")
        print(f"  保存先: {input_path.parent / output_name}")
        print("=" * 60)
        
        # ログ記録
        self.logger.info(
            f"ドライラン: {input_path.name}, "
            f"モード: {mode_info['name']}, "
            f"現在サイズ: {current_size:.2f}MB, "
            f"目標サイズ: {target_size_mb:.2f}MB, "
            f"圧縮率: {compression_ratio:.1f}%, "
            f"ビデオビットレート: {video_bitrate}kbps, "
            f"音声ビットレート: {audio_bitrate}kbps, "
            f"予想画質: {quality_level}"
        )
        
        if total == 1:
            print("\n💡 実際に圧縮する場合は --dry-run オプションを外して実行してください。")
    
    def _compress_and_report(self, input_path: Path, target_size_mb: float, 
                            output_format: str, video_info: dict, quality_mode: str,
                            current: int = 1, total: int = 1):
        """圧縮実行と結果レポート"""
        import time
        
        current_size = self.get_file_size_mb(input_path)
        duration = float(video_info['format']['duration'])
        audio_bitrate = self.get_audio_bitrate_for_mode(quality_mode)
        
        # 処理開始時刻記録
        start_time = time.time()
        
        try:
            video_bitrate = self.calculate_bitrate(target_size_mb, duration, audio_bitrate)
            mode_info = QualityMode.MODES[quality_mode]
            
            if total == 1:
                print(f"\n📊 計算結果:")
                print(f"  画質モード: {mode_info['name']}")
                print(f"  動画ビットレート: {video_bitrate} kbps")
                print(f"  音声ビットレート: {audio_bitrate} kbps")
        except ValueError as e:
            self.logger.error(f"ビットレート計算失敗: {input_path.name}, エラー: {e}")
            raise RuntimeError(f"ビットレート計算エラー: {e}")
        
        # 出力ファイル名生成
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        stem = input_path.stem
        output_name = f"{stem}--compressed--{target_size_mb:.1f}MB--{timestamp}.{output_format}"
        output_path = input_path.parent / output_name
        
        # ログ: 処理開始
        self.logger.info(
            f"圧縮開始: {input_path.name}, "
            f"モード: {mode_info['name']}, "
            f"現在サイズ: {current_size:.2f}MB, "
            f"目標サイズ: {target_size_mb:.2f}MB, "
            f"ビデオビットレート: {video_bitrate}kbps, "
            f"音声ビットレート: {audio_bitrate}kbps"
        )
        
        # 圧縮実行
        try:
            self.compress_video(input_path, output_path, video_bitrate, video_info, audio_bitrate, current, total)
        except Exception as e:
            self.logger.error(f"圧縮失敗: {input_path.name}, エラー: {e}")
            raise
        
        # 処理時間計算
        elapsed_time = time.time() - start_time
        
        # 完了レポート
        final_size = self.get_file_size_mb(output_path)
        compression_ratio = (1 - final_size / current_size) * 100
        size_diff = abs(final_size - target_size_mb)
        
        print("\n" + "=" * 60)
        print("✅ 圧縮が完了し、圧縮した動画ファイルは保存されました!")
        print("=" * 60)
        print(f"画質モード: {mode_info['name']}")
        print(f"ファイル名: {output_name}")
        print(f"保存先: {output_path}")
        print(f"目標サイズ: {target_size_mb:.2f} MB")
        print(f"実際のサイズ: {final_size:.2f} MB")
        print(f"差分: {size_diff:.2f} MB")
        print(f"圧縮率: {compression_ratio:.1f}%")
        print(f"処理時間: {self._format_time(elapsed_time)}")
        print("=" * 60)
        
        # ログ: 処理完了
        self.logger.info(
            f"圧縮完了: {input_path.name} -> {output_name}, "
            f"モード: {mode_info['name']}, "
            f"現在サイズ: {current_size:.2f}MB, "
            f"目標サイズ: {target_size_mb:.2f}MB, "
            f"実際サイズ: {final_size:.2f}MB, "
            f"差分: {size_diff:.2f}MB, "
            f"圧縮率: {compression_ratio:.1f}%, "
            f"処理時間: {self._format_time(elapsed_time)}"
        )
    
    def _phase1_get_input_files(self) -> List[Path]:
        """フェーズ1: ファイル/ディレクトリパス取得"""
        print("\n【フェーズ1】")
        while True:
            path_str = input("動画ファイルまたはディレクトリのパスを入力し、エンターを押してください:\n> ").strip()
            path_str = path_str.strip("'\"")
            path = Path(path_str).expanduser()
            
            if not path.exists():
                print(f"❌ エラー: 存在しないパスです。正しいパスを入力してください。")
                continue
            
            # ディレクトリの場合
            if path.is_dir():
                video_files = self.get_video_files_from_directory(path)
                if not video_files:
                    print(f"❌ エラー: このディレクトリには動画ファイルが見つかりませんでした。")
                    print(f"サポート形式: {', '.join(self.SUPPORTED_FORMATS)}")
                    continue
                return video_files
            
            # ファイルの場合
            if not path.is_file():
                print(f"❌ エラー: ファイルまたはディレクトリを指定してください。")
                continue
            
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                print(f"❌ エラー: サポートされていない形式です。")
                print(f"サポート形式: {', '.join(self.SUPPORTED_FORMATS)}")
                continue
            
            return [path]
    
    def _phase2_get_target_size(self, input_path: Path, video_info: dict) -> float:
        """フェーズ2: 目標サイズ入力"""
        current_size = self.get_file_size_mb(input_path)
        duration = float(video_info['format']['duration'])
        
        print("\n【フェーズ2】")
        print(f"ファイル名: {input_path.name}")
        print(f"現在のファイル容量: {current_size:.2f} MB")
        print(f"動画の長さ: {self._format_time(duration)}")
        
        while True:
            try:
                target_str = input("\nこの動画を何MBまで圧縮しますか？数字を入力しエンターを押してください。(小数点可):\n> ").strip()
                target_size = float(target_str)
                
                if target_size <= 0:
                    print("❌ エラー: 0より大きい値を入力してください。")
                    continue
                
                if target_size >= current_size:
                    print(f"❌ エラー: 目標サイズ({target_size:.2f}MB)が現在のサイズ({current_size:.2f}MB)以上です。")
                    print("圧縮する意味ないで。もっと小さい値を入力してくれ。")
                    continue
                
                return target_size
                
            except ValueError:
                print("❌ エラー: 数字を入力してください。")
    
    def _phase2_5_select_quality_mode(self) -> str:
        """フェーズ2.5: 画質モード選択"""
        print("\n【フェーズ2.5】画質モード選択")
        print("どのモードで圧縮しますか？")
        print()
        print("  1. 音質優先 (音声192kbps)")
        print("     音楽、講演、ASMR などの音が重要なコンテンツ向け")
        print()
        print("  2. 画質優先 (音声128kbps)")
        print("     アニメ、映画、ゲーム実況 などの映像が重要なコンテンツ向け")
        print()
        print("  3. バランス (音声160kbps)")
        print("     一般的な動画向け。音質と画質のバランスが取れた設定")
        print()
        
        mode_map = {
            '1': QualityMode.AUDIO_PRIORITY,
            '2': QualityMode.VIDEO_PRIORITY,
            '3': QualityMode.BALANCED
        }
        
        while True:
            choice = input("番号を選択してください (デフォルト: 1): ").strip()
            
            # デフォルト値
            if not choice:
                choice = '1'
            
            if choice in mode_map:
                selected_mode = mode_map[choice]
                mode_info = QualityMode.MODES[selected_mode]
                print(f"\n✅ {mode_info['name']}モードを選択しました。")
                self.logger.info(f"画質モード選択: {mode_info['name']}")
                return selected_mode
            
            print("❌ エラー: 1, 2, 3 のいずれかを入力してください。")
    
    def _phase3_convert_format(self, input_path: Path) -> str:
        """フェーズ3: 拡張子変換"""
        print("\n【フェーズ3】")
        convert = input("拡張子は変換しますか？ (y/何も入力せずEnter): ").strip().lower()
        
        if convert == 'y':
            print("\n変換可能な形式:")
            for key, (ext, desc) in self.CONVERT_FORMATS.items():
                print(f"  {key}. {desc}")
            
            while True:
                choice = input("\n番号を選択してください: ").strip()
                if choice in self.CONVERT_FORMATS:
                    return self.CONVERT_FORMATS[choice][0]
                print("❌ エラー: 正しい番号を入力してください。")
        else:
            return input_path.suffix[1:]
    
    def reset(self):
        """次の圧縮のために変数をリセット"""
        self.input_files = []
        self.target_size_mb = None
        self.output_format = None
        self.quality_mode = None
        self.batch_mode = False
        self.start_time = None


def main():
    """エントリーポイント"""
    dry_run = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            print(f"動画圧縮ツール v{__version__}")
            print(f"Platform: {platform.system()}")
            sys.exit(0)
        elif sys.argv[1] in ['--dry-run', '-d']:
            dry_run = True
            print("🔍 ドライランモード: 実際の圧縮は行わず、計算結果のみ表示します。")
        elif sys.argv[1] in ['--help', '-h']:
            print("動画圧縮ツール - 使い方")
            print()
            print("使用法:")
            print("  python compress_video.py              通常モード")
            print("  python compress_video.py --dry-run    ドライランモード")
            print("  python compress_video.py --version    バージョン表示")
            print("  python compress_video.py --help       ヘルプ表示")
            print()
            print("オプション:")
            print("  --dry-run, -d    実際の圧縮を行わず、計算結果のみ表示")
            print("  --version, -v    バージョン情報を表示")
            print("  --help, -h       このヘルプを表示")
            print()
            print("画質モード:")
            print("  1. 音質優先 (音声192kbps) - 音楽、講演、ASMR向け")
            print("  2. 画質優先 (音声128kbps) - アニメ、映画、ゲーム実況向け")
            print("  3. バランス (音声160kbps) - 一般的な動画向け")
            print()
            print("ログファイル:")
            print(f"  処理履歴は {Path.home() / '.video-compressor' / 'history.log'} に保存されます")
            print()
            print(f"プラットフォーム: {platform.system()}")
            sys.exit(0)
    
    try:
        print("=" * 60)
        print("🎥 動画圧縮ツール - Windows/macOS/Linux対応版")
        print(f"Platform: {platform.system()}")
        print("=" * 60)
        
        compressor = VideoCompressor(dry_run=dry_run)
        
        if not compressor.check_ffmpeg():
            print("\n❌ エラー: ffmpegがインストールされてないわ")
            print(compressor.get_ffmpeg_install_instructions())
            compressor.logger.error(f"ffmpegが未インストール (Platform: {platform.system()})")
            sys.exit(1)
        
        while True:
            compressor.run()
            
            print("\n" + "=" * 60)
            if dry_run:
                continue_choice = input("もう1本シミュレートする？ (y/n): ").strip().lower()
            else:
                continue_choice = input("もう1本圧縮する？ (y/n): ").strip().lower()
            
            if continue_choice != 'y':
                print("\n👋 お疲れさん!またな!")
                print(f"処理履歴は {Path.home() / '.video-compressor' / 'history.log'} に保存されています。")
                compressor.logger.info("ツール終了")
                break
            
            compressor.reset()
            print("\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  処理が中断されました。")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌予期しないエラーが発生: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
