import pytest

from models.api_model import Media


@pytest.fixture
def media_factory():
    def create_media(
        file_name: str,
        *,
        tag: list[str] | None = None,
        favorite: bool = False,
        year: int = 2026,
        month: int = 1,
        day: int = 1,
        title: str | None = None,
    ) -> Media:
        return Media(
            id=file_name,
            type="photo",
            year=year,
            month=month,
            day=day,
            file_name=file_name,
            thumbnail_file_name=f"thumb_{file_name}",
            aspect_ratio=1.0,
            tag=tag or [],
            favorite=favorite,
            total_time=None,
            title=title,
        )

    return create_media