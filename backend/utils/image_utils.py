import cv2
import numpy as np


def _resize_keep_aspect(
    img: np.ndarray,
    target_w: int | None = None,
    target_h: int | None = None,
) -> np.ndarray:
    """
    アスペクト比を保ったまま画像をリサイズする内部関数。

    target_wとtarget_hはどちらか一方のみ指定する。
    target_wを指定した場合は幅に合わせて高さを算出し、
    target_hを指定した場合は高さに合わせて幅を算出する。

    Parameters
    ----------
    img : numpy.ndarray
        リサイズ対象の画像（OpenCV形式、shape=(H, W[, C])）。
    target_w : int, optional
        リサイズ後の幅（px）。指定する場合はtarget_hはNoneにする。
    target_h : int, optional
        リサイズ後の高さ（px）。指定する場合はtarget_wはNoneにする。

    Returns
    -------
    numpy.ndarray
        リサイズ後の画像。縮小時はINTER_AREA、
        拡大時はINTER_LINEARで補間される。
    """
    if not isinstance(img, np.ndarray):
        raise TypeError(f"img は numpy.ndarray である必要があります: {type(img)}")
    if img.ndim not in (2, 3):
        raise ValueError(f"img の shape が不正です: {img.shape}")
    if (target_w is None) == (target_h is None):
        raise ValueError("target_w と target_h はどちらか一方のみ指定してください")

    h, w = img.shape[:2]
    if target_w is not None:
        target_h = round(h * (target_w / w))
    else:
        target_w = round(w * (target_h / h))
    interp = cv2.INTER_AREA if target_w < w else cv2.INTER_LINEAR
    return cv2.resize(img, dsize=(target_w, target_h), interpolation=interp)



def scale(img: np.ndarray, px: int) -> np.ndarray:
    """
    アスペクト比を変えずに、画像の縦横のうち長いほうを指定のピクセルにそろえる。

    画像が縦長（高さ > 幅）の場合は高さをpxに、
    横長または正方形の場合は幅をpxに合わせてリサイズする。

    Parameters
    ----------
    img : numpy.ndarray
        リサイズ対象の画像（OpenCV形式）。
    px : int
        長辺の長さ（px）。

    Returns
    -------
    numpy.ndarray
        長辺がpxにそろえられた画像。
    """
    if not isinstance(img, np.ndarray):
        raise TypeError(f"img は numpy.ndarray である必要があります: {type(img)}")
    if img.ndim not in (2, 3):
        raise ValueError(f"img の shape が不正です: {img.shape}")
    h, w = img.shape[:2]
    if h > w:
        img =  _resize_keep_aspect(img, target_h=px)
    else:
        img = _resize_keep_aspect(img, target_w=px)
    return img
