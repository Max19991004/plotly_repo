import numpy as np
import pandas as pd
from proton_driver import client

# 指数走势数据
stock_data = {
    '上证指数': [150, 152, 153, 151, 154],
    '深证指数': [2700, 2720, 2710, 2730, 2740],
    '创业板指': [300, 305, 307, 306, 308]
}
dates = pd.date_range('2024-06-01', periods=5)

# 板块热力图数据
def random_sector_data():
    sectors = [
        "国有大行银行Ⅱ", "半导体", "通信服务", "证券Ⅱ", "保险Ⅱ", "化学制药", "电池", "汽车零部件", "乘用车",
        "软件开发", "消费电子", "煤炭开采", "专用设备", "光学光电子", "房地产开发", "航天装备Ⅱ", "铁路线Ⅱ",
        "家电Ⅱ", "元件", "自动化设备", "医疗服务", "物流", "环保设备", "计算机设备", "中药Ⅱ", "基础建设",
        "农业综合", "化学原料", "多元金融", "航运港口", "生物制品", "工程机械", "一般零售", "养殖业"
    ]
    n = len(sectors)
    change = np.round(np.random.uniform(-3, 3, n), 2)
    value = np.random.randint(100, 1000, n)
    df = pd.DataFrame({
        "板块": sectors,
        "涨跌幅": change,
        "市值": value
    })
    df["涨跌幅_str"] = df["涨跌幅"].map(lambda x: f"{x:.2f}")
    df["root"] = " "
    return df

# 涨跌分布数据
price_range_labels = [
    "(-20%,-10%]", "(-10%,-5%]", "(-5%,-3%]", "(-3%,0%]", "(0%,0%]", 
    "(0%,3%]", "(3%,5%]", "(5%,10%]", "(10%,20%]"
]

def fetch_latest_row():
    c = client.Client(host='192.168.1.10', port=8463)
    query = """
    SELECT 
        TIMESTAMP, SYMBOL, num_symbols, num_upper_limit, num_lower_limit, total_volume, active_buy_ratio,
        price_range_0, price_range_1, price_range_2, price_range_3, price_range_4,
        price_range_5, price_range_6, price_range_7, price_range_8
    FROM PriceVol_UpDownDist
    ORDER BY TIMESTAMP DESC LIMIT 1
    """
    try:
        rows = list(c.execute_iter(query))
        columns = [
            "TIMESTAMP", "SYMBOL", "num_symbols", "num_upper_limit", "num_lower_limit", "total_volume", "active_buy_ratio",
            "price_range_0", "price_range_1", "price_range_2", "price_range_3", "price_range_4",
            "price_range_5", "price_range_6", "price_range_7", "price_range_8"
        ]
        df = pd.DataFrame(rows, columns=columns)
        return df
    except Exception as e:
        print("数据库查询异常：", e)
        return pd.DataFrame()
    finally:
        try:
            c.disconnect()
        except Exception:
            pass