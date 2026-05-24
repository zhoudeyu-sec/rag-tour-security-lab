import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "images"
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "run2").mkdir(exist_ok=True)

SRC1 = Path(r"C:\Users\Le'novo\Desktop\ai安全截图")
SRC2 = Path(r"C:\Users\Le'novo\Desktop\ai安全截图（2）")

for p in SRC1.glob("*.png"):
    shutil.copy2(p, ROOT / p.name)

mapping = {
    "image1(2).png": "run2-01.png",
    "image2(2).png": "run2-02.png",
    "image3(2).png": "run2-03.png",
    "image4(2).png": "run2-04.png",
}
for src_name, dst_name in mapping.items():
    shutil.copy2(SRC2 / src_name, ROOT / "run2" / dst_name)

print("copied:", len(list(ROOT.rglob("*.png"))), "files")
