import os, shutil, time
import requests
import tqdm
import yaml
from bs4 import BeautifulSoup
from git import Repo

# config 読み込み
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'secret.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
user = config['git_username']
email = config['git_email']
passwd = config['git_token']
account = config['atwiki_name']
target_repo = config['git_target_repo']

# repository 初期化
repo_path = os.path.join(script_dir, 'repo')
data_path = os.path.join(repo_path, account)
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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": f"https://w.atwiki.jp/{account}/backupx/1/list.html",
}

def get_page_list():
    result = [] # result = [name, id]
    page_list_url = f"https://w.atwiki.jp/{account}/list?pp="
    for i in range(1, 100): # 1ページ 100 URL * 100 = 10000 URLまで対応
        response = requests.get(f"{page_list_url}{i}", headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            ul_tag = soup.find('ul', {'class': 'atwiki-page-list'})
            if ul_tag:
                a_tags = ul_tag.find_all('a', href=True)
                for a_tag in a_tags:
                    page_title = a_tag.attrs['title'].split(' (')[0]
                    page_id = a_tag.attrs['href'].split('/')[-1].split('.')[0]
                    arg = [page_title, page_id]
                    if arg in result:
                        # @wikiの仕様では無効なppを指定すると1ページ目に戻るので、既に登録済みのページ情報の有無を終了トリガーにします
                        return result
                    result.append(arg)
    return result


def get_source(page_id, retry=3):
    backup_url = f"https://w.atwiki.jp/{account}/?cmd=backup&action=source&pageid={page_id}"
    result = ""
    for i in range(retry):
        response = requests.get(backup_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_tag = soup.find('pre')
            if pre_tag:
                result = pre_tag.text.strip().replace('\r\n', '\n')
            return result
        else:
            time.sleep(10)
    return result


def write_to_local(name, text):
    """ 
    ファイル名の禁則処理として / を __ に置き換えています
    オリジナルのファイル名はファイルの第一行に記述しています
    ファイルの出力フォーマットは name\ntext なので、
    取り出すときは \n で split() して 0番をファイル名、1番以降をコンテンツとして扱ってください
    """
    file_path = os.path.join(data_path, name.replace("/", "__"))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"{name}\n{text}")


if __name__ == "__main__":
    page_list = get_page_list()
    try :
        for page_name, page_id in tqdm.tqdm(page_list):
            """
            @wiki アクセス規制検証
            5秒 = 規制弱で規制されることを確認しています
            10秒 = 規制強で規制されないことを確認しています
            """
            time.sleep(10)
            source = get_source(page_id)
            if source == "":
                raise ValueError()
            write_to_local(page_name, source)
        print("complete")
        repo.git.add(data_path)
        repo.index.commit("こんにちは！牛")
        repo.remote(name='origin').push()
    except ValueError:
        print(f"ソース名「 {page_name} 」を取得できませんでした")
