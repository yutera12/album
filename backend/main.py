import argparse
import uvicorn
import logging
from typing import Annotated, Literal
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Request, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse

from logging_config import setup_logging
from paths import MEDIA_DIR, THUMBNAIL_DIR, LOG_DIR
from models.auth_models import Base, User
from models.api_model import Token, SetTagRequest, SetFavoriteRequest, AppState, BirthInfo, YearMonth, Media
from queries.media import filter_media_by_month, filter_media_by_tag, filter_media_by_tag_and_section, filter_media_by_tag_without_section_period
from services.preprocess import preprocess
from services.thumbnail import get_random_thumbnails_for_no_tag, get_random_thumbnails_for_all_tags, get_random_thumbnails_for_all_sections_in_tag
from services.update import set_tag, set_favorite
from services.auth import get_db, login, get_current_user
from database.database import engine

# ログ設定
setup_logging()
logger = logging.getLogger(__name__)

# DB初期化
Base.metadata.create_all(bind=engine)

def get_app_state(request: Request) -> AppState:
    return request.app.state.data


# ------------------------------------------------------------------
# 起動時に一度だけ preprocess() を実行し、その結果を app.state.data に保持する
# ------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading application data")

    app.state.data = preprocess()  # 起動時の前処理

    logger.info(
        "Media loaded: photos=%d, videos=%d",
        len(app.state.data.photos),
        len(app.state.data.videos),
    )

    logger.info(
        "Metadata loaded: tags=%d, birthdays=%d, year_months=%d",
        len(app.state.data.tag_info),
        len(app.state.data.birth_info),
        len(app.state.data.year_month_map),
    )

    yield  # ここでアプリが稼働。yield以降はシャットダウン時の処理を書ける（今回はなし）

# ------------------------------------------------------------------
# アプリ生成・ミドルウェア設定
# ------------------------------------------------------------------
app = FastAPI(lifespan=lifespan)

# 予期せぬ例外発生時
@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unexpected error: method=%s path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# 指定URL以外キャッシュ禁止
@app.middleware("http")
async def disable_cache(request: Request, call_next):
    response = await call_next(request)
    cache_allowed_paths = (
        "/media",
        "/thumbnail",
    )
    if not request.url.path.startswith(cache_allowed_paths):
        response.headers["Cache-Control"] = "no-store"
    return response

# CORS設定：フロントエンド（Angularアプリなど、localhost:4200）からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # 許可するオリジン
    allow_credentials=True,                   # Cookie等の資格情報を許可
    allow_methods=["*"],                      # 全HTTPメソッドを許可
    allow_headers=["*"],                      # 全ヘッダーを許可
)

# ------------------------------------------------------------------
# 認証系エンドポイント
# ------------------------------------------------------------------
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """認証成功時に、アクセスtokenを返すエンドポイント"""
    token = login(db, form_data)
    return token

@app.get("/is-admin", response_model=bool)
def is_admin(current_user: Annotated[User, Depends(get_current_user)]):
    """現在のユーザが管理者権限を持つ場合にTrueを、そうでない場合にFalseを返すエンドポイント"""
    return current_user.is_admin

# ------------------------------------------------------------------
# サムネイル関連エンドポイント
# ------------------------------------------------------------------
@app.get("/thumbnail-random", response_model=list[Media])
def get_thumbnail_random(favorite: bool, _: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """タグごとのランダムで1枚選択されたサムネイル情報を取得するエンドポイント"""
    return get_random_thumbnails_for_all_tags(
        media_list=data.photos + data.videos,
        tag_info=data.tag_info,
        favorite=favorite
    )


@app.get("/thumbnail-random/{tag}", response_model=list[Media])
def get_thumbnail_random_tag(tag: str, favorite: bool, _: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """指定タグについて、セクションごとのランダムに1枚選択されたサムネイル情報を取得するエンドポイント"""
    if tag == "no-tag":
        return get_random_thumbnails_for_no_tag(
            media_list=data.photos+data.videos,
            favorite=favorite
        )
    return get_random_thumbnails_for_all_sections_in_tag(
        media_list=data.photos+data.videos,
        tag_info=data.tag_info,
        tag_name=tag,
        favorite=favorite
    )

# ------------------------------------------------------------------
# メディア（写真・動画）取得エンドポイント
# ------------------------------------------------------------------
@app.get("/{media_type}/month/{yyyymm}", response_model=list[Media])
def get_videos_by_month(media_type: str, yyyymm: str, favorite: bool, _: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """指定した月のメディアを取得するエンドポイント"""
    target_data = {
        "videos": data.videos,
        "photos": data.photos,
    }[media_type]
    return filter_media_by_month(target_data, yyyymm, favorite)


@app.get("/{media_type}/tag/{tag}/section/{section}", response_model=list[Media])
def get_videos_by_tag_section(media_type: Literal["videos", "photos"], tag: str, section: str, favorite: bool, _: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """指定したタグ、セクションのメディアを取得するエンドポイント"""
    target_data = {
        "videos": data.videos,
        "photos": data.photos,
    }[media_type]
        
    if tag == "no-tag" and section == "no-section":
        return filter_media_by_tag(target_data, "", favorite)
    if tag != "no-tag" and section == "no-section":
        return filter_media_by_tag_without_section_period(target_data, data.tag_info, tag, favorite)
    if tag != "no-tag" and section != "no-section":
        return filter_media_by_tag_and_section(target_data, data.tag_info, tag, section, favorite)
    raise HTTPException(
        status_code=400,
        detail="section cannot be specified without tag"
    )


# ------------------------------------------------------------------
# タグ・誕生日・年月マップ関連エンドポイント
# ------------------------------------------------------------------
@app.get("/tag-list", response_model=list[str])
def get_tag_list(_: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """メディアに設定されたタグのリストを返すエンドポイント"""
    return [x.name for x in data.tag_info]

@app.get("/birthdays", response_model=list[BirthInfo])
def get_birthdays(_: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """誕生日の情報を返すエンドポイント"""
    return data.birth_info

@app.get("/year-month-map", response_model=list[YearMonth])
def get_year_month_map(_: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """メディアが存在する年・月のリストを返すエンドポイント"""
    return data.year_month_map


# ----------------------------------------------------------------
# タグ、お気に入り設定API（管理者権限必要）
# ----------------------------------------------------------------
@app.post("/set-tag", response_model=dict)
def set_tag_(req: SetTagRequest, current_user: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """メディアのタグ情報を変更するエンドポイント"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    if req.type == "video":
        set_tag(req.fileName, req.tags, req.type, data.videos)
    elif req.type == "photo":
        set_tag(req.fileName, req.tags, req.type, data.photos)
    else:
        raise HTTPException(status_code=400, detail=f"invalid type: {req.type}")
    logger.info(
        "Tag updated: user=%s file=%s type=%s tags=%s",
        current_user.username,
        req.fileName,
        req.type,
        req.tags,
    )
    return {"success": True}

@app.post("/set-favorite", response_model=dict)
def set_favorite_(req: SetFavoriteRequest, current_user: Annotated[User, Depends(get_current_user)], data: AppState = Depends(get_app_state)):
    """メディアのお気に入り情報を変更するエンドポイント"""
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    if req.type == "video":
        set_favorite(req.fileName, req.favorite, req.type, data.videos)
    elif req.type == "photo":
        set_favorite(req.fileName, req.favorite, req.type, data.photos)
    else:
        raise HTTPException(status_code=400, detail=f"invalid type: {req.type}")
    logger.info(
        "Favorite updated: user=%s file=%s type=%s favorite=%s",
        current_user.username,
        req.fileName,
        req.type,
        req.favorite,
    )
    return {"success": True}


# --------
# メディア
# --------
@app.get("/media/{media_type}/{id}")
def get_media(response: Response, media_type: Literal["video", "photo"], id: str, data: AppState = Depends(get_app_state)):
    """メディアを取得するエンドポイント"""
    response.headers["Cache-Control"] = "private, max-age=86400"    # 
    target_data = {
        "video": data.videos,
        "photo": data.photos,
    }[media_type]
    media = next((x for x in target_data if x.id == id), None)
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    path = MEDIA_DIR / media.file_name
    if not path.exists():
        raise HTTPException(404, detail="Media not found")
    return FileResponse(path)


@app.get("/thumbnail/{media_type}/{id}")
def get_thumbnail(response: Response, media_type: Literal["video", "photo"], id: str, data: AppState = Depends(get_app_state)):
    """サムネイルを取得するエンドポイント"""
    response.headers["Cache-Control"] = "private, max-age=86400"

    target_data = {
        "video": data.videos,
        "photo": data.photos,
    }[media_type]
    media = next((x for x in target_data if x.id == id), None)
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")
    path = THUMBNAIL_DIR / media.thumbnail_file_name
    if not path.exists():
        raise HTTPException(404, detail="Media not found")
    return FileResponse(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--access-log",
        action="store_true",
        help="アクセスログを有効にする",
    )
    args = parser.parse_args()

    uvicorn.run(
        app,
        host="localhost",
        port=10000,
        access_log=args.access_log,
    )