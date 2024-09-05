import os
os.environ["REPLICATE_API_TOKEN"] = "your_REPLICATE_API_TOKEN"
os.environ['GROQ_API_KEY'] = 'your_GROQ_API_KEY'
GROQ_API_KEY = 'your_GROQ_API_KEY'
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    ServiceContext,
    load_index_from_storage
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq

import requests
from bs4 import BeautifulSoup
from llama_index.core import Document
def extract_urls_from_concept_info(new_concept_info):
    urls = [concept['新闻链接'] for concept in new_concept_info if '新闻链接' in concept]
    return urls

from bs4 import BeautifulSoup
from llama_index.core import Document
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from bs4 import BeautifulSoup
from llama_index.core import Document

def fetch_html_from_url(url):
    edge_options = EdgeOptions()
    edge_options.use_chromium = True  # if we miss this line, we can't make Edge headless
    # A little different from Chrome cause we don't need two lines before 'headless' and 'disable-gpu'
    edge_options.add_argument('headless')
    # edge_options.add_argument('disable-gpu')
    driver = Edge(executable_path='edgedriver_win64\msedgedriver.exe', options=edge_options)  # 替换为你的 EdgeDriver 路径
    driver.get(url)
    # 等待页面加载完成，可以调整等待时间
    driver.implicitly_wait(10)  # 等待最多10秒，直到页面加载完成

    # 获取 <div id="result-container"> 的 HTML 内容
    try:
        element = driver.find_element(By.ID, "result-container")
        html_content = element.get_attribute('outerHTML')
    except:
        html_content = None
    driver.quit()
    return html_content
def parse_html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # 提取所有<p>标签的文本内容，或你需要的其他内容
    text = ' '.join([p.get_text() for p in soup.find_all('p')])
    return text

def create_document_from_url(url):
    html_content = fetch_html_from_url(url)
    if html_content:
        text_content = parse_html_to_text(html_content)
        
        # 创建 Document 对象并添加元数据
        document = Document(
            text=text_content,
            metadata={"url": f'{url}'},
        )
        return document
    else:
        return None

def create_and_store_index(urls, model_name, groq_model_name, persist_dir):
    documents = []
    for url in urls:
        document = create_document_from_url(url)
        if document:
            documents.append(document)

    text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
    nodes = text_splitter.get_nodes_from_documents(documents, show_progress=True)

    embed_model = HuggingFaceEmbedding(model_name=model_name)
    llm = Groq(model=groq_model_name, api_key=GROQ_API_KEY) #api_key=os.getenv("GROQ_API_KEY"))
    service_context = ServiceContext.from_defaults(embed_model=embed_model, llm=llm)

    vector_index = VectorStoreIndex.from_documents(
        documents, show_progress=True, service_context=service_context, node_parser=nodes
    )
    vector_index.storage_context.persist(persist_dir=persist_dir)

def load_and_query_index(persist_dir, query_text, model_name, groq_model_name):
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    embed_model = HuggingFaceEmbedding(model_name=model_name)
    llm = Groq(model=groq_model_name, api_key=GROQ_API_KEY)#api_key=os.getenv("GROQ_API_KEY"))
    service_context = ServiceContext.from_defaults(embed_model=embed_model, llm=llm)

    index = load_index_from_storage(storage_context, service_context=service_context)
    query_engine = index.as_query_engine(service_context=service_context)

    resp = query_engine.query(query_text)
    return resp
