from datetime import date


def to_date(yyyymmdd: int) -> date:
    """
    YYYYMMDD形式の整数をdate型に変換する。

    Parameters
    ----------
    yyyymmdd : int
        8桁のYYYYMMDD形式の日付（例: 20240115）。

    Returns
    -------
    date
        変換後のdateオブジェクト。

    Raises
    ------
    ValueError
        月が1〜12の範囲外の場合、年月日が有効範囲
        （1900〜2200年、1〜12月、1〜31日）外の場合、
        またはdate()生成時に不正な日付（例: 2月30日）と判定された場合。
    """
    year  = yyyymmdd // 10000
    month = yyyymmdd % 10000 // 100
    day   = yyyymmdd % 100

    if not (1900 <= year <= 2200 and 1 <= month <= 12 and 1 <= day <= 31):
        raise ValueError(f"日付が{year}年{month}月{day}日")

    try:
        return date(year, month, day)
    except ValueError as e:
        raise ValueError(f"不正な値: yyyymmdd={yyyymmdd}, year={year}, month={month}, day={day}, error={e}") from e


def extract_date_from_filename(filename: str) -> tuple[int, int, int, int]  :
    """
    ファイル名の先頭8桁（YYYYMMDD）から日付情報を抽出する。

    ファイル名は "YYYYMMDD..." の形式（先頭8文字が数字）で
    あることを前提とする。

    Parameters
    ----------
    filename : str
        日付情報を含むファイル名。先頭8文字がYYYYMMDDである必要がある。

    Returns
    -------
    tuple[int, int, int, int]
        (year, month, day, yyyymm) のタプル。
        yyyymmはファイル名先頭6文字（YYYYMM）を整数化した値。

    Raises
    ------
    ValueError
        ファイル名の先頭8文字が数字でない場合、
        またはto_date()が不正な日付と判定した場合。
    """
    if len(filename) < 8 or not filename[:8].isdecimal():
        raise ValueError(f"ファイル名が{filename}です。ファイル名が日付になっていません。")
    yyyymmdd = int(filename[:8])
    d = to_date(yyyymmdd)
    yyyymm = int(filename[:6])
    return d.year, d.month, d.day, yyyymm


def create_year_month_map(files: list[str]) -> list[dict[str, int | list[int]]]:
    """
    ファイル名から年月情報を抽出し、
    [{"year": YYYY, "months": [MM, ...]}, ...]
    の形式で返す。

    各ファイル名はextract_date_from_filename()で解析可能な
    形式（先頭8文字がYYYYMMDD）である必要がある。
    yyyymm（年月）単位で重複を除去したうえで、年ごとに
    月を昇順に格納する（同じ年月の日付が複数あっても、
    その月は1回だけ格納される）。

    Parameters
    ----------
    files : list
        ファイル名のリスト。

    Returns
    -------
    list[dict]
        年ごとの月一覧。年昇順でソートされ、各要素は
        {"year": int, "months": list[int]} の形式。
        monthsは重複のない昇順のリスト。

    Raises
    ------
    ValueError
        いずれかのファイル名がextract_date_from_filename()で
        解析できない場合。
    """
    # YYYYMMを抽出して重複除去・ソート
    year_month_list = sorted({
        extract_date_from_filename(filename)[3]
        for filename in files
    })

    # 年一覧
    year_list = sorted({
        yyyymm // 100
        for yyyymm in year_month_list
    })

    # 年ごとの月一覧
    month_list = [[] for _ in year_list]
    for yyyymm in year_month_list:
        year = yyyymm // 100
        month = yyyymm % 100
        idx = year_list.index(year)
        month_list[idx].append(month)

    # 出力
    return [
        {"year": year, "months": months}
        for year, months in zip(year_list, month_list)
    ]
