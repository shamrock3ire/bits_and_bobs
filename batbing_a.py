#!-- coding:utf-8 --
import csv
import urllib
import requests

# 以下のo-tomoxさんのBing Search API の python ラッパーを利用させてもらいました。
#　https://gist.github.com/o-tomox/6649758
# 標準ライブラリ以外では requests が必要です。
# requests
# https://pypi.python.org/pypi/requests
# pip などをつかってインストールしておいてください
# pip については以下を参照してください
# http://www.lifewithpython.com/2012/11/Python-package-setuptools-pip.html
# あとは変数を適当にいれて実行してください
# 入力CSVファイルが格納されているフォルダに
# ファイル名の末尾に _out　がついたCSVファイルが出力されます

####入力変数####
# 入力CSVファイルの指定
# 文字コード：utf-8
# 列番号は 1列目 = 0
csvf = "/home/sham3/data/nursery/facilities_20141030.csv"
n_name = 1 # 保育所名の列番号
n_type = 0 # 施設の種類（ex. 認可保育所,幼稚園 etc..）の列番号
n_adr = 3 # 自治体名の列番号（ex. 札幌市, 横浜市）
n_top = 3 # 上位何位までを検索するかを指定
# bing search api　キーの指定 (5000クエリ/月まで)
api_key = 'BkUO6J8XreuDrqoFuwhrgj3hvs7cU9nV/YrERZKWP3k'
##############

def web_search(query, k, keys=["Url"], skip=0):
    """
        keysには'ID','Title','Description','DisplayUrl','Url'が入りうる
    """
    # 基本になるURL
    url = 'https://api.datamarket.azure.com/Bing/Search/Web?'
    # 一回で返ってくる最大数
    max_num = 50
    # 各種パラメータ
    params = {
        "Query": "'{0}'".format(query),
        "Market": "'ja-JP'"
    }

    # フォーマットはjsonで受け取る
    request_url = url + urllib.urlencode(params) + "&$format=json" 
    # 結果を格納する配列
    results = [] 
    # 最大数でAPIをたたく繰り返す回数
    repeat = k / max_num
    # 残り
    remainder = k % max_num
    # 最大数でAPIをたたくのを繰り返す    
    for i in xrange(repeat):
        result = _search(request_url, max_num, skip, keys)
        results.extend(result)
        skip += max_num
    # 残り
    if remainder:
        result = _search(request_url, remainder, skip, keys)
        results.extend(result)
    # 結果を返す
    return results

def _search(request_url, top, skip, keys):
    # APIをたたくための最終的なURL
    final_url = "{0}&$top={1}&$skip={2}".format(request_url, top, skip)
    # レスポンス(json化)
    response = requests.get(final_url, 
                            auth=(api_key, api_key), 
                            headers={'User-Agent': 'My API Robot'})
    
    response = response.json()

    # 結果を格納する配列
    results = []
    # 帰ってきたもののうち指定された情報を取得する
    for item in response["d"]["results"]:
        result = {}
        for key in keys:
            result[key] = item[key].encode("utf-8")
        results.append(result)

    # 結果を返す
    return results

###処理本体####

# CSVファイルの読み込み
cobj = csv.reader(open(csvf, "rb"))
# 出力用CSVファイルの作成（同じ名前のファイル名は上書きされる）
f = open(csvf[:-4] + "_out.csv", 'wb')
csvWriter = csv.writer(f)

# 施設名 + 自治体名称 を　bing.web_searchになげて top3 のURLをjsonで返しCSVに書き込む処理
prgr = 0
for i in cobj:
    list_ns = []
    if str(i[n_type])=="幼稚園":
        # 幼稚園は名称のみ入力されているので　自治体名＋施設名 に　"幼稚園"を追加して検索  
        results = web_search(str(i[n_adr]) + "　" + str(i[n_name]) + "　幼稚園", n_top, ["Url"])
    else:
        # 幼稚園以外は　自治体名　＋　施設名　で検索
        results = web_search(str(i[n_adr]) + "　" + str(i[n_name]), n_top, ["Url"])
    #　施設名をリストの先頭に追加
    list_ns.append(str(i[n_name]))    
    for result in results:
        #　検索結果のjson(dict obj)からvalue のみ抽出
        list_ns.append(result.values()[0])
    csvWriter.writerow(list_ns)
    prgr = prgr + 1
    # progress barのかわりに検索終了施設数をterminalに出力
    print str(prgr) + " 施設終了"
# CSVを保存して閉じる
f.close()
print "finished"
