from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

from services.strategy_models import BollingerModel, KdModel, RsiModel, SMAModel, MACDModel
from services.info_n_financials import scrawl_info
from services.scrawl_news_final import news
import datetime as dt


CHANNEL_ACCESS_TOKEN = "WFGOhWW581sHWFBKDQVjb+X3HXDjI3VITfUCp8hnR6ldAraA9FpTtV0U0vXBFf3i0k2nxJXqvRwwbWoGGarGk+iZWBOMZCiE5UbCTWVlxGyRTpnXzHk8aqIsTe1YnrgBAnS5rRFNY6Y2CpAJR1ZWUQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "c6586ddc26e80da8ee220f7945ae73aa"
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(CHANNEL_SECRET)

res_strategy1 = "(1)使用布林通道策略請輸入:\n布林通道 <股票代號> <測試天數>\n<初始資本> <短天線> <長天線>\n"
res_strategy2 = "(2)使用KD策略請輸入:\nKD <股票代號> <測試天數> <初始資本> <短天線> <長天線>\n"
res_strategy3 = "(3)使用RSI策略請輸入:\nRSI <股票代號> <測試天數> <初始資本> <最小短天線> <最大短天線>\n<最小長天線> <最大長天線>\n"
res_strategy4 = "(4)使用SMA策略請輸入:\nSMA <股票代號> <測試天數> <初始資本> <最小短天線> <最大短天線>\n<最小長天線> <最大長天線>\n"
res_strategy5 = "(5)使用MACD策略請輸入:\nMACD <股票代號> <測試天數> <初始資本> <最小短天線> <最大短天線>\n<最小長天線> <最大長天線>\n\n(e.g. 布林通道 2330.TW 1000 1000000 6 12)"


RES_TS = f"{res_strategy1}\n{res_strategy2}\n{res_strategy3}\n{res_strategy4}\n{res_strategy5}"


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if isinstance(event.message, TextMessage):
                    mtext = event.message.text

                    # service1
                    if mtext == "交易策略":
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=RES_TS))
                    elif "布林通道" in mtext:
                        strategy, stock_id, days, capital, short, long = \
                                mtext.split(" ")
                        # process the data types
                        days = int(days)
                        capital = int(capital)
                        short = int(short)
                        long = int(long)
                        end_day = dt.datetime.today()
                        # call the model
                        boll = BollingerModel(stock_id, end_day, days, capital)
                        best_window, best_dr, best_sr = boll.optimizer(short, long)
                        best_dr = round(100 * best_dr, 4)
                        best_sr = round(100 * best_sr, 4)
                        res_msg = f"最佳天線: {best_window}\n買進持有策略: {best_dr}%\n布林通道策略: {best_sr}%"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))
                    elif "KD" in mtext:
                        strategy, stock_id, days, capital, short, long = \
                                mtext.split(" ")
                        # process the data types
                        days = int(days)
                        capital = int(capital)
                        short = int(short)
                        long = int(long)
                        end_day = dt.datetime.today()
                        k_value = 50
                        # call the model
                        kd = KdModel(stock_id, end_day, days, capital, k_value)
                        best_window, best_dr, best_sr = kd.optimizer(short, long)
                        best_dr = round(100 * best_dr, 4)
                        best_sr = round(100 * best_sr, 4)
                        res_msg = f"最佳天線: {best_window}\n買進持有策略: {best_dr}%\nKD策略: {best_sr}%"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))
                    elif "RSI" in mtext:
                        strategy, stock_id, days, capital, min_short, max_short, min_long, max_long = \
                                mtext.split(" ")
                        # process the data types
                        days = int(days)
                        capital = int(capital)
                        min_short = int(min_short)
                        max_short = int(max_short)
                        min_long = int(min_long)
                        max_long = int(max_long)
                        end_day = dt.datetime.today()
                        # call the model
                        rsi = RsiModel(stock_id, end_day, days, capital)
                        best_short, best_long, best_dr, best_sr = rsi.optimizer(min_short, max_short, min_long, max_long)
                        best_dr = round(100 * best_dr, 4)
                        best_sr = round(100 * best_sr, 4)
                        res_msg = f"最佳短天線: {best_short}\n最佳長天線: {best_long}\n買進持有策略: {best_dr}%\nRSI策略: {best_sr}%"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))
                    elif "SMA" in mtext:
                        strategy, stock_id, days, capital, min_short, max_short, min_long, max_long = \
                                mtext.split(" ")
                        # process the data types
                        days = int(days)
                        capital = int(capital)
                        min_short = int(min_short)
                        max_short = int(max_short)
                        min_long = int(min_long)
                        max_long = int(max_long)
                        end_day = dt.datetime.today()
                        # call the model
                        sma = SMAModel(stock_id, end_day, days, capital)
                        best_short, best_long, best_dr, best_sr = sma.optimizer(min_short, max_short, min_long, max_long)
                        best_dr = round(100 * best_dr, 4)
                        best_sr = round(100 * best_sr, 4)
                        res_msg = f"最佳短天線: {best_short}\n最佳長天線: {best_long}\n買進持有策略: {best_dr}%\nSMA策略: {best_sr}%"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))
                    elif "MACD" in mtext:
                        strategy, stock_id, days, capital, min_short, max_short, min_long, max_long = \
                                mtext.split(" ")
                        # process the data types
                        days = int(days)
                        capital = int(capital)
                        min_short = int(min_short)
                        max_short = int(max_short)
                        min_long = int(min_long)
                        max_long = int(max_long)
                        end_day = dt.datetime.today()
                        # call the model
                        macd = MACDModel(stock_id, end_day, days, capital)
                        best_short, best_long, best_dr, best_sr = macd.optimizer(min_short, max_short, min_long, max_long)
                        best_dr = round(100 * best_dr, 4)
                        best_sr = round(100 * best_sr, 4)
                        res_msg = f"最佳短天線: {best_short}\n最佳長天線: {best_long}\n買進持有策略: {best_dr}%\nMACD策略: {best_sr}%"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))

                    # service2
                    elif mtext == "基本面":
                        res_msg = "(1)欲查詢基本資訊請輸入:\n  <股票代號> <基本資訊>\n(2)欲查詢新聞請輸入:\n  <股票代號> <新聞>\n(e.g. 2330 基本資訊)"
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=res_msg))
                    elif "基本資訊" in mtext:
                        stock_id = str(mtext.split(" ")[0])
                        basic_info = scrawl_info(stock_id)
                        # if len(basic_info) > 279:
                        #     basic_info = basic_info[:279]
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=basic_info))
                    elif "新聞" in mtext:
                        stock_id = str(mtext.split(" ")[0])
                        ns = str(news(stock_id))
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=ns))
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="(1)欲查詢公司基本資訊請輸入: 基本面\n(2)欲使用交易策略請輸入: 交易策略"))
                        
        return HttpResponse()

    else:
        return HttpResponseBadRequest()
