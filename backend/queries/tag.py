from pydantic import validate_call
from models.api_model import TagCategory, TagSection


@validate_call
def get_taginfo_by_tag(
    tag_info: list[TagCategory],
    tag_name: str
) -> TagCategory:
    """
    指定したタグ名に一致するタグ情報を取得する。

    Args:
        tag_info: 検索対象となるタグ情報一覧。
        tag_name: 取得対象となるタグ名。

    Returns:
        指定したタグ名に一致する TagCategory。

    Raises:
        ValueError: 指定したタグ名が存在しない場合。
    """
    result = next((t for t in tag_info if t.name == tag_name), None)
    if result is None:
        raise ValueError(f"Tag not found: {tag_name!r}")
    return result


@validate_call
def get_taginfo_by_tag_and_section(
    tag_info: list[TagCategory],
    tag_name: str,
    section_name: str,
) -> TagSection:
    """
    指定したタグ名およびセクション名に一致するセクション情報を取得する。

    Args:
        tag_info: 検索対象となるタグ情報一覧。
        tag_name: 検索対象となるタグ名。
        section_name: 取得対象となるセクション名。

    Returns:
        指定したタグ内のセクション情報。

    Raises:
        ValueError:
            指定したタグ名またはセクション名が存在しない場合。
    """
    target_tag = get_taginfo_by_tag(tag_info, tag_name)
    result = next(
        (sec for sec in target_tag.section if sec.name == section_name),
        None,
    )
    if result is None:
        raise ValueError(
            f"Section {section_name!r} not found in tag {tag_name!r}."
        )
    return result