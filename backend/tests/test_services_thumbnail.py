import services.thumbnail as thumbnail
from models.api_model import TagCategory, TagSection

# --------------------------------------------- #
# thumbnail.py _random_item_for_tag_and_section #
# --------------------------------------------- #
def test_random_item_for_tag_and_section_prefers_unused(
    media_factory,
    monkeypatch,
):
    """未使用のものを優先するかのテスト"""
    media = [
        media_factory("a.jpg", tag=["旅行"]),
        media_factory("b.jpg", tag=["旅行"]),
    ]

    tag_info = [
        TagCategory(
            name="旅行",
            section=[
                TagSection(
                    name="東京",
                    start=20260101,
                    finish=20261231,
                )
            ],
        )
    ]

    used_file_names = {"a.jpg"}

    monkeypatch.setattr(
        thumbnail.random,
        "choice",
        lambda items: items[0],
    )

    result = thumbnail._random_item_for_tag_and_section(
        media,
        tag_info,
        "旅行",
        "東京",
        used_file_names,
        False,
    )

    assert result is not None
    assert result.file_name == "b.jpg"
    assert used_file_names == {"a.jpg", "b.jpg"}



def test_random_item_for_tag_and_section_returns_none_when_no_items(
    media_factory,
):
    """候補が存在しない場合にNoneを返すかのテスト"""
    media = [
        media_factory("20250101.jpg", tag=["旅行"], year=2025),
    ]

    tag_info = [
        TagCategory(
            name="旅行",
            section=[
                TagSection(
                    name="東京",
                    start=20260101,
                    finish=20261231,
                )
            ],
        )
    ]

    used_file_names: set[str] = set()

    result = thumbnail._random_item_for_tag_and_section(
        media,
        tag_info,
        "旅行",
        "東京",
        used_file_names,
        False,
    )

    assert result is None
    assert used_file_names == set()


def test_random_item_for_tag_and_section_allows_duplicate_when_all_used(
    media_factory,
    monkeypatch,
):
    """未選択の候補が存在しない場合は、重複を許可して候補全体から選択するかのテスト"""
    media = [
        media_factory("a.jpg", tag=["旅行"]),
        media_factory("b.jpg", tag=["旅行"]),
    ]

    tag_info = [
        TagCategory(
            name="旅行",
            section=[
                TagSection(
                    name="東京",
                    start=20260101,
                    finish=20261231,
                )
            ],
        )
    ]

    used_file_names = {"a.jpg", "b.jpg"}

    monkeypatch.setattr(
        thumbnail.random,
        "choice",
        lambda items: items[0],
    )

    result = thumbnail._random_item_for_tag_and_section(
        media,
        tag_info,
        "旅行",
        "東京",
        used_file_names,
        False,
    )

    assert result is not None
    assert result.file_name == "a.jpg"
