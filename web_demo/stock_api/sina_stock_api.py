import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
import requests
import json
import re

class SinaStockAPI:
    def __init__(self, json_filename="data/stock_codes.json"):
        self.json_filename = json_filename
        self.base_url = "http://hq.sinajs.cn/list="
        self.name_to_code_url = "http://suggest3.sinajs.cn/suggest/name="
        self.headers = {'Referer': 'https://finance.sina.com.cn'}
        self.stock_data = self.load_stock_data()

    def load_stock_data(self):
        """
        从本地加载股票代码和名称数据
        """
        try:
            with open(self.json_filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"File {self.json_filename} not found.")
            return None


    def get_stock_data(self, stock_code):
        """
        获取股票的实时数据
        :param stock_code: 股票代码，例如 'sh601006' 表示上海交易所的大秦铁路
        :return: 解析后的股票数据
        """
        url = self.base_url + stock_code
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.text
            stock_data = self.parse_stock_data(data)
            return stock_data
        else:
            print(f"Failed to retrieve data for {stock_code}")
            return None

    def parse_stock_data(self, data):
        """
        解析返回的股票数据
        :param data: 新浪返回的原始数据字符串
        :return: 解析后的数据字典
        """
        try:
            data = data.split('"')[1]
            elements = data.split(',')

            stock_info = {
                "股票名称": elements[0],           # 股票名称
                "今日开盘价": float(elements[1]),    # 今日开盘价
                "昨日收盘价": float(elements[2]), # 昨日收盘价
                "当前价格": float(elements[3]),   # 当前价格
                "今日最高价": float(elements[4]),    # 今日最高价
                "今日最低价": float(elements[5]),     # 今日最低价
                "竞买价": float(elements[6]),     # 竞买价
                "竞卖价": float(elements[7]),     # 竞卖价
                "成交的股票数（手）": int(elements[8]) // 100,  # 成交的股票数（手）
                "成交金额（万元）": float(elements[9]) / 10000, # 成交金额（万元）
                "日期": elements[30],          # 日期
                "时间": elements[31]           # 时间
            }
            return stock_info
        except IndexError:
            print("Failed to parse data")
            return None

    def find_stock_code(self, stock_name):
        """
        通过股票名称模糊查找股票代码
        :param stock_name: 股票名称（部分或全部）
        :return: 匹配的股票代码和名称的列表
        """
        if not self.stock_data:
            print("Stock data is not loaded.")
            return None

        # 将搜索关键词转化为正则表达式，允许中间有任意字符
        pattern = '.*?'.join(stock_name)
        print(pattern)
        regex = re.compile(pattern)

        matching_stocks = []
        for stock in self.stock_data:
            # print(stock)
            if regex.search(stock['name']):
                matching_stocks.append({
                    "name": stock['name'],
                    "code": stock['code'],
                    "exchange": stock['exchange']
                })

        if matching_stocks:
            return matching_stocks
        else:
            print(f"No stocks found matching the name '{stock_name}'.")
            return None

    def parse_stock_code_data(self, data):
        """
        解析返回的股票代码数据
        :param data: 新浪返回的原始数据字符串
        :return: 股票代码和名称的字典
        """
        try:
            data = data.split('"')[1]
            stocks = data.split(';')
            stock_code_dict = {}
            for stock in stocks:
                if stock:
                    code_name = stock.split(',')
                    stock_code_dict[code_name[0]] = code_name[4]  # 股票代码对应股票名称
            return stock_code_dict
        except IndexError:
            print("Failed to parse stock code data")
            return None
