import json

with open('Data\\songerInfo.json', 'r', encoding='utf-8') as f:
    content=json.load(f)
with open('songerInfo.txt', 'w',encoding='utf-8') as f:
    for info_dict in content:
        for key, value in info_dict.items():
            f.write(key + ' : ' + value + '\n')
            f.write('===='*30+'\n')