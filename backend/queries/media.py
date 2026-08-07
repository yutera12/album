from datetime import date
from pydantic import validate_call

from models.api_model import TagCategory, TagSection, Media
from utils.date_utils import to_date
from .tag import get_taginfo_by_tag, get_taginfo_by_tag_and_section


def _match_favorite(media: Media, favorite: bool) -> bool:
    """
    お気に入り条件にメディアが一致するか判定する。

    favorite が True の場合は favorite が Trueのメディアのみ一致する。
    favorite が False の場合はすべてのメディアを一致とする。

    Args:
        media: 判定対象のメディア。
        favorite: お気に入りのみを対象にするかどうか。

    Returns:
        お気に入り条件に一致する場合は True、それ以外は False。
    """
    return not favorite or media.favorite


def _match_tag(media: Media, tag: str | None) -> bool:
    """
    指定したタグ条件にメディアが一致するか判定する。

    tag が None の場合はタグによる絞り込みを行わず、
    tag が空文字列の場合はタグを持たないメディアのみ一致する。
    それ以外の場合は、指定タグを含むメディアが一致する。

    Args:
        media: 判定対象のメディア。
        tag: 絞り込み対象のタグ。
            None の場合はタグ条件なし。
            空文字列の場合はタグなしを指定。

    Returns:
        タグ条件に一致する場合は True、それ以外は False。
    """
    if tag is None:
        return True

    if tag == "":
        return not media.tag

    return tag in media.tag


def _is_media_in_period(
    media: Media,
    start_date: date,
    finish_date: date,
) -> bool:
    """
    media の撮影日が start_date ～ finish_date の範囲内か判定する。

    Args:
        media: 判定対象のメディア。
        start_date: 判定開始日。
        finish_date: 判定終了日。

    Returns:
        撮影日が期間内であれば True、それ以外は False。
    """
    return start_date <= date(media.year, media.month, media.day) <= finish_date



def _get_section_period(section: TagSection) -> tuple[date, date]:
    """
    セクション情報から開始日と終了日を取得する。

    Args:
        section: セクション情報。

    Returns:
        (開始日, 終了日)

    Raises:
        ValueError: 開始日が終了日より後の場合。
    """
    start_date = to_date(section.start)
    finish_date = to_date(section.finish)
    if start_date > finish_date:
        raise ValueError(
            f"Section {section.name!r} has start ({start_date}) "
            f"later than finish ({finish_date})"
        )

    return start_date, finish_date


@validate_call
def filter_media_by_tag(
    media_list: list[Media],
    tag: str | None,
    favorite: bool
) -> list[Media]:
    """
    指定したタグおよびお気に入り条件でメディアを絞り込む。

    Args:
        media_list: 絞り込み対象のメディア一覧。
        tag: 絞り込み対象のタグ。
            None の場合はタグ条件を無視する。
            空文字列の場合はタグを持たないメディアを対象とする。
        favorite: True の場合、お気に入り登録済みのメディアのみ対象とする。

    Returns:
        条件に一致したメディア一覧。
    """
    return [
        m
        for m in media_list
        if _match_tag(m, tag)
        and _match_favorite(m, favorite)
    ]


@validate_call
def filter_media_by_tag_and_section(
    media: list[Media],
    tag_info: list[TagCategory],
    tag_name: str,
    section_name: str | None,
    favorite: bool
) -> list[Media]:
    """
    指定したタグ、セクション期間、お気に入り条件でメディアを絞り込む。

    Args:
        media: 絞り込み対象のメディア一覧。
        tag_info: タグおよびセクション期間情報の一覧。
        tag_name: 絞り込み対象のタグ名。
        section_name: 絞り込み対象のセクション名。
            空文字列、Noneの場合はセクション期間による絞り込みを行わない。
        favorite: True の場合、お気に入り登録済みのメディアのみ対象とする。

    Returns:
        条件に一致したメディア一覧。
    """
    if not section_name:
        return filter_media_by_tag(media, tag_name, favorite)

    section = get_taginfo_by_tag_and_section(
        tag_info,
        tag_name,
        section_name,
    )
    start_date, finish_date = _get_section_period(section)

    return [
        m
        for m in media
        if _match_tag(m, tag_name)
        and _match_favorite(m, favorite)
        and _is_media_in_period(m, start_date, finish_date)
    ]


@validate_call
def filter_media_by_tag_without_section_period(
    media: list[Media],
    tag_info: list[TagCategory],
    tag_name: str,
    favorite: bool
) -> list[Media]:
    """
    指定したタグに属し、いずれのセクション期間にも含まれないメディアを取得する。

    Args:
        media: 絞り込み対象のメディア一覧。
        tag_info: タグおよびセクション期間情報の一覧。
        tag_name: 絞り込み対象のタグ名。
        favorite: True の場合、お気に入り登録済みのメディアのみ対象とする。

    Returns:
        指定タグに一致し、セクション期間外のメディア一覧。
    """
    tag = get_taginfo_by_tag(tag_info, tag_name)
    periods = [
        _get_section_period(section)
        for section in tag.section
    ]
    return [
        m
        for m in media
        if _match_tag(m, tag_name)
        and _match_favorite(m, favorite)
        and not any(
            _is_media_in_period(m, start, finish)
            for start, finish in periods
        )
    ]


@validate_call
def filter_media_by_month(
    media: list[Media],
    yyyymm: str,
    favorite: bool
) -> list[Media]:
    """
    指定した年月およびお気に入り条件でメディアを絞り込む。

    Args:
        media: 絞り込み対象のメディア一覧。
        yyyymm: 6桁の年月文字列 (例: "202610")。
        favorite: True の場合、お気に入り登録済みのメディアのみ対象とする。

    Returns:
        指定した年月に一致するメディア一覧。
        戻り値の title は None に設定される。

    Raises:
        ValueError:
            yyyymm が6桁の数字でない場合。
        ValueError:
            月が1～12の範囲外の場合。
    """
    if not isinstance(yyyymm, str) or len(yyyymm) != 6 or not yyyymm.isdigit():
        raise ValueError("yyyymm must be a 6-digit numeric string like '202610'")

    year = int(yyyymm[:4])
    month = int(yyyymm[4:])
    if not (1 <= month <= 12):
        raise ValueError("month must be between 1 and 12")

    return [
        m
        for m in media
        if (
            m.year == year
            and m.month == month
            and _match_favorite(m, favorite)
        )
    ]