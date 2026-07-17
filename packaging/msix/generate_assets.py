"""
packaging/msix/generate_assets.py
──────────────────────────────────
Genera los assets de imagen que exige el manifest MSIX
(Square44x44Logo, Square150x150Logo, Wide310x150Logo, StoreLogo,
SplashScreen) a partir de wifi_monitor.png (256x256).

Se ejecuta dentro del job de CI, después de build_windows_prep.py
y antes de empaquetar con makeappx.
"""

import sys
from pathlib import Path
from PIL import Image

# ── Fix encoding para Windows (cp1252 no soporta emojis/cajas Unicode) ──
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SRC = Path("wifi_monitor.png")
OUT = Path("packaging/msix/Assets")
BG = (13, 33, 55, 255)  # mismo azul oscuro del ícono placeholder

SQUARE_SIZES = {
    "Square44x44Logo.png": 44,
    "Square150x150Logo.png": 150,
    "StoreLogo.png": 50,
}

src: Image.Image


def square(size: int) -> Image.Image:
    return src.resize((size, size), Image.LANCZOS)


def letterbox(w: int, h: int) -> Image.Image:
    """Centra el ícono cuadrado sobre un lienzo rectangular con fondo sólido."""
    canvas = Image.new("RGBA", (w, h), BG)
    scale = min(w, h) / max(src.size)
    new_w, new_h = int(src.size[0] * scale), int(src.size[1] * scale)
    resized = src.resize((new_w, new_h), Image.LANCZOS)
    canvas.paste(resized, ((w - new_w) // 2, (h - new_h) // 2), resized)
    return canvas


def main():
    global src
    if not SRC.exists():
        raise SystemExit(f"ERROR: No se encontró {SRC}. Este script corre desde la raíz del repo.")

    OUT.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")

    for name, size in SQUARE_SIZES.items():
        square(size).save(OUT / name)
        print(f"  OK {name} ({size}x{size})")

    letterbox(310, 150).save(OUT / "Wide310x150Logo.png")
    print("  OK Wide310x150Logo.png (310x150)")

    letterbox(620, 300).save(OUT / "SplashScreen.png")
    print("  OK SplashScreen.png (620x300)")

    print(f"\nAssets generados en {OUT}/")


if __name__ == "__main__":
    main()
