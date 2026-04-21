#!/usr/bin/env python3
"""
デスクトップ整理スクリプト

ファイルをカテゴリ別フォルダに整理します。
重要ファイルは移動前に日本語で確認を取ります。
"""

import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 整理先フォルダとその対象拡張子
FOLDER_RULES = [
    ("画像・スクショ", {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}),
    ("動画", {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"}),
    ("書類", {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt"}),
    ("ショートカット", {".lnk"}),
]

# 確認が必要な拡張子
CONFIRM_EXTENSIONS = {".xlsx", ".xls", ".csv", ".pdf", ".docx", ".zip", ".exe", ".msi"}

# 確認が必要なキーワード（ファイル名に含まれる場合）
CONFIRM_KEYWORDS = ["重要", "契約", "請求", "決算", "税"]

# 最近更新されたファイルのしきい値（日数）
RECENT_DAYS = 30


def get_target_folder(extension: str) -> str:
    """拡張子からコピー先フォルダ名を返す。どれにも該当しない場合は「その他」。"""
    ext = extension.lower()
    for folder_name, extensions in FOLDER_RULES:
        if ext in extensions:
            return folder_name
    return "その他"


def needs_confirmation(file_path: Path) -> tuple[bool, list[str]]:
    """
    このファイルを移動する前にユーザー確認が必要かどうかを判定する。
    戻り値: (確認が必要か, 理由リスト)
    """
    reasons = []
    ext = file_path.suffix.lower()

    if ext in CONFIRM_EXTENSIONS:
        reasons.append(f"拡張子 {ext} は要確認対象です")

    for keyword in CONFIRM_KEYWORDS:
        if keyword in file_path.name:
            reasons.append(f"ファイル名に「{keyword}」が含まれています")
            break

    try:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        if datetime.now() - mtime < timedelta(days=RECENT_DAYS):
            days_ago = (datetime.now() - mtime).days
            reasons.append(f"{days_ago}日前に更新されたファイルです（30日以内）")
    except OSError:
        pass

    return bool(reasons), reasons


def ask_confirmation(file_path: Path, reasons: list[str]) -> bool:
    """日本語でユーザーに確認を求める。'y' または 'yes' で移動を許可。"""
    print()
    print(f"  ⚠️  要確認ファイル: {file_path.name}")
    for reason in reasons:
        print(f"     - {reason}")
    answer = input("  このファイルを移動してもよろしいですか？ (y/n): ").strip().lower()
    return answer in ("y", "yes")


def organize(target_dir: Path, dry_run: bool = False) -> None:
    """
    target_dir 内のファイルをカテゴリ別フォルダに整理する。

    dry_run=True の場合は実際の移動を行わず、実行予定内容のみ表示する。
    """
    if not target_dir.exists():
        print(f"エラー: フォルダが見つかりません: {target_dir}")
        sys.exit(1)

    files = [f for f in target_dir.iterdir() if f.is_file()]

    if not files:
        print("整理対象のファイルが見つかりませんでした。")
        return

    print(f"\n対象フォルダ: {target_dir}")
    print(f"ファイル数: {len(files)} 件")
    if dry_run:
        print("（ドライランモード: ファイルの移動は行いません）")
    print()

    moved = 0
    skipped = 0
    errors = 0

    for file_path in sorted(files):
        dest_folder_name = get_target_folder(file_path.suffix)
        dest_dir = target_dir / dest_folder_name

        confirm_needed, reasons = needs_confirmation(file_path)

        if confirm_needed:
            if dry_run:
                print(f"  [要確認] {file_path.name} → {dest_folder_name}/")
                for reason in reasons:
                    print(f"           - {reason}")
                continue

            allowed = ask_confirmation(file_path, reasons)
            if not allowed:
                print(f"  ⏭️  スキップしました: {file_path.name}")
                skipped += 1
                continue
        else:
            print(f"  {file_path.name} → {dest_folder_name}/")

        if dry_run:
            continue

        try:
            dest_dir.mkdir(exist_ok=True)
            dest_path = dest_dir / file_path.name

            # 同名ファイルが既に存在する場合はリネームして保存
            if dest_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_path = dest_dir / f"{stem}_{timestamp}{suffix}"

            shutil.move(str(file_path), str(dest_path))
            moved += 1
        except Exception as e:
            print(f"  ❌ 移動エラー: {file_path.name} ({e})")
            errors += 1

    print()
    if not dry_run:
        print(f"完了: {moved} 件移動 / {skipped} 件スキップ / {errors} 件エラー")
    else:
        print("（ドライランモード終了）")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="デスクトップのファイルをカテゴリ別フォルダに整理します。"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path.home() / "Desktop"),
        help="整理するフォルダのパス（省略時: ~/Desktop）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際の移動を行わず、実行予定内容のみ表示します",
    )
    args = parser.parse_args()

    target_dir = Path(args.directory).expanduser().resolve()
    organize(target_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
