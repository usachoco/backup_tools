import os
import re

# - は詰めて良いが + は１行開けたいので別処理が必要
regex_args = [
    [r'[ \t]+\n', r'\n'],               # strip()
    [r'\[#([^\]]+)\]', r'&aname(\1)'],  # anchor
    [r'~\n#style', r'\n#style'],        # #style
    [r'~\n#pre', r'\n#pre'],        # #pre
    [r'(.)([~\n])+\-', r'\1\n-'],       # - の処理
    [r'(\n\-.+?)(~\n~)+', r'\1'],
    #[r'(.~\n~\n)\+', r'\1\n+'],         # + の処理
    #[r'(\|[\n]*[}]+\n.*?)~\n\n\+', r'\1~\n+'], #
    [r'(\n\+[^\|\+]+?)(~\n~)+', r'\1~\n~\n'], # + 処理2
    [r'\n\n ', r'\n \n '], # 空の pre 処理
    [r'//.*?\n', r''],   # コメント削除
    [r'([^\n\|\}\)\]~])\n([^\n\+\-\|#&])', r'\1~\n\2'],
]

# フォルダのパスを指定
script_dir = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(script_dir, 'wayback')
out_folder_path = os.path.join(folder_path, 'replace')
folder_path = os.path.join(folder_path, 'origin')


# ファイル内のテキストを置換する
def replace_in_file(file_path=r"C:\github\usachoco\backup_tools\origin.txt", out_file_path=r"C:\github\usachoco\backup_tools\new.txt"):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    for pattern, replacement in regex_args:
        r = re.compile(pattern, re.DOTALL)
        #r = re.compile(pattern)
        content = r.sub(replacement, content)
        #content = re.sub(pattern, replacement, content, re.DOTALL)    
    with open(out_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

"""
# フォルダ内のすべてのファイルを再帰的に処理
for foldername, _, filenames in os.walk(folder_path):
    for filename in filenames:
        file_path = os.path.join(foldername, filename)
        out_file_path = os.path.join(out_folder_path, filename)
        replace_in_file(file_path, out_file_path)
"""

if __name__ == "__main__":
    replace_in_file()