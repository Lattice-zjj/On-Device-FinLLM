import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
import requests
import json

class AShareStockAPI:
    def __init__(self):
        self.api_url = "https://jay.tohours.com/miniprogram/api/external/stock/query-code"
        self.page_size = 100  # 每页请求的数据量，最大为100

    def get_all_stock_codes(self):
        stock_mapping = []
        page_no = 1
        while True:
            response = self.fetch_stock_data(page_no)
            if response and response.get('resCode') == '200':
                records = response['resData']['records']
                if not records:
                    break  # 如果没有更多数据，则退出循环
                for record in records:
                    exchange = self.determine_exchange(record['code'])
                    stock_mapping.append({
                        "name": record['name'],
                        "code": record['code'],
                        "exchange": exchange
                    })
                page_no += 1
            else:
                print("Failed to retrieve data")
                break
        return stock_mapping

    def fetch_stock_data(self, page_no):
        params = {
            "pageNo": page_no,
            "pageSize": self.page_size
        }
        response = requests.post(self.api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve data for page {page_no}")
            return None

    def determine_exchange(self, code):
        """
        根据股票代码判断所属交易所
        :param code: 股票代码
        :return: 交易所名称 (SH/SZ/BJ)
        """
        if code.startswith('60'):
            return 'SH'  # 上海证券交易所
        elif code.startswith('00') or code.startswith('30'):
            return 'SZ'  # 深圳证券交易所
        elif code.startswith('83') or code.startswith('87'):
            return 'BJ'  # 北京证券交易所
        else:
            return 'UNKNOWN'  # 未知交易所

    def save_to_json(self, stock_mapping, filename="data/stock_codes.json"):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(stock_mapping, file, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")

# 示例调用
if __name__ == "__main__":
    api = AShareStockAPI()
    stock_mapping = api.get_all_stock_codes()

    if stock_mapping:
        api.save_to_json(stock_mapping)
