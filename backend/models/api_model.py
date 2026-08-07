from pydantic import BaseModel
from typing import Literal
from dataclasses import dataclass


class Media(BaseModel):
    """
    写真・動画1件分の情報。

    Attributes
    ----------
    id : str
        メディアを一意に識別するID。
    type : Literal["video", "photo"]
        メディア種別。
    year : int
        撮影年。
    month : int
        撮影月。
    day : int
        撮影日。
    file_name : str
        元ファイル名。
    thumbnail_file_name : str
        サムネイル画像のファイル名。
    aspect_ratio : float
        画像または動画のアスペクト比。
    tag : list[str]
        メディアに設定されたタグ一覧。
    favorite : bool
        お気に入り数。
    total_time : float | None
        動画の場合の再生時間（秒）。
        写真の場合はNone。
    title : str | None
        表示タイトル。
    """

    id: str
    type: Literal["video", "photo"]
    year: int
    month: int
    day: int
    file_name: str
    thumbnail_file_name: str
    aspect_ratio: float
    tag: list[str]
    favorite: bool
    total_time: float | None
    title: str | None


class YearMonth(BaseModel):
    """
    年ごとの存在する月一覧。

    Attributes
    ----------
    year : int
        年。
    months : list[int]
        その年に存在する月の一覧。
    """

    year: int
    months: list[int]


# --------------------------------- #
# 誕生日情報
# --------------------------------- #
class BirthInfo(BaseModel):
    """
    人物1名分の誕生日情報。

    Attributes
    ----------
    name : str
        人物名。
    year : int
        生まれた年。
    month : int
        生まれた月。
    day : int
        生まれた日。
    """

    name: str
    year: int
    month: int
    day: int


# --------------------------------- #
# タグカテゴリ内の期間情報
# --------------------------------- #
class TagSection(BaseModel):
    """
    タグカテゴリに設定された期間。
    ----------
    name : str
        期間の表示名。
    start : int
        開始日（YYYYMMDD形式）。
    finish : int
        終了日（YYYYMMDD形式）。
    """

    name: str
    start: int
    finish: int


# --------------------------------- #
# タグカテゴリ情報
# --------------------------------- #
class TagCategory(BaseModel):
    """
    タグカテゴリ1件分の情報。

    Attributes
    ----------
    name : str
        タグカテゴリ名。
    section : list[TagSection]
        カテゴリ内の期間一覧。
    """

    name: str
    section: list[TagSection]


# ---------------------------------------- #
# アプリケーション実行中の状態
# ---------------------------------------- #
@dataclass
class AppState:
    """
    アプリケーション全体で共有する状態情報。

    起動時に読み込んだメディア情報や設定情報を保持する。

    Attributes
    ----------
    year_month_map : list[YearMonth]
        年月選択用の一覧。
    videos : list[Media]
        動画メディア一覧。
    photos : list[Media]
        写真メディア一覧。
    tag_info : list[TagCategory]
        タグカテゴリ設定一覧。
    birth_info : list[BirthInfo]
        誕生日情報一覧。
    """

    year_month_map: list[YearMonth]
    videos: list[Media]
    photos: list[Media]
    tag_info: list[TagCategory]
    birth_info: list[BirthInfo]


# -----------------
# APIリクエスト
# -----------------

class SetTagRequest(BaseModel):
    """
    メディアへのタグ設定リクエスト。

    Attributes
    ----------
    fileName : str
        対象ファイル名。
    tags : list[str]
        設定するタグ一覧。
    type : Literal["video", "photo"]
        対象メディア種別。
    """

    fileName: str
    tags: list[str]
    type: Literal["video", "photo"]


class SetFavoriteRequest(BaseModel):
    """
    メディアへのお気に入り設定リクエスト。

    Attributes
    ----------
    fileName : str
        対象ファイル名。
    favorite : bool
        お気に入り登録するか否か。
    type : Literal["video", "photo"]
        対象メディア種別。
    """

    fileName: str
    favorite: bool
    type: Literal["video", "photo"]

# -----------------
# 認証関連
# -----------------

class Token(BaseModel):
    """
    JWTアクセストークンレスポンス。

    Attributes
    ----------
    access_token : str
        認証済みアクセストークン。
    token_type : str
        トークン種別（通常はbearer）。
    """

    access_token: str
    token_type: str