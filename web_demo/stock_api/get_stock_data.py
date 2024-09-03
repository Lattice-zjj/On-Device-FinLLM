import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
import requests

def get_stock_data(stock_code):
    url = f"http://qt.gtimg.cn/q={stock_code}"
    response = requests.get(url)
    data = response.text
    return data

def parse_stock_data(data):
    # 去掉前缀和引号
    data = data.split('=')[1].strip('"')
    fields = data.split('~')

    stock_info = {
        "名字": fields[1],
        "代码": fields[2],
        "当前价格": fields[3],
        "昨收": fields[4],
        "今开": fields[5],
        "成交量（手）": fields[6],
        "外盘": fields[7],
        "内盘": fields[8],
        "买一": fields[9],
        "买一量（手）": fields[10],
        "卖一": fields[19],
        "卖一量": fields[20],
        "最近逐笔成交": fields[29],
        "时间": fields[30],
        "涨跌": fields[31],
        "涨跌%": fields[32],
        "最高": fields[33],
        "最低": fields[34],
        "换手率": fields[38],
        "市盈率": fields[39],
        "振幅": fields[43],
        "流通市值": fields[44],
        "总市值": fields[45],
        "市净率": fields[46],
        "涨停价": fields[47],
        "跌停价": fields[48],
    }

    return stock_info

def get_funds_flow(stock_code):
    url = f"http://qt.gtimg.cn/q=ff_{stock_code}"
    response = requests.get(url)
    data = response.text
    fields = data.split('=')[1].strip('"').split('~')

    funds_flow = {
        "代码": fields[0],
        "主力流入": fields[1],
        "主力流出": fields[2],
        "主力净流入": fields[3],
        "主力净流入占比": fields[4],
        "散户流入": fields[5],
        "散户流出": fields[6],
        "散户净流入": fields[7],
        "散户净流入占比": fields[8],
        "资金流入流出总和": fields[9],
        "名字": fields[12],
        "日期": fields[13],
    }

    return funds_flow

def get_market_analysis(stock_code):
    url = f"http://qt.gtimg.cn/q=s_pk{stock_code}"
    response = requests.get(url)
    data = response.text
    fields = data.split('=')[1].strip('"').split('~')

    market_analysis = {
        "买盘大单": fields[0],
        "买盘小单": fields[1],
        "卖盘大单": fields[2],
        "卖盘小单": fields[3],
    }

    return market_analysis

def get_brief_info(stock_code):
    url = f"http://qt.gtimg.cn/q=s_{stock_code}"
    response = requests.get(url)
    data = response.text
    fields = data.split('=')[1].strip('"').split('~')

    brief_info = {
        "名字": fields[1],
        "代码": fields[2],
        "当前价格": fields[3],
        "涨跌": fields[4],
        "涨跌%": fields[5],
        "成交量（手）": fields[6],
        "成交额（万）": fields[7],
        "总市值": fields[9],
    }

    return brief_info

if __name__ == "__main__":
    stock_code = "sz000858"
    
    # 获取详细股票信息
    stock_data = get_stock_data(stock_code)
    stock_info = parse_stock_data(stock_data)
    print("详细股票信息:", stock_info)

    # 获取实时资金流向
    funds_flow = get_funds_flow(stock_code)
    print("实时资金流向:", funds_flow)

    # 获取盘口分析
    market_analysis = get_market_analysis(stock_code)
    print("盘口分析:", market_analysis)

    # 获取简要信息
    brief_info = get_brief_info(stock_code)
    print("简要信息:", brief_info)
