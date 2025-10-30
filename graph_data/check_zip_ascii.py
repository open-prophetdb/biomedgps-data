import zipfile
import pandas as pd
from io import BytesIO, StringIO
from pathlib import Path

# === 要检查的目录 ===
zip_dir = Path("/Users/zhuzhixing/KG/biomedgps-data/datasets/biomedgps-v20250831-8cdd6f")

for zip_path in sorted(zip_dir.glob("*.zip")):
    print(f"\n📦 检查 {zip_path.name} ...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                if not member.lower().endswith(".tsv"):
                    continue
                print(f"  ▶ 文件 {member}")
                data = zf.read(member)
                try:
                    # 尝试 ASCII 严格解码
                    text = data.decode("ascii")
                    # 测试用 pandas 解析前几行
                    df = pd.read_csv(StringIO(text), sep="\t", nrows=5)
                    print("    ✅ ASCII-only (可以成功读取)")
                except UnicodeDecodeError as e:
                    print(f"    ❌ 含非 ASCII 字符: {e}")
    except Exception as e:
        print(f"  ⚠️ 无法读取 {zip_path.name}: {e}")

