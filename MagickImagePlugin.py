from __future__ import annotations
import io
import os
import shutil
import subprocess
from typing import IO

from PIL import Image

"""
  Can be overwritten with custom path:

  import MagickImagePlugin
  MagickImagePlugin.MAGICK_BIN = "D:\\ImageMagick\\magick.exe"
  ...

"""
MAGICK_BIN = shutil.which('magick')

#"""
#    Can be overwritten with more or less (container) formats:
#
#    import MagickImagePlugin
#    MagickImagePlugin.MAGICK_FORMATS = (".pct", ".pict")
#  ...
#"""
MAGICK_FORMATS = (".exr", ".jng", ".heif", ".heic", ".mng", ".pcd", ".pct", ".pict", ".psb", ".psd", ".svg", ".wpg")

IS_WIN = os.name == 'nt'
if IS_WIN:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
    if ' ' in MAGICK_BIN:
        MAGICK_BIN = f'"{MAGICK_BIN}"'


########################################
#
########################################
def _open(fp: IO[bytes], filename: str | bytes, ** kwargs) -> Image.Image:
    if type(filename) == bytes:
        filename = filename.decode()
    ext = os.path.splitext(filename)[1]
    if ext.lower() not in MAGICK_FORMATS:
        raise SyntaxError("No Magick file")

    proc = subprocess.run(
        f"{MAGICK_BIN} \"{filename}\" bmp:-",
        startupinfo = startupinfo if IS_WIN else None,
        capture_output = True,
    )
    im = Image.open(io.BytesIO(proc.stdout), formats=("BMP",))
    im.filename = filename
    im.format = ext[1:].upper()
    return im

########################################
#
########################################
def _save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    if type(filename) == bytes:
        filename = filename.decode()

    fp.close()

    f = io.BytesIO()
    im.save(f, 'BMP')
    f.seek(0)

    subprocess.run(
        f"{MAGICK_BIN} bmp:- \"{filename}\"",
        input=f.read(),
        startupinfo = startupinfo if IS_WIN else None,
    )

# --------------------------------------------------------------------

Image.register_open("EXR", _open, lambda prefix: prefix.startswith(b"v/1"))
Image.register_save("EXR", _save)
Image.register_extensions("EXR", (".exr",))

Image.register_open("HEIF", _open, lambda prefix: prefix[4:12] == b"ftypheic")
Image.register_save("HEIF", _save)
Image.register_extensions("HEIF", (".heif", ".heic"))

Image.register_open("JNG", _open, lambda prefix: prefix.startswith(b"\x8bJNG"))
Image.register_save("JNG", _save)
Image.register_extensions("JNG", (".jng",))

Image.register_open("MNG", _open, lambda prefix: prefix.startswith(b"\x8aMNG"))
Image.register_save("MNG", _save)
Image.register_extensions("MNG", (".mng",))

Image.register_open("PSB", _open, lambda prefix: prefix.startswith(b"8BPS\x00\x02"))
Image.register_save("PSB", _save)
Image.register_extensions("PSB", (".psb",))

Image.register_open("SVG", _open, lambda prefix: prefix.startswith(b"<?xml"))
Image.register_save("SVG", _save)  # Saves as PNG embedded in SVG
Image.register_extensions("SVG", (".svg",))

# Read-only
Image.register_open("WPG", _open, lambda prefix: prefix.startswith(b"\xffWPC"))
Image.register_extensions("WPG", (".wpg",))

# PCD read support is implemented by a standard Pillow plugin
Image.register_save("PCD", _save)

Image.register_open("PICT", _open)
Image.register_save("PICT", _save)
Image.register_extensions("PICT", (".pict", ".pct"))

# PSD read support is implemented by a standard Pillow plugin
Image.register_save("PSD", _save)

if __name__ == "__main__":
    try:
        import WinImageShowPlugin
    except:
        pass

    im = Image.open("_test_files/test.exr")
#    im.save("_test_files/_new.exr")
    im.show()

#    im = Image.open("_test_files/test.heif")
#    im.save("_test_files/_new.heif")

#    im = Image.open("_test_files/test.jng")
#    im.save("_test_files/_new.jng")

#    im = Image.open("_test_files/test.mng")
#    im.save("_test_files/_new.mng")

#    im = Image.open("_test_files/test.pct")
#    im.save("_test_files/_new.pct")

#    im = Image.open("_test_files/test.psb")
#    im.save("_test_files/_new.psb")

#    im = Image.open("_test_files/test.svg")
#    im.save("_test_files/_new.svg")

#    im = Image.open("_test_files/test.wpg")
#    im.save("_test_files/_new.wpg")  # Saves weird

#    im = Image.open("_test_files/test.pcd")
#    im.save("_test_files/_new.pcd")

#    im = Image.open("_test_files/test.psb")
#    im.save("_test_files/_new.psd")

#    im = Image.open("_test_files/test.psd")
#    im.save("_test_files/_new.psd")
