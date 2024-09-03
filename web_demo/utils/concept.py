import os
import pandas as pd
import requests
from datetime import datetime
column_mapping = {
    'code': '代码',
    'rate': '热度',
    'rise_and_fall': '涨跌幅',
    'name': '名称',
    'hot_rank_chg': '热度排名变化',
    'market_id': '市场ID',
    'hot_tag': '热度标签',
    'tag': '标签',
    'order': '顺序',
    'etf_rise_and_fall': 'ETF涨跌幅',
    'etf_product_id': 'ETF产品ID',
    'etf_name': 'ETF名称',
    'etf_market_id': 'ETF市场ID'
}

def get_stock_concept_rot_rank():
    url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/plate?'
    params = {'type': 'concept'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
    }
    res = requests.get(url=url, params=params, headers=headers)
    text = res.json()
    status_code = text['status_code']
    if int(status_code) == 0:
        df = pd.DataFrame(text['data']['plate_list'])
        df = df.rename(columns=column_mapping)
        return df
    else:
        print('获取数据失败')
        return pd.DataFrame()

def clean_stock_concept_data(df):
    df_cleaned = df.dropna(axis=1, how='any')
    df_cleaned['涨跌幅'] = df_cleaned['涨跌幅'].astype(str) + "%"
    df_cleaned = df_cleaned.drop(columns=['市场ID'])
    return df_cleaned

def fetch_concept_information():
    url = "https://dq.10jqka.com.cn/fuyao/concept_express/index/v1/get"
    response = requests.get(url)
    data = response.json()

    status_code = data.get('status_code')
    if status_code == 0:
        today_date = datetime.now().date().strftime("%Y-%m-%d")
        new_concepts = data.get('data', {}).get('new_concept', [])
        concept_trends = data.get('data', {}).get('concept_trends', {}).get('list', [])

        new_concept_info = [
            {
                "名称": concept['concept']['name'],
                "上涨": concept['concept']['increase'],
                "原因": concept['reason'],
                "新闻链接": concept['news_url']
            }
            for concept in new_concepts
        ]

        concept_trend_info = [
            {
                "名称": trend['concept']['name'],
                "动作": trend['action'],
                "原因": trend['reason'],
                "新闻链接": trend['news_url']
            }
            for trend in concept_trends
        ]

        return today_date, new_concept_info, concept_trend_info
    else:
        print(f"Failed to fetch data. Status code: {status_code}")
        return None, [], []

