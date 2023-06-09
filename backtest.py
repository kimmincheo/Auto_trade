from asyncore import dispatcher
from hashlib import blake2b
from itertools import count
from pickle import NONE
from re import I
import time
import pyupbit
import datetime
import jwt   # PyJWT 
import uuid
import math
import os 
import pandas as pd
from pytz import timezone
import numpy as np
import telegram
import asyncio
#import schedule
import sys
access = "RZF9BxUayHxjtU7PrL0tnxMEu5IRQtOlpuk6bD7n"
secret = "ynGxpZUPMh2prdcPebA8HjwHCPb7M8qQWki7HSkj"
server_url = "https://api.upbit.com"
#시가(open), 고가(high), 저가(low), 종가(close), 거래량(volume) 거래대금(value)




def get_target_price(ticker):
    """현재가 전"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=3) # 1분당 캔들조회
    return df.iloc[1]['open']

def get_nowtarget_price(ticker):
    """현재가"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2) # 1분당 캔들조회
    return df.iloc[0]['open']

def get_target_value(ticker):
    """거래대금"""
    df = pyupbit.get_ohlcv(ticker,interval="day",count=1) #24시간 거래대금
    return df.iloc[0]['value']

def get_target_volume(ticker):
    """거래량 """ 
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2) # 1분당 캔들조회

    if df.iloc[0]['volume']!=None:
        return df.iloc[0]['volume']
def get_target_now_volume(ticker):
    """현재 거래량 """ 
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=3) # 1분당 캔들조회

    if df.iloc[1]['volume']!=None:
        return df.iloc[1]['volume']

def get_target_low(ticker):
    """저가 """
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=3) # 저가

    return df.iloc[1]['low']

def get_dispersion():
    """내 자산"""

    krw = upbit.get_balance() #보유중인 현금

    
    return krw

def get_target_buy(ticker):
    """매수"""
    
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2) # 저가

    compare = df.iloc[0]['low']
    eadown = 2

    if compare < 100000 and compare >= 10000: #1만이상 10만 미만
        return compare - 10 * eadown 

    elif compare >= 1000 and compare < 10000:
        return compare - 5 * eadown # 1천 이상 1만 미만

    elif compare >= 100 and compare < 1000:
        return compare - 1 * eadown  # 100이상 1천미만
    
    elif compare >= 10 and compare < 100:
        return compare - 0.1 * eadown  # 10 이상 100 미만
    
    elif compare >=1 and compare < 10:
        return compare - 0.01 * eadown  # 1원 이상 10 미만   

def get_target_sell(ticker):
    """매도하는 코ㅗㅗㅗ드"""
    price = 0.0052

    balan = upbit.get_balance_t('%s'%ticker)  # 거래 코인 갯수 float
    avg = upbit.get_avg_buy_price('%s'%ticker)# 거래 평균가
    compare = round((avg * price) + avg,2) 

    if compare >= 1000000:
        upbit.sell_limit_order(
             ("%s" % ticker),round((avg * price + avg)-3), balan) # 지정가 매도코드 100만이상

    elif compare >= 100000 and compare < 1000000:
        upbit.sell_limit_order(
             ("%s" % ticker),round((avg * price + avg),-2), balan) # 지정가 매도코드 10만원 이상 100만 미만

    elif compare >= 1000 and compare < 100000:
        upbit.sell_limit_order(
             ("%s" % ticker),round((avg * price + avg),-1), balan)  # 지정가 매도코드 1천원 이상 10만 미만
    
    elif compare >= 100 and compare < 1000:
        upbit.sell_limit_order(
            ("%s" % ticker),round((avg * price + avg),0), balan)  # 지정가 매도코드 100원 이상 1천원 미만
    
    elif compare >=10 and compare < 100:
        upbit.sell_limit_order(
            ("%s" % ticker), round((avg * price + avg),1), balan)  # 지정가 매도코드 10원이상 100원 미만
   
    elif compare >=1 and compare < 10:
        upbit.sell_limit_order(
            ("%s" % ticker), round((avg * price + avg),2), balan)  # 지정가 매도코드 1원이상 10원미만

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("로그인 확인")
max = 0
KrCoin = pyupbit.get_tickers(fiat="KRW") #원화거래 코인 조회
limit = len(KrCoin)-1 # 조회된 원화거래코인 최대개수확인  
kn = []

while True:
    try: 
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        #손절 ask
        bal = upbit.get_balances()
        for b in bal:
            ticker = (b['currency']) #거래 코인명
            buy_price = float ((b['avg_buy_price'])) # 코인 매수금액

            if ticker!='KRW'and ticker!='GTO'and ticker!='QTCON' and ticker!='VTHO' and ticker!='APENFT':
                    time.sleep(0.1)
                    get_target_sell('KRW-%s'%ticker)    
                    cancel = upbit.get_order('KRW-%s'%ticker) #uuid 수집
                    buy_ticker = float (get_nowtarget_price('KRW-%s'%ticker))
                    price_avg = (buy_ticker - buy_price)/buy_price*100

                    if price_avg <= -1.2:
                        for ca in cancel:
                            
                            upbit.cancel_order(ca['uuid'])
                            time.sleep(0.2)
                            balanc = upbit.get_balance(ticker)
                            upbit.sell_market_order("KRW-%s" %ticker, balanc)
                            print("KRW-%s 2퍼손절" %ticker)
        for k in kn:
            b_cancel = upbit.get_order(k)
            coin_name = k
            for bca in b_cancel:
                does_buy = bca['side']
                if does_buy == 'bid':
                    buy_time = (bca ['created_at'])
                    limittime = datetime.datetime.strptime(buy_time,'%Y-%m-%dT%H:%M:%S%z')
                    limitseconds = now - limittime

                    if limitseconds.seconds >= 180:

                            upbit.cancel_order(bca['uuid'])
                            time.sleep(0.2)
                            print("%s 3분 경과 매수취소"%k)
                            kn.remove(coin_name)
                else:
                    kn.remove(coin_name)




        for n in bal:
            if ('KRW-%s' % n['currency']) == KrCoin[max]: # 이미 가지고 있는 코인인가?
                if max == limit:
                    max = 0
                else:
                    max += 1
                continue
        for knn in kn:
            if KrCoin[max] == knn:
                if max == limit:
                    max =0
                else:
                    max += 1
                continue
        #매수 부분
        if get_dispersion() > 5000 and get_nowtarget_price(KrCoin[max]) < 100000:
            if get_target_value(KrCoin[max]) >= 10000000000: #거래대금이 10,000백만 이상인가
                buy_price = get_target_price(KrCoin[max])
                buy_now_price = get_nowtarget_price(KrCoin[max])
                buy_low = get_target_buy(KrCoin[max])
                while True:
                    try:
                        df = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=16)# 1분당 캔들조회
                        df1 = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=106) # 1분당 캔들조회
                        ma60 = round(df1['close'].rolling(window=100 ,min_periods=1).mean(),1)#60분 거래평균
                        ma5 = round(df['close'].rolling(window=12 ,min_periods=1).mean(),1) #5분 거래평균
                        break
                    except Exception as e:
                        continue
                    
                buy_avg_per = (buy_price - ma60.iloc[-2])/buy_price*100
                buy_avg_per1 = (buy_now_price - ma5.iloc[-1])/buy_now_price*100
                    
                #골든크로스 매수 
                if  buy_avg_per < -1.6 and get_target_now_volume(KrCoin[max]) > 1000:#매수
                    upbit.buy_limit_order(KrCoin[max],buy_low,round(100000/buy_low),8)
                    kn.append(KrCoin[max])
                    async def main():
                        CHAT_ID = '6071034278'
                        TOKEN = '6240669790:AAEU5GJ7qa_kELgoC3mqlIk_AP0sTZN9fHA'
                        bot = telegram.Bot(token=TOKEN)
                        await bot.sendMessage(chat_id=CHAT_ID, text="%s 매수중"%KrCoin[max])
                    asyncio.run(main())
                    time.sleep(1)
                #매수
                # if  buy_avg_per1 >= 0.7 and get_target_now_volume(KrCoin[max]) > 1000:#매수
                #     upbit.buy_limit_order(KrCoin[max],buy_low,round(9000/buy_low),8)
                #     kn.append(KrCoin[max])
                #     async def main():
                #         CHAT_ID = '6071034278'
                #         TOKEN = '6240669790:AAEU5GJ7qa_kELgoC3mqlIk_AP0sTZN9fHA'
                #         bot = telegram.Bot(token=TOKEN)
                #         await bot.sendMessage(chat_id=CHAT_ID, text="%s 매수중"%KrCoin[max])
                #     asyncio.run(main())
                #     time.sleep(1)
                    

                    

                                              
        time.sleep(0.2)
        if max ==limit:
            max = 0
        else:
            max += 1
    
    except Exception as e:
        time.sleep(1)