import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

# PukiWikiのベースURL
base_url = "https://crsdr.rowiki.jp/"

# 初期化
script_dir = os.path.dirname(os.path.abspath(__file__))
today_date = datetime.now().strftime("%Y-%m-%d")
folder_path = os.path.join(script_dir, 'wiki_source')
folder_path = os.path.join(folder_path, urlparse(base_url).netloc)
folder_path = os.path.join(folder_path, today_date)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


def get_page_name_list():
    result = []
    page_list_url = base_url + "?cmd=list"
    response = requests.get(page_list_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_tag = soup.find('ul')
        if ul_tag:
            a_tags = ul_tag.find_all('a', href=True, id=False)
            for a_tag in a_tags:
                page_name = a_tag.text.strip()
                result.append(page_name)
    return result


def get_source(page_name):
    result = ""
    edit_url = base_url + f"?cmd=edit&page={page_name}"
    response = requests.get(edit_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea_tag = soup.find('textarea', {'name': 'msgwhite'})
        if textarea_tag:
            result = textarea_tag.text.strip()
    return result


def write_to_local(name, text):
    """ 
    ファイル名の禁則処理として/を__に置き換えている
    オリジナルのファイル名はファイルの第一行に記述している
    ファイルの出力フォーマットは
    name\ntext
    なので、取り出すときは\nでsplitして
    0番をファイル名
    1番以降をコンテンツとして扱うこと
    """
    file_path = os.path.join(folder_path, name.replace("/", "__"))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{name}\n{text}")


if __name__ == "__main__":
    for name in get_page_name_list():
        time.sleep(30)
        text = get_source(name)
        if text != "":
            write_to_local(name, text)