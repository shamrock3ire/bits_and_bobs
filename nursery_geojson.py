#!-- coding:utf-8 --
import csv
import json
import codecs
import os
import sys
from collections import OrderedDict
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
## 使い方 ##
# 保育園情報を整理した nurseryFacilities.csv　を　任意のフォルダに保存する
# 注意!! 列名は1行目に入力してくださいませ
# 注意!! X座標(経度)：1列目 Y座標(緯度)：2列目　にすること(あとでどこでも認識するように直します...)

# linux/Mac/Windows:
# 
# 1) 任意の場所にcsv2pmmap.py" (このファイル)を置く
# 2) terminal/コマンドプロンプト で　カレントディレクトリを1)の場所に変更
# cd /yourpath
# 3) 以下のコマンドを入力し実行する
# python csv2pmmap.py
# 4) ファイル指定のダイアログボックスが表示されるので 入力CSVを指定する
# 5) ファイル保存先指定のダイアログボックスが表示されるので　出力geojsonファイルを指定する

## 使い方おわり ##

# ファイルの保存場所の絶対パスを取得
absp = os.path.dirname(os.path.abspath(sys.argv[0]))
# s: ファイル指定ダイアログボックスの表示
csv_filename = askopenfilename(filetypes = [('CSV File', ('.csv'))],initialdir = absp)

# CSVファイルのencodeing 調査関数
def conv_encoding(data):
    lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
            'shift_jis', 'shift_jis_2004','shift_jisx0213',
            'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3',
            'iso2022_jp_ext','latin_1', 'ascii')
    encode = None
    for encoding in lookup:
        try:
            data = data.decode(encoding)
            encode = encoding
            break
        except:
            pass
    if isinstance(data, unicode):
        return data,encode
    else:
        raise LookupError

##ファイル読込とencodeingの調査##
fp = open(csv_filename,'r')
str_en,encoding = None,None
try:
    str_en,encoding = conv_encoding(fp.read())
finally:
    print encoding
    fp.close()
##encodeing 調査　ここまで##

## csv2geojson 変換処理本体 ##

f=open(csv_filename, 'r')
reader = csv.reader(f) #
# 2次元のリスト形式にする
# 空のリスト用意(保育園リスト)
list_n = []
for row in reader:
    # 空のリスト(各保育園の情報要素を格納)
    list_e = []
    for i in range(0,len(row)):
        # 未入力の要素にNone(json.dump後にはnullとなる)を埋めておく
        if row[i] == "":
            list_e.append(None)
        else:
            #listの要素をdecodeする
            list_e.append(row[i].decode(encoding))
    list_n.append(list_e)

print str(len(list_n)) + ' Nersery has been registered'

# かっちょわるいが各種パーツを用意しておく(unicode)

basal_obj = u'''{"type":"FeatureCollection",
            "crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features":[\n'''
hd_obj = u'{"type":"Feature","properties":'
jnt_obj = u',"geometry":{"type":"Point","coordinates":'
tail_obj = u'}},\n'
footer_obj = u']}'
 
# geojson作成ブロック #
countlist = 0
jsrow = u''
for row_n in list_n:
    countlist = countlist + 1
    if countlist == 1:
        # 最初の行をjsonのkeyとして抽出
        keylist = row_n
        # 投影法などの情報部分
        jsrow = basal_obj
    else:
        # dictionary に変換した後 　json　にダンプ
        # OrderedDict moduleでCSVの列順をそのまま保持
        att_obj = json.dumps(OrderedDict(zip(keylist,row_n)),ensure_ascii=False)
        # 緯度経度の抽出
        # 要素の型変換(str→float)
        cord_obj = map(float,row_n[0:2])
        jsrow = jsrow + hd_obj + att_obj + jnt_obj + str(cord_obj) + tail_obj
# 整形
jsrow = jsrow[0:-2] + footer_obj
# チェックのためプリント
print jsrow
# geojson　ファイル名の指定
savepath = os.path.dirname(csv_filename)
# s:ファイル保存先ダイアログボックスの表示
json_filename = asksaveasfilename(filetypes = [('geojson File', ('.geojson'))],initialdir = savepath, initialfile = "NurseryFacility.geojson")
# utf-8でエンコードされた空のファイルを開く
jsonf = codecs.open(json_filename,'w','utf-8')
# 保育園情報の書き込み
jsonf.write(jsrow)
jsonf.close()
f.close()

print "finish !!"