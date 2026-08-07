import os
import json
from pydantic import validate_call
from models.api_model import Media


@validate_call
def set_tag(
    file_name: str,
    tags: list[str],
    media_type: str,
    media_list: list[Media]
) -> None:
    """
    指定したメディアのタグを info.json とメモリ上のデータの両方に反映する。

    Args:
        file_name: タグを更新するメディアのファイル名。
        tags: 設定するタグ一覧。
        media_type: info.json 内のメディア種別キー（"video" または "photo"）。
        media_list: 更新対象となるメモリ上のメディア一覧。

    Returns:
        None
    """
    filename = os.path.basename(file_name)
    with open("info.json", "r", encoding="utf-8") as f:
        info_input = json.load(f)
    info_input[media_type][filename]["tag"] = tags
    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(info_input, f, indent=2, ensure_ascii=False)

    for media in media_list:
        if media.file_name == file_name:
            media.tag = tags


@validate_call
def set_favorite(
    file_name: str,
    favorite: bool,
    media_type: str,
    media_list: list[Media]
) -> None:
    """
    指定したメディアのお気に入り設定を info.json とメモリ上のデータの両方に反映する。

    Args:
        file_name: タグを更新するメディアのファイル名。
        favorite: お気に入り設定。
        media_type: info.json 内のメディア種別キー（"video" または "photo"）。
        media_list: 更新対象となるメモリ上のメディア一覧。

    Returns:
        None
    """
    filename = os.path.basename(file_name)
    with open("info.json", "r", encoding="utf-8") as f:
        info_input = json.load(f)
    info_input[media_type][filename]["favorite"] = favorite
    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(info_input, f, indent=2, ensure_ascii=False)

    for media in media_list:
        if media.file_name == file_name:
            media.favorite = favorite