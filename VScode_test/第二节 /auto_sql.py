# data_pipeline.py — Tushare 版本

import tushare as ts
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# 初始化
ts.set_token("3802cf290ae13386d235c87bb54bc64f8b59630c274230aa5f1bbc4c")
pro = ts.pro_api()

def init_db(db="finance.db"):
    """建库建表，重复运行不报错"""
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker  TEXT NOT NULL,
            date    TEXT NOT NULL,
            open    REAL,
            high    REAL,
            low     REAL,
            close   REAL,
            volume  INTEGER,
            UNIQUE(ticker, date)
        )
    """)
    conn.commit()
    conn.close()

def update_prices(tickers: list, start_date=None, end_date=None, db="finance.db"):
    """
    拉取股价并写入数据库
    tickers: 股票代码列表，如 ["600519.SH", "000858.SZ"]
    start_date / end_date: 格式 "20240101"，不传则默认最近一年
    """
    if end_date is None:
        end_date = datetime.today().strftime("%Y%m%d")
    if start_date is None:
        start_date = (datetime.today() - timedelta(days=365)).strftime("%Y%m%d")

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    results = []

    for ticker in tickers:
        try:
            df = pro.daily(ts_code=ticker,
                           start_date=start_date,
                           end_date=end_date)

            if df.empty:
                results.append({"ticker": ticker, "inserted": 0, "status": "无数据"})
                continue

            # 整理列名
            df = df.rename(columns={"trade_date": "date", "vol": "volume"})
            df["ticker"] = ticker

            inserted = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO stock_prices
                        (ticker, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row["ticker"], row["date"],
                        row["open"], row["high"],
                        row["low"], row["close"], row["volume"]
                    ))
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass  # 已存在跳过

            conn.commit()
            results.append({"ticker": ticker, "inserted": inserted, "status": "ok"})

        except Exception as e:
            results.append({"ticker": ticker, "inserted": 0, "status": str(e)})

    conn.close()
    return pd.DataFrame(results)


# 每次运行只需要改这里
if __name__ == "__main__":
    init_db()

    watchlist = ["600519.SH", "000858.SZ", "600036.SH"]  # 茅台/五粮液/招商银行

    # 首次拉历史：拉一年
    report = update_prices(watchlist, start_date="20240101")

    # 之后每天增量更新，只拉最近7天（防节假日漏数据）
    # report = update_prices(watchlist)

    print(report)
