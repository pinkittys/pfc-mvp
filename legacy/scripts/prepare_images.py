import os, csv, re, unicodedata
from pathlib import Path
from PIL import Image
from dotenv import load_dotenv

# ----- 설정 -----
# ✅ 프로젝트 루트를 현재 파일이 있는 폴더로 지정 (parents[1] 아님!)
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data/images_raw"
OUT = ROOT / "data/images_webp"
MANIFEST = ROOT / "data/images_manifest.csv"

load_dotenv(ROOT / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # 버킷 public 가정
BUCKET = os.getenv("SUPABASE_BUCKET", "flowers")
PUBLIC_BASE = os.getenv("PUBLIC_BASE")

# (선택) supabase 업로드
try:
    from supabase import create_client, Client  # type: ignore
    sb: "Client|None" = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    sb = None

COLOR_MAP = {
    "화이트":"white","하양":"white","흰색":"white",
    "핑크":"pink","분홍":"pink",
    "레드":"red","빨강":"red",
    "옐로우":"yellow","노랑":"yellow","노란색":"yellow",
    "라벤더":"lavender",
    "퍼플":"purple","보라":"purple",
    "블루":"blue","파랑":"blue",
    "그린":"green","초록":"green",
}

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s.strip().lower())
    return s

def parse_name(fname: str):
    stem = Path(fname).stem
    while any(stem.lower().endswith(ext) for ext in (".jpg",".jpeg",".png",".webp",".gif")):
        stem = Path(stem).stem
    parts = re.split(r"[_\-]", stem, maxsplit=1)
    if len(parts) == 2:
        eng, color_ko = parts
    else:
        eng, color_ko = parts[0], "white"
    color_en = COLOR_MAP.get(color_ko.strip(), color_ko.strip().lower())
    return slugify(eng), color_en

def ensure_out():
    OUT.mkdir(parents=True, exist_ok=True)

def convert_to_webp(src: Path, dst: Path, size=(960,1200), quality=90):
    im = Image.open(src)
    if im.mode in ("RGBA","P"):
        im = im.convert("RGBA")
    else:
        im = im.convert("RGB")
    im = im.resize(size, Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "WEBP", quality=quality, method=6)

def upload_to_supabase(local_path: Path, key: str) -> str:
    if sb is None:
        print("⚠️  supabase client 미초기화: 업로드 생략")
        return ""
    try:
        with open(local_path, "rb") as f:
            sb.storage.from_(BUCKET).upload(key, f, {"upsert": "true"})
        return f"{PUBLIC_BASE}/{BUCKET}/{key}"
    except Exception as e:
        print(f"⚠️  업로드 실패 ({key}): {e}")
        return ""

def main(do_upload=True):
    ensure_out()
    if not RAW.exists():
        print(f"❌ 원본 폴더 없음: {RAW}")
        return

    rows = []
    files = [p for p in sorted(RAW.iterdir()) if p.suffix.lower() in [".jpg",".jpeg",".png",".webp",".gif",".jpg",".png",".jpeg",".webp"]]
    print(f"📦 대상 파일: {len(files)}개")

    for file in files:
        eng_slug, color_en = parse_name(file.name)
        rel_key = f"{eng_slug}/{color_en}.webp"
        out_path = OUT / eng_slug / f"{color_en}.webp"

        convert_to_webp(file, out_path, size=(960,1200), quality=90)
        print(f"✅ 변환: {file.name} -> {out_path.relative_to(ROOT)}")

        url = upload_to_supabase(out_path, rel_key) if do_upload else ""
        if url:
            print(f"   ↳ 업로드 OK: {url}")

        rows.append({
            "source_file": file.name,
            "eng_slug": eng_slug,
            "color": color_en,
            "storage_key": rel_key,
            "public_url": url or (f"{PUBLIC_BASE}/{BUCKET}/{rel_key}" if PUBLIC_BASE else ""),
        })

    if rows:
        with open(MANIFEST, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"📝 manifest 저장: {MANIFEST.relative_to(ROOT)}")
    print(f"🎉 완료: {len(rows)} files")

if __name__ == "__main__":
    main(do_upload=True)

