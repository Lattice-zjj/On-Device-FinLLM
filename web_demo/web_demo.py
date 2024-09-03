import os

os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'
import warnings
warnings.filterwarnings('ignore')
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from PIL import Image
import io

import base64
import time
import pandas as pd
from openai import OpenAI
from utils.stock import *
from utils.concept import *
from utils.rag import *
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    user_message = data['message']

    # Emit 'thinking' event to the client
    emit('thinking', {'message': '思考中...'}, broadcast=True)

    # Initialize OpenAI client
    port = os.environ.get("API_PORT", 8000)
    client = OpenAI(api_key="0", base_url=f"http://localhost:{port}/v1")

    # Get stock code from user message
    stock_code = get_stock_code_from_message(client, user_message)
    print(stock_code)
    references = []
    if '概念' in user_message:
        rot_rank = get_stock_concept_rot_rank()
        rot_rank = clean_stock_concept_data(rot_rank)
        
        if not os.path.exists('./storage_mini'):
            today_date, new_concept_info, concept_trend_info = fetch_concept_information()
            urls = extract_urls_from_concept_info(new_concept_info)
            # print(urls)

            create_and_store_index(
                urls=urls,
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                groq_model_name="llama-3.1-8b-instant",
                persist_dir="./storage_mini"
            )
        query = user_message
        resp = load_and_query_index("./storage_mini", query, "sentence-transformers/all-MiniLM-L6-v2", "llama-3.1-8b-instant")
        
        for node_with_score in resp.source_nodes:
            node = node_with_score.node
            url = node.metadata.get('url', 'Unknown URL')
            text_content = node.text
            references.append({"url": url, "text": text_content})

        
    # If a stock code is found, process the stock information
    if stock_code:
        stock_info = None
        try:
            stock_info = get_stock_info(stock_code)
            merged_df = generate_merged_dataframe(stock_info)
        except:
            merged_df = pd.DataFrame([])
        
        # Generate and emit the response message
        message_me = generate_response_message(stock_code, stock_info, user_message)
    else:
        message_me = generate_response_message(None, None, user_message)

    if references != []:
        references_str = '已知：' + references[0]["text"]
        message_me = references_str + message_me
        print(message_me)
    # Continue the conversation with the AI model
    messages_user = [{"role": "user", "content": message_me}]
    # print(message_me)
    response = client.chat.completions.create(
        messages=messages_user, model="Chinese-LLaMA-2-7B-hf", stream=True, temperature=1
    )
    accumulated_content = ""
    for part in response:
        content = part.choices[0].delta.content
        if content:
            accumulated_content += content
            emit('response', {'message': content}, broadcast=True)
            time.sleep(0.01)
    emit('response', {'list': references})
    emit('response', {'message': "[DONE]"}, broadcast=True)
    
    
    if stock_code:
        if not merged_df.empty:
        # Convert DataFrame to HTML and emit to client
            df_html = merged_df.to_html(escape=False, index=False, classes="table table-striped table-bordered")
            emit('response_dataframe', {'table': df_html})
        
        # Send stock chart
        send_stock_chart(stock_code, user_message)
    if '概念' in user_message:
        df_html = rot_rank.to_html(escape=False, index=False, classes="table table-striped table-bordered")
        emit('response_dataframe', {'table': df_html})

if __name__ == '__main__':
    socketio.run(app, debug=True)