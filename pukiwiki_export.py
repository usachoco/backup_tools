import os
import time
import requests
import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yaml

# config 読み込み
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'secret.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# PukiWikiのベースURL
base_url = config['pukiwiki_url']

# 初期化
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'pukiwiki')
folder_path = os.path.join(folder_path, urlparse(base_url).netloc)
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
    # ファイル名禁則処理
    file_path = os.path.join(folder_path, name.replace("/", "__"))
    with open(file_path, 'w', encoding='utf-8') as f:
        # オリジナルファイル名 (name) をキープ
        f.write(f"{name}\n{text}")


if __name__ == "__main__":
    for name in tqdm.tqdm(get_page_name_list()):
        time.sleep(30)
        text = get_source(name)
        if text != "":
            write_to_local(name, text)