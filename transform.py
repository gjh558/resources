# -*- encoding: utf-8 -*-

import json
import sys

class Trans:
    def __init__(self, pos, trans):
        self.pos = pos
        self.trans = trans

class Sentence:
    def __init__(self, en, cn):
        self.en = en
        self.cn = cn

class Word:
    def __init__(self, headWord, usphone, ukphone, trans, sentence):
        self.name = headWord.lower()
        self.usphone = usphone
        self.ukphone = ukphone
        self.trans = trans
        self.sentence = sentence

def replaceFran(str):
    fr_en = [['é', 'e'], ['ê', 'e'], ['è', 'e'], ['ë', 'e'], ['à', 'a'], ['â', 'a'], ['ç', 'c'], ['î', 'i'], ['ï', 'i'],
             ['ô', 'o'], ['ù', 'u'], ['û', 'u'], ['ü', 'u'], ['ÿ', 'y']
             ]
    for i in fr_en:
        str = str.replace(i[0], i[1])
    return str

def transform(path):
    output = []
    with open(path, mode="r", encoding="utf-8") as f:
        s_error, p_error = 0, 0
        for line in f:
            text = replaceFran(line.strip())
            obj = json.loads(text)
            word = obj['content']['word']['wordHead']
            src = obj['content']['word']['content']
            t = []
            src_trans = src['trans']
            for tr in src_trans:
                t.append(Trans(tr['pos'], tr['tranCn']))
            if 'sentence' not in src.keys():
                s_error+=1
            if 'usphone' not in src.keys() or 'ukphone' not in src.keys():
                p_error+=1

            s = Sentence(src['sentence']['sentences'][0]['sContent'], src['sentence']['sentences'][0]['sCn']) if 'sentence' in src.keys() and len(src['sentence']['sentences']) > 0 else Sentence('', '')
            usphone, ukphone = '', ''
            if 'usphone' in src.keys():
                usphse = src['usphone']
            if 'ukphone' in src.keys():
                ukphse = src['ukphone']

            w = Word(word, usphone, ukphone, t, s)
            output.append(w)

    print(s_error, p_error)
    return output

def sorter(e):
    return e.name

if len(sys.argv) != 2:
    print('wrong args')
    exit()

res = transform(sys.argv[1])
res.sort(key=sorter)

f = open('words.js', 'w+')
f.write(json.dumps(res, default=vars))
f.close()
