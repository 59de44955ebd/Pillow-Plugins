from __future__ import annotations
import os
import shutil
import subprocess
from typing import IO

from PIL import Image

IS_WIN = os.name == "nt"

"""
  Can be overwritten with custom path:

  import BpgImagePlugin
  BpgImagePlugin.BGPDEC_BIN = "/foo/bpgdec"
  BpgImagePlugin.BGPENC_BIN = "/foo/bpgenc
  ...

"""
BGPDEC_BIN = os.path.join(os.path.dirname(__file__), "bin", "bpgdec.exe") if IS_WIN else shutil.which("bpgdec")
BGPENC_BIN = os.path.join(os.path.dirname(__file__), "bin", "bpgenc.exe") if IS_WIN else shutil.which("bpgenc")

TMP_DIR = os.environ["TMP"] if IS_WIN else "/tmp"

if IS_WIN:
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startupinfo = None

def _open(fp: IO[bytes], filename: str | bytes, ** kwargs) -> Image.Image:
    if type(filename) == bytes:
        filename = filename.decode()
    tmp_png = os.path.join(TMP_DIR, "~bpp.png")
    proc = subprocess.run(
        [BGPDEC_BIN, "-b", "16", "-o", tmp_png, filename],
        capture_output=True,
        startupinfo=startupinfo
    )
    im = Image.open(tmp_png).copy()
    os.unlink(tmp_png)
    im.filename = filename
    im.format = "BPG"
    return im

def _save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    if type(filename) == bytes:
        filename = filename.decode()

    # -q qp       set quantizer parameter (smaller gives better quality, range: 0-51, default = 29)
    quantizer = im.encoderinfo.get("quantizer", 29)
    command = [BGPENC_BIN, "-b", "12", "-q", str(quantizer)]

    # -lossless   enable lossless mode
    lossless = im.encoderinfo.get("lossless", False)
    if lossless:
        command.append("-lossless")

    tmp_png = os.path.join(TMP_DIR, "~bpp.png")
    command += ["-o", filename, tmp_png]

    im.save(tmp_png)
    subprocess.run(
        command,
        startupinfo = startupinfo
    )
    os.unlink(tmp_png)

# --------------------------------------------------------------------

Image.register_open("BPG", _open, lambda prefix: prefix.startswith(b"BPG"))
Image.register_save("BPG", _save)
Image.register_extension("BPG", ".bpg")

if __name__ == "__main__":
    try:
        import WinImageShowPlugin
    except:
        pass
    im = Image.open(b"../_test_files/test.bpg")
#    im.save("new.bpg", quantizer=0) #, lossless=True)
    im.show()
