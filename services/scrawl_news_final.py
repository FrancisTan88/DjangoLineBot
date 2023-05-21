
import requests
from lxml import etree
import pandas as pd
import urllib.request as req
import json


def news(stock):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',}

    # 載入鉅亨網搜尋結果頁面
    search_url = "https://api.cnyes.com/media/api/v1/search?q="+ stock  # 鉅亨網網址

    request = req.Request(search_url, headers = headers)

    with req.urlopen(request) as response:
        data = response.read().decode('utf-8')

    data = json.loads(data)

    content = ''
    for i in range(10):
        news_id = data['items']['data'][i]['newsId']
        url = 'https://news.cnyes.com/news/id/'+ str(news_id)  # 新聞連結

        title = data['items']['data'][i]['title']  # 新聞標題
        title = title.replace('<mark>', '')  # 取代掉字體顏色的標記
        title = title.replace('</mark>', '')

        res = requests.get(url, headers)
        html = etree.HTML(res.content)
        posttime = html.xpath('//*[@id="content"]/div/div/div[2]/main/div[2]/div[2]/time/text()')[0] 
        posttime = posttime.split(' ')
        date = posttime[0]  # 新聞日期

        content += "{} {}\n{}\n".format(date, title, url)
    return content

# stock = input()  # 輸入要搜尋的股票
# tmp = news(stock)
# print(tmp)
