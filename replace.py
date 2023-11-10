import os
import re

regex_args = [
    [r'\[#.+\]', ''],   # アンカー削除
    [r'#ref\([^\)]+\)', ''],   # 画像削除
    [r'&ref\([^\)]+\);', ''],   # 画像削除
    [r'\[\[([^>]+)[^\]]+\]\]', r'\1'],    # リンク削除
    [r'#contents', r'#contents(fromhere=true)'],    # tocの修正
    [r'([^\n])~\n([|*#+\-])', r'\1~\n~\n\n\2'],   # 行末に改行記号、かつ次の行に特殊記号がある場合、次の行に改行記号を挿入し、さらに特殊記号の前に空白行を開ける
    [r'\n~\n([*+\-])', r'\n~\n\n\1'],    # 行頭に改行記号、かつ次の行に特殊記号がある場合、改行記号と特殊記号の間に空白行を開ける
    [r'\|\n~\n\n', '|\n~\n'], # テーブル直後の行に改行記号、その次に空白行がある場合、空白行を削除する
    [r'~\n#style', r'~\n\n#style'],   # styleプラグイン対応
    [r'\n~\n~', r'\n~'], # 置換後の2行連続~~を~にまとめる
]

# フォルダのパスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'wayback')
out_folder_path = os.path.join(folder_path, 'replace')
folder_path = os.path.join(folder_path, 'origin')


# ファイル内のテキストを置換する
def replace_in_file(file_path, out_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    for pattern, replacement in regex_args:
        content = re.sub(pattern, replacement, content)    
    with open(out_file_path, 'w', encoding='utf-8') as file:
        file.write(content)


# フォルダ内のすべてのファイルを再帰的に処理
for foldername, _, filenames in os.walk(folder_path):
    for filename in filenames:
        file_path = os.path.join(foldername, filename)
        out_file_path = os.path.join(out_folder_path, filename)
        replace_in_file(file_path, out_file_path)
