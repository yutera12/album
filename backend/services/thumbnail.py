import random
from pydantic import validate_call
from queries.media import filter_media_by_tag, filter_media_by_tag_and_section, get_taginfo_by_tag, filter_media_by_tag_without_section_period
from models.api_model import TagCategory, Media



def _random_item_for_tag_and_section(
    media_list: list[Media],
    tag_info: list[TagCategory],
    tag_name: str,
    section_name: str | None,
    used_file_names: set[str],
    favorite: bool
) -> Media | None:
    """
    指定したタグ・セクションに属するメディアから、ランダムに1件取得する。

    可能な限り未選択のメディアを優先する。
    未選択の候補が存在しない場合は、重複を許可して候補全体から選択する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        tag_info: タグおよびセクション情報の一覧。
        tag_name: 対象となるタグ名。
        section_name: 対象となるセクション名。
            None の場合はタグ全体を対象とする。
        used_file_names: すでに選択済みのファイル名を保持する集合。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        条件に一致するメディア。
        候補が存在しない場合は None。
    """
    items = filter_media_by_tag_and_section(
        media_list,
        tag_info,
        tag_name,
        section_name,
        favorite
    )

    if not items:
        return None

    # 未選択のメディアを優先
    available_items = [
        item
        for item in items
        if item.file_name not in used_file_names
    ]

    # 未選択があればそこから選択
    candidates = available_items or items

    chosen = random.choice(candidates)

    # 初回選択でも重複許可選択でも記録する
    used_file_names.add(chosen.file_name)

    return chosen


def _random_item_for_tag_and_no_section(
    media_list: list[Media],
    tag_info: list[TagCategory],
    tag_name: str,
    favorite: bool
) -> Media | None:
    """
    指定したタグに属し、セクションが設定されていないメディアから
    ランダムに1件取得する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        tag_info: タグおよびセクション情報の一覧。
        tag_name: 対象となるタグ名。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        条件に一致するメディア。
        候補が存在しない場合は None。
    """
    items = filter_media_by_tag_without_section_period(media_list, tag_info, tag_name, favorite)
    if not items:
        return None
    chosen = random.choice(items)
    return chosen


def _random_item_for_no_tag(
    media_list: list[Media],
    favorite: bool
) -> Media | None:
    """
    タグが設定されていないメディアからランダムに1件取得する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        タグ未設定のメディア。
        候補が存在しない場合は None。
    """
    items = filter_media_by_tag(media_list, "", favorite)
    if not items:
        return None
    chosen = random.choice(items)
    return chosen



@validate_call
def get_random_thumbnails_for_no_tag(
    media_list: list[Media],
    favorite: bool
) -> list[Media]:
    """
    タグ未設定メディアからランダムに1件選択し、サムネイル一覧として返す。

    選択されたメディアには title として "no-tag" を設定する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        タグ未設定メディアのサムネイル一覧。
        対象メディアが存在しない場合は空のリスト。
    """
    item = _random_item_for_no_tag(
        media_list,
        favorite
    )

    if item is None:
        return []

    return [
        item.model_copy(update={"title": "no-section"})
    ]


@validate_call
def get_random_thumbnails_for_all_tags(
    media_list: list[Media],
    tag_info: list[TagCategory],
    favorite: bool
) -> list[Media]:
    """
    全タグについて、それぞれランダムに1件ずつメディアを選択する。

    各タグに属するメディアから重複しないようにランダム選択を行う。
    選択されたメディアにはタグ名を title として設定する。
    また、タグが設定されていないメディアが存在する場合は、
    "no-tag" のタイトルで1件追加する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        tag_info: タグおよびセクション情報の一覧。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        各タグおよびタグ未設定メディアのサムネイル一覧。
        対象メディアが存在しないタグは結果に含まれない。
    """
    used_file_names: set[str] = set()
    results: list[Media] = []
    for tag in tag_info:
        item = _random_item_for_tag_and_section(
            media_list=media_list,
            tag_info=tag_info,
            tag_name=tag.name,
            section_name=None,
            used_file_names=used_file_names,
            favorite=favorite
        )
        if item is None:
            continue
        results.append(item.model_copy(update={"title": tag.name}))
    item = _random_item_for_no_tag(
        media_list=media_list,
        favorite=favorite
    )
    if item:
        results.append(item.model_copy(update={"title": "no-tag"}))
    return results


@validate_call
def get_random_thumbnails_for_all_sections_in_tag(
    media_list: list[Media],
    tag_info: list[TagCategory],
    tag_name: str,
    favorite: bool
) -> list[Media]:
    """
    指定したタグ配下の各セクションについて、ランダムに1件ずつメディアを選択する。

    指定タグに含まれる各セクションからメディアを選択し、
    同じメディアが複数セクションのサムネイルとして使用されないようにする。
    選択されたメディアにはセクション名を title として設定する。

    また、セクションが設定されていないメディアが存在する場合は、
    "no-section" のタイトルで1件追加する。

    Args:
        media_list: 写真・動画を含むメディア一覧。
        tag_info: タグおよびセクション情報の一覧。
        tag_name: 対象となるタグ名。
        favorite: True の場合、お気に入りメディアのみを対象とする。

    Returns:
        指定タグ配下の各セクションおよびセクション未設定メディアの
        サムネイル一覧。
        対象メディアが存在しないセクションは結果に含まれない。
    """

    target_tag_info = get_taginfo_by_tag(tag_info, tag_name)
    used_file_names: set[str] = set()
    results: list[Media] = []
    for section in target_tag_info.section:
        item = _random_item_for_tag_and_section(
            media_list=media_list,
            tag_info=tag_info,
            tag_name=tag_name,
            section_name=section.name,
            used_file_names=used_file_names,
            favorite=favorite
        )
        if item is None:
            continue
        results.append(item.model_copy(update={"title": section.name}))
    item = _random_item_for_tag_and_no_section(
        media_list=media_list,
        tag_info=tag_info,
        tag_name=tag_name,
        favorite=favorite
    )
    if item is not None:
        results.append(item.model_copy(update={"title": "no-section"}))
    return results
