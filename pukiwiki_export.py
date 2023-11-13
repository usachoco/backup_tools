import os
import shutil
import time
import requests
from requests.auth import HTTPBasicAuth
import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import yaml
from git import Repo

# config 読み込み
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'pukiwiki_secret.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# github 設定
user = config['git_username']
email = config['git_email']
passwd = config['git_token']
target_repo = config['git_target_repo']

# PukiWikiのベースURL
base_url = config['pukiwiki_url']
pukiwiki_user = config['pukiwiki_admin']
pukiwiki_passwd = config['pukiwiki_password']
domain_name = urlparse(base_url).netloc

# repository 初期化
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_path = os.path.join(script_dir, 'pukiwiki')
data_path = os.path.join(repo_path, domain_name)
if os.path.exists(repo_path):
    repo = Repo(repo_path)
else:
    os.makedirs(repo_path)
    repo = Repo.clone_from(
        f"https://{user}:{passwd}@github.com/{target_repo}",
        repo_path
    )
repo.config_writer().set_value("user", "name", user).release()
repo.config_writer().set_value("user", "email", email).release()

# データの初期化
if os.path.exists(data_path):
    shutil.rmtree(data_path)
os.makedirs(data_path)

# User-Agent設定
user_agent = config['ua']
headers = {
    "User-Agent": f"{user_agent}",
}

# セッション取得
sess = requests.Session()
sess.auth = HTTPBasicAuth(pukiwiki_user, pukiwiki_passwd)

def get_page_name_list():
    result = []
    page_list_url = base_url + "?cmd=list"
    response = sess.get(page_list_url, headers=headers)
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
    response = sess.get(edit_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        textarea_tag = soup.find('textarea', {'name': 'msg'})
        if textarea_tag:
            result = textarea_tag.text.strip()
    return result


def write_to_local(name, text):
    # ファイル名禁則処理
    file_path = os.path.join(data_path, name.replace("/", "__"))
    with open(file_path, 'w', encoding='utf-8') as f:
        # オリジナルファイル名 (name) をキープ
        f.write(f"{name}\n{text}")


def check_missing_file(file_list):
    tmp_list = os.listdir(data_path)
    local_files = map(lambda x: x.replace('__', '/'), tmp_list)
    files = set(file_list) - set(local_files)
    print(f"{len(files)} 個のファイルが取得できていません。")
    for file in files:
        print(file)


def push_to_repository():
    repo.git.add(data_path)
    repo.index.commit("こんにちは！牛")
    repo.remote(name='origin').push()


if __name__ == "__main__":
    page_list = get_page_name_list()
    for name in tqdm.tqdm(page_list):
        time.sleep(10)
        text = get_source(name)
        if text != "":
            write_to_local(name, text)
        else:
            print(f"{name}:ソース読み込みに失敗しました。")
    push_to_repository()
    print(f"コミット完了しました。")
    check_missing_file(page_list)
