import os

PHOTO_EXTS = {".jpg", ".jpeg", ".png"}
MOVIE_EXTS = {".mp4"}


def select_files(files: list[str]) -> tuple[list[str], list[str]]:
    """
    ファイルリストから画像ファイル一覧と動画ファイル一覧を返す。

    拡張子（大文字小文字を区別しない）がPHOTO_EXTSに含まれるものは
    画像ファイル、MOVIE_EXTSに含まれるものは動画ファイルとして分類する。

    Parameters
    ----------
    files : list[str]
        分類対象のファイル名（またはパス）のリスト。

    Returns
    -------
    tuple[list[str], list[str]]
        (photo_files, movie_files) のタプル。
        それぞれ元のリストの順序を保った画像ファイル一覧、
        動画ファイル一覧。

    Raises
    ------
    ValueError
        拡張子がPHOTO_EXTSにもMOVIE_EXTSにも
        含まれないファイルが存在する場合。
    """
    photo_files = []
    movie_files = []

    for file in files:
        _, ext = os.path.splitext(file)
        ext = ext.lower()

        if ext in PHOTO_EXTS:
            photo_files.append(file)
        elif ext in MOVIE_EXTS:
            movie_files.append(file)
        else:
            raise ValueError(
                f"{file}は画像({PHOTO_EXTS})または動画({MOVIE_EXTS})ではありません。"
            )

    return photo_files, movie_files