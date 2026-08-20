from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
MEDIA_DIR = ASSETS_DIR / "media"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
THUMBNAIL_DIR.mkdir(exist_ok=True)
INFO_JSON_PATH = ASSETS_DIR / "info.json"
PHOTO_CACHE = DATA_DIR / "info_photo_cache.json"
VIDEO_CACHE = DATA_DIR / "info_video_cache.json"
DATABASE_PATH = DATA_DIR / "app.db"
