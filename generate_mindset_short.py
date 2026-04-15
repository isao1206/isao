#!/usr/bin/env python3
"""
mindset_short.mp4 ジェネレーター
YouTube Shorts / TikTok 向け 30秒自己啓発動画

使い方:
    python3 generate_mindset_short.py

必要ライブラリ:
    pip install moviepy pillow numpy
"""

import sys
import os
import numpy as np

# ─────────────────────────────────────────────
#  依存チェック
# ─────────────────────────────────────────────
try:
    from moviepy import VideoClip, AudioArrayClip, concatenate_videoclips
except ImportError:
    print("[ERROR] moviepy が見つかりません: pip install moviepy")
    sys.exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[ERROR] Pillow が見つかりません: pip install Pillow")
    sys.exit(1)

# ─────────────────────────────────────────────
#  設定
# ─────────────────────────────────────────────
WIDTH      = 1080
HEIGHT     = 1920
FPS        = 30
OUTPUT     = "mindset_short.mp4"

# 強調ワード → 黄色
HIGHLIGHT_YELLOW = ["凡人", "差", "才能", "選択", "行動", "成功"]
# 強調ワード → 赤
HIGHLIGHT_RED    = ["搾取", "逆", "凡人"]

# 台本（テキスト, 表示秒数）
SCRIPT = [
    ("ほとんどの人間は",         1.2),
    ("凡人で終わる",             1.5),
    ("でも理由はシンプル",       1.2),
    ("正しい方向を\n知らないだけ", 1.5),
    ("最初は差なんてない",       1.3),
    ("でも５年後",               1.0),
    ("取り返せない\n差になる",   1.5),
    ("年収300万と\n3000万",      1.5),
    ("違いは才能じゃない",       1.3),
    ("選択と行動だけ",           1.3),
    ("群れに従う人は\n一生そのまま", 1.4),
    ("逆を選べ",                 1.0),
    ("集中できない人は",         1.3),
    ("一生搾取される",           1.5),
    ("成功者は\n仕組みを作る",   1.5),
    ("そして最後",               1.0),
    ("動いた人だけが\n人生を変える", 1.8),
]

# ─────────────────────────────────────────────
#  フォント検索（日本語対応）
# ─────────────────────────────────────────────
FONT_CANDIDATES = [
    # Linux (IPA)
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    # Linux (Noto CJK)
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    # macOS
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    # Windows
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]

def find_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            print(f"  [フォント] {path}")
            return path
    print("  [警告] 日本語フォントが見つかりません。デフォルトフォントを使用します")
    return None

# ─────────────────────────────────────────────
#  背景グラデーション
# ─────────────────────────────────────────────
def make_background():
    """ダーク系グラデーション背景を PIL Image で生成"""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(8  + 12 * ratio)
        g = int(5  +  8 * ratio)
        b = int(18 + 22 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img

BG_IMAGE = make_background()  # 使い回す

# ─────────────────────────────────────────────
#  テキスト描画
# ─────────────────────────────────────────────
def get_text_color(text: str):
    """テキストの強調色を返す"""
    for word in HIGHLIGHT_RED:
        if word in text:
            return (255, 60, 60)      # 赤
    for word in HIGHLIGHT_YELLOW:
        if word in text:
            return (255, 225, 0)      # 黄
    return (255, 255, 255)            # 白（通常）

def draw_text_centered(draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                       color, outline_size=5):
    """複数行テキストを中央に描画（黒縁付き）"""
    lines = text.split("\n")
    line_h   = int(font.size * 1.35)
    total_h  = len(lines) * line_h
    start_y  = (HEIGHT - total_h) // 2

    for i, line in enumerate(lines):
        y = start_y + i * line_h
        # テキスト幅取得
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w    = bbox[2] - bbox[0]
        except AttributeError:
            w, _ = draw.textsize(line, font=font)
        x = (WIDTH - w) // 2

        # 黒アウトライン
        for dx in range(-outline_size, outline_size + 1):
            for dy in range(-outline_size, outline_size + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
        # メインテキスト
        draw.text((x, y), line, font=font, fill=color)

# ─────────────────────────────────────────────
#  ズームエフェクト（軽いカットイン）
# ─────────────────────────────────────────────
def apply_zoom(img: Image.Image, scale: float) -> np.ndarray:
    """中心を基準に scale 倍ズーム（0.98〜1.04 程度を想定）"""
    if abs(scale - 1.0) < 0.001:
        return np.array(img)
    new_w = int(WIDTH  * scale)
    new_h = int(HEIGHT * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - WIDTH)  // 2
    top  = (new_h - HEIGHT) // 2
    cropped = resized.crop((left, top, left + WIDTH, top + HEIGHT))
    return np.array(cropped)

# ─────────────────────────────────────────────
#  クリップ生成
# ─────────────────────────────────────────────
def make_clip(text: str, duration: float, font) -> VideoClip:
    """テキスト1枚のクリップを生成（ズームアニメ付き）"""
    color = get_text_color(text)

    def make_frame(t: float) -> np.ndarray:
        # ズーム: クリップ冒頭で 1.03 → 1.00 に収束（カットイン感）
        progress = t / duration
        scale    = 1.03 - 0.03 * min(progress * 3, 1.0)

        img  = BG_IMAGE.copy()
        draw = ImageDraw.Draw(img)
        draw_text_centered(draw, text, font, color)

        return apply_zoom(img, scale)

    clip = VideoClip(make_frame, duration=duration)
    return clip.with_fps(FPS)

# ─────────────────────────────────────────────
#  BGM 生成（テンション系ドローン＋ビート）
# ─────────────────────────────────────────────
def make_bgm(duration: float, sr: int = 44100) -> np.ndarray:
    """NumPy でテンション系BGMを合成する"""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # ─ ドローン（低音持続）
    drone  = 0.25 * np.sin(2 * np.pi * 55 * t)            # A1
    drone += 0.12 * np.sin(2 * np.pi * 82.5 * t)          # E2
    drone += 0.08 * np.sin(2 * np.pi * 110 * t)           # A2
    # 軽いビブラート
    mod    = 1.0 + 0.003 * np.sin(2 * np.pi * 4 * t)
    drone *= mod

    # ─ キック（0.5秒ごと）
    beat_env = np.maximum(np.sin(2 * np.pi * 2.0 * t), 0) ** 8
    kick      = 0.5 * beat_env * np.sin(2 * np.pi * 60 * t * np.exp(-t % 0.5 * 8))

    # ─ ハイハット
    rng       = np.random.default_rng(42)
    noise     = rng.standard_normal(len(t))
    hat_env   = np.maximum(np.sin(2 * np.pi * 4.0 * t + np.pi / 2), 0) ** 10
    hihat     = 0.06 * hat_env * noise

    # ─ 合成 & フェード
    audio = drone + kick + hihat
    fade  = int(0.5 * sr)
    audio[:fade]  *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)

    # 正規化
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.75

    return np.column_stack([audio, audio]).astype(np.float32)  # ステレオ

# ─────────────────────────────────────────────
#  メイン
# ─────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  mindset_short.mp4 ジェネレーター")
    print("=" * 50)
    print(f"  解像度 : {WIDTH}x{HEIGHT}  FPS:{FPS}")
    print(f"  クリップ数: {len(SCRIPT)}")
    total_sec = sum(d for _, d in SCRIPT)
    print(f"  合計時間: {total_sec:.1f} 秒")
    print()

    # フォント読み込み
    font_path = find_font()
    font_size = 88
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"  [警告] フォント読み込み失敗: {e}")
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    # クリップ生成
    print("クリップ生成中...")
    clips = []
    for i, (text, dur) in enumerate(SCRIPT):
        label = text.replace("\n", " ")
        print(f"  [{i+1:02d}/{len(SCRIPT)}] {label:<30s} {dur:.1f}s")
        clips.append(make_clip(text, dur, font))

    # 連結
    print("\nクリップを連結中...")
    video = concatenate_videoclips(clips, method="compose")

    # BGM
    print("BGM を生成中...")
    bgm_arr  = make_bgm(video.duration)
    bgm      = AudioArrayClip(bgm_arr, fps=44100)
    video    = video.with_audio(bgm)

    # 書き出し
    print(f"\n動画を書き出し中 → {OUTPUT}")
    print("（数分かかる場合があります）\n")
    video.write_videofile(
        OUTPUT,
        fps        = FPS,
        codec      = "libx264",
        audio_codec= "aac",
        bitrate    = "4000k",
        preset     = "medium",
        logger     = "bar",
    )

    size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f"\n完成！ ファイル: {OUTPUT}  ({size_mb:.1f} MB)")
    print("YouTube Shorts / TikTok にそのままアップロードできます。")

if __name__ == "__main__":
    main()
