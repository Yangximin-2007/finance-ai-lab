import sqlite3
import pandas as pd

# 连接数据库（文件不存在会自动创建）
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# 建股价表
cursor.execute("""
CREATE TABLE IF NOT EXISTS stock_prices (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker    TEXT    NOT NULL,
    date      TEXT    NOT NULL,
    open      REAL,
    high      REAL,
    low       REAL,
    close     REAL,
    volume    INTEGER,
    UNIQUE(ticker, date)
)
""")

# 建财务指标表
cursor.execute("""
CREATE TABLE IF NOT EXISTS financials (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker    TEXT NOT NULL,
    period    TEXT NOT NULL,
    revenue   REAL,
    net_profit REAL,
    gross_margin REAL,
    UNIQUE(ticker, period)
)
""")

conn.commit()
print("数据库建好了，finance.db 已创建")

# `UNIQUE(ticker, date)` 防止重复插入同一天同一股票的数据，数据管道反复跑也不会有重复行。




 #!pip install tushare -q
import sqlite3
import tushare as ts
import pandas as pd
ts.set_token("3802cf290ae13386d235c87bb54bc64f8b59630c274230aa5f1bbc4c")
pro = ts.pro_api()

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# 拉贵州茅台的历史股价（港股/美股格式：600519.SS）
df = pro.daily(ts_code="600519.SH", 
               start_date="20240101", 
               end_date="20250101")
df["ticker"] = "600519.SH"  # 添加股票代码列，方便后续查询分析

# 整理格式
df = df.rename(columns={"trade_date":"date", "vol":"volume"})

# 存入数据库（已存在则跳过，不报错）
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
    except sqlite3.IntegrityError:
        pass  # UNIQUE 冲突，跳过

conn.commit()
print(f"写入 {len(df)} 条记录")


#===============验证数据真的进去了================
conn = sqlite3.connect("finance.db")
df_check = pd.read_sql("""
    SELECT date, close, volume
    FROM stock_prices
    WHERE ticker = '600519.SH'
    ORDER BY date DESC
    LIMIT 5
""", conn)
conn.close()
print(df_check)

#===============SQL查询实战================
conn = sqlite3.connect("finance.db")
# 1. 基础查询：最近20天收盘价
df1 = pd.read_sql("""
    SELECT date, close
    FROM stock_prices
    WHERE ticker = '600519.SH'
    ORDER BY date DESC
    LIMIT 20
""", conn)
print(df1)
# 2. 聚合：每月最高价/最低价
df2 = pd.read_sql("""
    SELECT
        substr(date, 1, 7) AS month,
        MAX(high)  AS month_high,
        MIN(low)   AS month_low,
        AVG(close) AS avg_close
    FROM stock_prices
    WHERE ticker = '600519.SH'
    GROUP BY month
    ORDER BY month DESC
""", conn)
print(df2)
# 3. 窗口函数：计算5日均线（重要！因子基础）
df3 = pd.read_sql("""
    SELECT
        date, close,
        AVG(close) OVER (
            ORDER BY date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS ma5
    FROM stock_prices
    WHERE ticker = '600519.SH'
    ORDER BY date DESC
    LIMIT 30
""", conn)
print(df3)
# 4. 异常检测：成交量超过30日均量2倍的日期
df4 = pd.read_sql("""
    SELECT * FROM (
        SELECT
            date, close, volume,
            AVG(volume) OVER (
                ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS avg_vol_30
        FROM stock_prices
        WHERE ticker = '600519.SH'
    )
    WHERE volume > avg_vol_30 * 2
    ORDER BY date DESC
""", conn)
print(df4)
