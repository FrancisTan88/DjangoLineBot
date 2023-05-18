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
    y = f'近5年平均現金殖利率: {yields}'

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

    return basic_info + "\n\n" + pb + '\n' + str(y) +'\n'+str(pe) + '\n' + percent
