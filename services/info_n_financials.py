import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import date


def scrawl_info(ticker):

    stock_id = ticker


    '''以下是給「公司基本資訊」'''
    # 找到連結
    url = f"https://tw.stock.yahoo.com/quote/{stock_id}/profile"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    root = BeautifulSoup(res.text, 'html.parser')
    # 資料在div下面的這個class裡面，接下來我去印出來，就會出現所有這個class的東西，再一個一個去找我要的資料
    divs = root.find_all("div", class_= "Py(8px) Pstart(12px) Bxz(bb)")
    company_name = f"公司名稱: {divs[0].string}"
    industry = f"產業: {divs[8].string}"
    tmp = divs[22].string.replace('\r', '').replace('\n', '')
    items = f"經營項目: {tmp}"
    basic_info =  f"{company_name}\n{industry}\n{items}"
    # info = pd.DataFrame({
    #     '公司名稱':divs[0].string,
    #     '產業':divs[8].string,
    #     '經營項目':divs[22].string.replace('\r', '').replace('\n', '')
    # },index=[stock_id])
    
    

    '''這段在印出最新價格'''
    url = f"https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym={stock_id}&v=1&callback=jQuery111302872649618000682_1649814120914&_=1649814120915"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url, headers=headers)
    # 最新價格
    current = [l for l in res.text.split('{') if len(l)>=60][-1]
    current = current.replace('"','').split(',')
    # 現在日期
    date = date.today().strftime('%Y-%m-%d')
    # 輸出最新價格 
    price = f"最新價格({date}): {float(re.search(':.*', current[4]).group()[1:])}"
    

    '''印出EPS'''
    # 要在network 輸入想找到的數字，然後去看看哪個連結是正確的，找到正確連結，看responce和preview，再抓出url
    url = f"https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.revenues;includedFields=priceAssessment;period=quarterSum4;priceAssessmentPeriod=quarter;symbol={stock_id}.TW?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseNewQuoteTabColor%2CenableSubscriptionPromotion&intl=tw&lang=zh-Hant-TW&partner=none&prid=580k25di57d3m&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1825&returnMeta=true"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    # 因為這個連結抓出來的東西是json，所以利用下面的方是找到我要的東西
    jd = res.json()["data"]
    # 一層一層抓，發現我的東西在 data>>result>>revenues裡面，然後goal是一個list
    goal = jd["data"]['result']['revenues']
    # 因為我每次要回傳的，一定會是最新的那一個數字，最新的一定會被放在list中的最前面，所以直接找[0]
    newest = goal[0]
    # 因為newest 是一個dict，所以利用這樣的方式，找到我最後要的那個數字
    acc4q = newest['epsAcc4Q']
    eps = f'近四季每股盈餘 : {acc4q}'


    '''印出殖利率'''
    url = f"https://tw.stock.yahoo.com/quote/{stock_id}/dividend"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    root = BeautifulSoup(res.text, 'html.parser')
    # 因為在原始碼中，近5年平均現金殖利率是在'span'裡面，所以我把所有span下面的class="Fw(b)"都抓出來
    spans = root.find_all("span", class_= "Fw(b)")
    # 全部抓出來之後，發現我要的資訊會出現在最後一個，所以我直接挑出最後一個，string就是去抓到純文字的部分
    yields = spans[-1].string
    # 印出 近 5 年平均現金殖利率 2.69%
    y = f'近 5 年平均現金殖利率 : {yields}'

    '''印出PE ratio'''
    url = f"https://tw.stock.yahoo.com/quote/{stock_id}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    root = BeautifulSoup(res.text, 'html.parser')
    # 因為在原始碼中，本益比是在'span'裡面，所以我把所有span下面的class="Fz(16px) C($c-link-text) Mb(4px)"都抓出來
    spans = root.find_all("span", class_= "Fz(16px) C($c-link-text) Mb(4px)")
    # 全部抓出來之後，發現我要的資訊會出現在最後一個，所以我直接挑出最後一個，string就是去抓到純文字的部分
    pers = spans[-1].string
    ## 因為同時會有這個股票的本益比跟同業平均本益比，我取前面那個數字就好
    # per = pers.split("(")[0].strip()
    pe = f'本益比(同業平均): {pers}'


    '''印出PBratio'''
    url = f"https://jsjustweb.jihsun.com.tw/z/zc/zca/zca_{stock_id}.djhtm"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    root = BeautifulSoup(res.text, 'html.parser')
    # 網頁中營收比重被放在"td", class_= "t3n1"所以藉由這個方式把所有的抓出來
    tds = root.find_all("td", class_= "t3n1")
    # 找到股價淨值比，在第34個位置
    pbratio = tds[34].string
    # 印出來
    pb = f'股價淨值比: {pbratio}'


    '''印出業務佔比'''
    url = f"https://jsjustweb.jihsun.com.tw/z/zc/zca/zca_{stock_id}.djhtm"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/111.25 (KHTML, like Gecko) Chrome/99.0.2345.81 Safari/123.36'}
    res = requests.get(url,headers=headers)
    root = BeautifulSoup(res.text, 'html.parser')
    # 網頁中營收比重被放在"td", class_= "t3t1", colspan="7"當中，所以藉由這個方式把所有的抓出來
    tds = root.find_all("td", class_= "t3t1", colspan="7")
    # 然後營收比重是這所有的當中的第一個
    percentages = tds[0].string
    # 印出來
    percent = f'營收比重: {percentages}'


    return basic_info
    # return str(basic_info)+'\n'+str(price)+'\n'+str(eps)+'\n'+str(y)+'\n'+str(pe)+'\n'+str(pb)+'\n'+str(percent)
