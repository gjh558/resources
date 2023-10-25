# -*- encoding: utf-8 -*-

import json
import sys
import zipfile
import gzip
import requests
import xml.etree.ElementTree as ET

class Trans:
    def __init__(self, pos, trans):
        self.pos = pos
        self.ex = trans

class Sentence:
    def __init__(self, en, cn):
        self.en = en
        self.cn = cn

class Word:
    def __init__(self, headWord, phones, trans, sentence):
        self.n = headWord.lower()
        self.t = trans
        self.s = sentence
        self.p = phones

def replaceFran(str):
    fr_en = [['é', 'e'], ['ê', 'e'], ['è', 'e'], ['ë', 'e'], ['à', 'a'], ['â', 'a'], ['ç', 'c'], ['î', 'i'], ['ï', 'i'],
             ['ô', 'o'], ['ù', 'u'], ['û', 'u'], ['ü', 'u'], ['ÿ', 'y']
             ]
    for i in fr_en:
        str = str.replace(i[0], i[1])
    return str

def parseXML(strXML):
    root = ET.fromstring(strXML)
    keyTag = root.find('key')
    psTag = root.findall('ps')
    phones = [psTag[1].text, psTag[0].text]
    posTag = root.findall('pos')
    acceptationTag = root.findall('acceptation')
    trans = []
    for i in range(len(posTag)):
        trans.append(Trans(posTag[i].text, acceptationTag[i].text))
    sentTag = root.findall('sent')
    maxSentNum = min(len(sentTag), 2)
    sents = []
    for s in sentTag:
        sents.append(Sentence(s[0].text, s[1].text))

    wordObj = Word(keyTag.text, phones, trans, sents)
    print(json.dumps(wordObj, default=vars))

def queryWord(word):
    r = requests.get('https://dict-co.iciba.com/api/dictionary.php?key=C8DDDA9B1360645BA7C3888DF6F54702&w=' + word.lower())
    if r.status_code != 200:
        print("ERROR: failed to query: " + word)
        return None
    return parseXML(r.text)

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
                if 'pos' not in tr.keys() or 'tranCn' not in tr.keys():
                    continue
                t.append(Trans(tr['pos'], tr['tranCn']))

            sents = []
            if 'sentence' in src.keys():
                if 'sentences' in src['sentence'].keys():
                    for sent in src['sentence']['sentences']:
                        sents.append(Sentence(sent['sContent'], sent['sCn']))

            phones = []
            if 'usphone' in src.keys() and 'ukphone' in src.keys():
                phones.append(src['usphone'])
                phones.append(src['ukphone'])
            # validation
            if len(t) == 0 or len(sents) == 0 or len(phones) != 2:
                print('try to query: ' + word)
                res = queryWord(word)
                if res == None:
                    continue
                output.append(res)
            else:
                w = Word(word, phones, t, sents)
                output.append(w)

    return output

def sorter(e):
    return e.n

if len(sys.argv) != 2:
    print('wrong args')
    exit()

# unzip
zfile = zipfile.ZipFile(sys.argv[1] + '/word.zip','r')
if len(zfile.namelist()) != 1:
    print(sys.argv[1])
    exit()

for filename in zfile.namelist():
    data = zfile.read(filename)
    file = open(sys.argv[1] + '/word.txt', 'w+b')
    file.write(data)
    file.close()


res = transform(sys.argv[1] + '/word.txt')
res.sort(key=sorter)


with open(sys.argv[1] + '.gz', 'w+b') as f:
    f.write(gzip.compress(str.encode(json.dumps(res, default=vars))))

f.close()
