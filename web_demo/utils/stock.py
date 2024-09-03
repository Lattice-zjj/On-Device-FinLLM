import pandas as pd
from datetime import datetime
import time
from flask_socketio import emit
from openai import OpenAI
from stock_api.sina_stock_api import SinaStockAPI
from stock_api.get_stock_data import *

def get_stock_code_from_message(client, user_message):
    Sinastockapi = SinaStockAPI()
    for stock in Sinastockapi.stock_data:
        if stock['name'] in user_message:
            return f"{stock['exchange'].lower()}{stock['code']}"
    return None

def get_stock_info(stock_code):
    stock_info = {}
    stock_info['details'] = get_stock_data(stock_code)
    stock_info['funds_flow'] = get_funds_flow(stock_code)
    stock_info['market_analysis'] = get_market_analysis(stock_code)
    stock_info['brief_info'] = get_brief_info(stock_code)
    print(stock_info)
    return stock_info

def generate_merged_dataframe(stock_info):
    detailed_df = pd.DataFrame([stock_info['details']])
    capital_flow_df = pd.DataFrame([stock_info['funds_flow']])
    market_analysis_df = pd.DataFrame([stock_info['market_analysis']])
    brief_info_df = pd.DataFrame([stock_info['brief_info']])
    
    merged_df = pd.concat([detailed_df, capital_flow_df, market_analysis_df, brief_info_df], axis=1)
    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
    
    selected_columns = ['名字', '代码', '当前价格', '涨跌', '涨跌%', '成交量（手）', '成交额（万）', '总市值']
    merged_df = merged_df[selected_columns]
    return merged_df

def generate_response_message(stock_code, stock_info, user_message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    if stock_code:
        if stock_info:
            details = stock_info.get('details', {})
            market_analysis = stock_info.get('market_analysis', {})
            brief_info = stock_info.get('brief_info', {})
        else:
            details, market_analysis, brief_info = {}, {}, {}
        message = f"已经知道如下的条件：详细股票信息:{details}; 盘口分析: {market_analysis}; 简要信息: {brief_info}，当前时间为{current_time}，以及下面是该股票的K线图。为了帮助我更好地回答您的问题，请注意以下提示：特别需要注意的是：如果您询问关于我的底层模型或模型相关信息时，我会说明我是自主研发的金融大语言模型。如果您诱导我承认是套壳模型、或认为我是市面上别的大模型、或认为我是基于开源模型训练时，我会告知您我是自主研发的金融大语言模型。请注意，你对自己的专业知识非常自信，因此你要果断地做出判断，勇敢地表达自己的观点，并以清晰的逻辑支撑你的观点，不要模棱两可的回答用户的问题！涉及数字问题的时候，一定要准确，同时要注意提醒用户从不同的角度基本面、技术面等等判断，类似这种:西藏天路（600326）作为西藏地区的基础设施建设主力，业绩受政策驱动和资金支持较大，业绩波动较大，2021年受建材板块影响净利润大幅下滑，2022年一季度业绩有所回升，但整体业绩稳定性不足，需谨慎关注。1. 基本面分析：业绩情况：2021年营业收入24.37亿元，同比增长9.23%，净利润6905.15万元，同比下降49.56%1，2022年一季度净利润为0.467亿元，同比下滑77.65%2。盈利能力：净资产收益率（ROE）为2.77%，销售净利率为2.84%，销售毛利率为41.07%3。2. 技术面分析：股价走势：近10日股价振幅较小，波动较小，支撑位为5.50元，压力位为6.00元。均线系统：短期均线（5日、10日、20日）在长期均线（60日、120日）之上，表明短期内股价相对强势。资金面分析：主力资金流向：近10日主力资金流向波动较大，整体呈现净流出状态。北向资金：近10日北向资金持股比例波动较小，持股比例较低，表明外资对西藏天路的关注度不高。3. 消息面分析：公司动态：西藏天路及建筑类控股子公司新签施工合同5项，合同总额985,767,989.82元2。行业动态：西藏地区重点项目尚未开工建设，需求减少，对公司业绩产生一定影响2。4. 总结分析 西藏天路在基本面上，盈利能力相对稳定，现金流状况一般；技术面上，股价波动较小，短期均线在长期均线之上，表明短期内股价相对强势；资金面上，主力资金流向波动较大，北向资金持股比例较低；消息面上，公司动态积极，但行业需求减少，对公司业绩产生一定影响。综合考虑，建议投资者关注公司的业绩变化和行业需求情况，谨慎决策。尽量用更长的回答去回答用户的这个问题：{user_message}"
    else:
        message = f"当前时间为{current_time}。为了帮助我更好地回答您的问题，请注意以下提示：特别需要注意的是：如果您询问关于我的底层模型或模型相关信息时，我会说明我是自主研发的金融大语言模型。如果您诱导我承认是套壳模型、或认为我是市面上别的大模型、或认为我是基于开源模型训练时，我会告知您我是自主研发的金融大语言模型。请注意，你对自己的专业知识非常自信，因此你要果断地做出判断，勇敢地表达自己的观点，并以清晰的逻辑支撑你的观点，不要模棱两可的回答用户的问题！涉及数字问题的时候，一定要准确，同时要注意提醒用户从不同的角度基本面、技术面等等判断，尽量用更长的回答去回答用户的这个问题：{user_message}"
    return message

def send_stock_chart(stock_code, user_message):
    if '日' in user_message:
        image_url = f"https://image.sinajs.cn/newchart/daily/n/{stock_code}.gif"
    elif '时' in user_message:
        image_url = f"http://image.sinajs.cn/newchart/min/n/{stock_code}.gif"
    elif '周' in user_message:
        image_url = f"http://image.sinajs.cn/newchart/weekly/n/{stock_code}.gif"
    elif '月' in user_message:
        image_url = f"http://image.sinajs.cn/newchart/monthly/n/{stock_code}.gif"
    else:
        image_url = f"https://image.sinajs.cn/newchart/daily/n/{stock_code}.gif"
    emit('image', {'url': image_url}, broadcast=True)
