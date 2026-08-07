def min_sec_to_sec(minutes_seconds: tuple[float, float]) -> float:
    """
    (分, 秒)のタプルを秒に変換する。

    例：(1, 7) → 67
        1分7秒を67秒に変換する。

    Parameters
    ----------
    minutes_seconds : tuple[float, float]
        (分, 秒)のタプル。

    Returns
    -------
    float
        変換後の秒数。
    """
    minutes, seconds = minutes_seconds
    return minutes * 60 + seconds
