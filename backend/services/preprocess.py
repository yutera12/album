import subprocess
import json
import shutil
import cv2
from tqdm import tqdm
from pathlib import Path
from pydantic import validate_call
from typing import Literal
import uuid

from models.api_model import AppState, Media, BirthInfo, TagCategory, YearMonth
from utils.json_store_utils import JsonStore
from utils.date_utils import extract_date_from_filename
from utils.image_utils import scale
from utils.time_utils import min_sec_to_sec
from utils.date_utils import create_year_month_map
from utils.file_utils import select_files


ROOT = Path(__file__).parent.parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
MEDIA_DIR = ASSETS_DIR / "media"
THUMBNAIL_DIR = DATA_DIR / "thumbnails"
INFO_JSON = ASSETS_DIR / "info.json"
PHOTO_CACHE = DATA_DIR / "info_photo_cache.json"
VIDEO_CACHE = DATA_DIR / "info_video_cache.json"
SAVE_INTERVAL = 10
TEMP_THUMBNAIL_NAME = "__thumbnail_tmp.jpg"

def _preprocess_photo(files: list[str]) -> dict[str, dict[str, float | str]]:
    """
    画像ファイルを前処理する。

    各画像について以下を実施する。

    - サムネイルを必要に応じて生成する。
    - アスペクト比とID情報をキャッシュする。
    - 取得済みの情報はキャッシュから再利用する。

    サムネイルを必要に応じて生成し、
    キャッシュされた情報を含む画像情報を返す。

    Args:
        files: 前処理対象の画像ファイル名一覧。

    Returns:
        ファイル名をキーとした辞書。

        {
            filename: {
                "id": str,
                "aspect_ratio": float,
                "thumbnail_file_name": str,
            }
        }

    Side Effects:
        - ``assets/thumbnails`` にサムネイル画像を生成する。
        - ``info_photo_cache.json`` を更新する。
    """

    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    cache = JsonStore(PHOTO_CACHE)

    media_info = {}
    updated = 0
    for filename in tqdm(files, desc="photo"):
        thumbnail_path = THUMBNAIL_DIR / filename

        # サムネイルファイル未作成の場合は作成
        if not thumbnail_path.exists():
            img = cv2.imread(str(MEDIA_DIR / filename))
            img = scale(img, 400)
            temp_path = THUMBNAIL_DIR / "temp.png"
            cv2.imwrite(str(temp_path), img)
            shutil.move(temp_path, thumbnail_path)

        # アスペクト比未導出の場合導出
        if filename not in cache:
            im = cv2.imread(str(MEDIA_DIR / filename))
            cache[filename] = {
                "id": str(uuid.uuid4()),
                "aspect_ratio": im.shape[1] / im.shape[0],
            }
            updated += 1
            if updated >= SAVE_INTERVAL:
                cache.save()
                updated = 0

        media_info[filename] = {
            "id": cache[filename]["id"],
            "aspect_ratio": cache[filename]["aspect_ratio"],
            "thumbnail_file_name": filename
        }

    if updated:
        cache.save()
    return media_info


def _preprocess_video(files: list[str], thumbnail_time: dict[str, tuple[int, float]]) -> dict[str, dict[str, float | str]]:
    """
    動画ファイルを前処理する。

    各動画について以下を実施する。

    - 指定時刻のサムネイルを生成する。
    - ffprobe を利用して動画長および解像度情報を取得する。
    - アスペクト比を取得する。
    - 取得済みの情報はキャッシュから再利用する。

    Args:
        files: 前処理対象の動画ファイル名一覧。
        thumbnail_time:
            ファイル名をキーとしたサムネイル生成時刻
            （分, 秒）のタプル。

    Returns:
        ファイル名をキーとした辞書。

        {
            filename: {
                "total_time": float,
                "aspect_ratio": float,
                "thumbnail_file_name": str,
            }
        }

    Raises:
        RuntimeError:
            サムネイル生成時に動画フレームを取得できなかった場合。
        subprocess.CalledProcessError:
            ``ffprobe`` の実行に失敗した場合。

    Side Effects:
        - ``assets/thumbnails`` にサムネイル画像を生成する。
        - ``info_video_cache.json`` を更新する。
    """

    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    cache = JsonStore(VIDEO_CACHE)
    updated = 0
    media_info = {}
    for filename in tqdm(files, desc="movie"):

        stem = Path(filename).stem
        capture_time = min_sec_to_sec(thumbnail_time[filename])
        thumbnail_path = THUMBNAIL_DIR / f"{stem}__{capture_time}.png"

        # サムネイルファイル未作成の場合は作成
        if not thumbnail_path.exists():
            video = cv2.VideoCapture(str(MEDIA_DIR / filename))
            video.set(cv2.CAP_PROP_POS_MSEC, capture_time * 1000)

            ret, img = video.read()
            video.release()
            if not ret:
                raise RuntimeError(f"Failed to read thumbnail: {filename}")
            
            img = scale(img, 400)

            # OpenCV が日本語パスを扱えないため、一時ファイルへ出力してからリネームする
            temp_path = thumbnail_path.parent / TEMP_THUMBNAIL_NAME

            if not cv2.imwrite(str(temp_path), img):
                raise RuntimeError(f"Failed to write thumbnail: {temp_path}")

            shutil.move(temp_path, thumbnail_path)


        # アスペクト比、動画時間が未導出の場合導出
        if filename not in cache:

            cmd = [
                "ffprobe",
                "-v", "error",
                "-print_format", "json",
                "-show_entries", "format=duration:stream=width,height",
                str(MEDIA_DIR / filename),
            ]

            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            metadata = json.loads(r.stdout)

            total_time = float(metadata["format"]["duration"])

            video_stream = next(
                s for s in metadata["streams"]
                if "width" in s and "height" in s
            )

            aspect_ratio = video_stream["width"] / video_stream["height"]

            cache[filename] = {
                "id": str(uuid.uuid4()),
                "total_time": total_time,
                "aspect_ratio": aspect_ratio,
            }

            updated += 1
            if updated >= SAVE_INTERVAL:
                cache.save()
                updated = 0


        media_info[filename] = {
            "id": cache[filename]["id"],
            "total_time": cache[filename]["total_time"], 
            "aspect_ratio": cache[filename]["aspect_ratio"],
            "thumbnail_file_name": str(thumbnail_path.relative_to(THUMBNAIL_DIR))
        }

    if updated:
        cache.save()

    return media_info


def _build_media(
    id: str, media_type: Literal["video", "photo"], total_time: float | None,
    file_name: str, thumbnail_file_name: str, aspect_ratio: float, tag_list: list[str], favorite: bool
) -> Media:
    """
    写真・動画共通のメディア情報を生成する。

    ファイル名から日付情報を抽出し、
    ``Media`` を構築して返す。

    Args:
        id:
            メディアID。
        media_type:
            メディア種別（video または photo）。
        total_time:
            動画の場合の再生時間。写真の場合は None。
        file_name:
            メディアファイル名。
        thumbnail_file_name:
            サムネイルファイル名。
        aspect_ratio:
            メディアのアスペクト比。
        tag_list:
            メディアに紐付くタグ一覧。
        favorite:
            お気に入り状態。
    Returns:
        構築済みの ``Media``。
    """
    year, month, day, _ = extract_date_from_filename(file_name)

    return Media(
        id=id,
        type=media_type,
        year=year,
        month=month,
        day=day,
        file_name=file_name,
        thumbnail_file_name=thumbnail_file_name,
        aspect_ratio=aspect_ratio,
        tag=tag_list,
        favorite=favorite,
        total_time=total_time,
        title=None
    )


def _validate_files(actual_files: list[str], info_files: dict, media_type: Literal["video", "photo"]):
    """
    画像・動画ファイルと ``info.json`` の整合性を検証する。

    実際に存在するファイルと ``info.json`` に記載された
    ファイル一覧が完全一致していることを確認する。

    Args:
        actual_files: 実際に存在するファイル名一覧。
        info_files: ``info.json`` の対象セクション。
        media_type: メディアタイプ("photo" or "video")

    Raises:
        ValueError:
            実ファイルと ``info.json`` の内容に差異がある場合。
    """
    actual = set(actual_files)
    expected = set(info_files.keys())

    missing_in_info = actual - expected
    missing_in_files = expected - actual

    if missing_in_info:
        txt = ''
        for f in sorted(missing_in_info):
            if media_type == "photo":
                txt += '"' + f + '": {\n'
                txt += '  "tag": [],\n'
                txt += '  "favorite": false\n'
                txt += '},\n'
            elif media_type == "video":
                txt += '"' + f + '": {\n'
                txt += '  "thumbnail": [*, *],\n'
                txt += '  "tag": [],\n'
                txt += '  "favorite": false\n'
                txt += '},\n'
            else:
                raise ValueError("Invalid media type")

        raise ValueError(
            f'ファイルが存在するのにもかかわらずinfo.jsonに存在しない。次の内容をinfo.jsonの"{media_type}"セクションに記載すること。\n{txt}'
        )
    if missing_in_files:
        raise ValueError(
            "info.jsonに存在するのにもかかわらずファイルとして存在しない:\n"
            + "\n".join(sorted(missing_in_files))
        )


def _validate_tags(tags_in_files: set[str], tags_in_info: set[str]):
    """
    タグ定義と各メディアのタグの整合性を検証する。

    ``tag_info`` に定義されたタグと、
    各メディアに付与されたタグ集合が一致していることを確認する。

    Args:
        tags_in_files: 各メディアで使用されているタグ集合。
        tags_in_info: ``tag_info`` に定義されたタグ集合。

    Raises:
        ValueError:
            定義済みタグと使用タグが一致しない場合。
    """
    missing_in_files = tags_in_info - tags_in_files
    missing_in_info = tags_in_files - tags_in_info

    if missing_in_files:
        raise ValueError(
            "tag_infoに含まれるタグが各ファイルのタグに含まれない:\n"
            + "\n".join(sorted(missing_in_files))
        )

    if missing_in_info:
        raise ValueError(
            "各ファイルに含まれているタグがtag_infoに含まれない:\n"
            + "\n".join(sorted(missing_in_info))
        )

@validate_call
def preprocess() -> AppState:
    """
    アプリケーションで利用する全メディア情報を構築する。

    処理内容は以下のとおり。

    1. 画像・動画ファイルを列挙する。
    2. ``info.json`` を読み込む。
    3. ファイルおよびタグ定義の整合性を検証する。
    4. 写真・動画のサムネイル生成およびメタデータ取得を行う。
    5. ``Media`` モデルを構築する。
    6. ``AppState`` を生成して返す。

    Returns:
        フロントエンドで利用する全データを保持した ``AppState``。

    Raises:
        ValueError:
            ``info.json`` と実ファイル、またはタグ定義に不整合がある場合。
        RuntimeError:
            動画サムネイルの生成に失敗した場合。
        subprocess.CalledProcessError:
            ``ffprobe`` の実行に失敗した場合。
    """
    photo_files, movie_files = select_files([p.name for p in MEDIA_DIR.iterdir()])
    with INFO_JSON.open("r", encoding="utf-8") as f:
        info_input = json.load(f)

    _validate_files(photo_files, info_input["photo"], "photo")
    _validate_files(movie_files, info_input["video"], "video")

    tags_in_files = set()
    for item in (*info_input["photo"].values(), *info_input["video"].values()):
        tags_in_files.update(item["tag"])
    _validate_tags(tags_in_files, {x["name"] for x in info_input["tag_info"]})

    info_video = _preprocess_video(movie_files, {
        filename: item["thumbnail"]
        for filename, item in info_input["video"].items()
    })
    info_photo = _preprocess_photo(photo_files)


    # videos
    videos = [
        _build_media(
            prop["id"],
            "video",
            prop["total_time"],
            filename,
            prop["thumbnail_file_name"],
            prop["aspect_ratio"],
            info_input["video"][filename]["tag"],
            info_input["video"][filename]["favorite"]
        )
        for filename, prop in info_video.items()
    ]

    # photos
    photos = [
        _build_media(
            prop["id"],
            "photo",
            None,
            filename,
            prop["thumbnail_file_name"],
            prop["aspect_ratio"],
            info_input["photo"][filename]["tag"],
            info_input["photo"][filename]["favorite"]
        )
        for filename, prop in info_photo.items()
    ]


    birth_info = [BirthInfo(**b) for b in info_input["birth"]]
    tag_info = [TagCategory(**t) for t in info_input["tag_info"]]
    year_month_map = [YearMonth(**x) for x in create_year_month_map(photo_files + movie_files)]

    return AppState(
        year_month_map=year_month_map,
        videos=videos,
        photos=photos,
        tag_info=tag_info,
        birth_info=birth_info,
    )

