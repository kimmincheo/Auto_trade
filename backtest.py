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
import schedule
import sys
access = "RZF9BxUayHxjtU7PrL0tnxMEu5IRQtOlpuk6bD7n"
secret = "ynGxpZUPMh2prdcPebA8HjwHCPb7M8qQWki7HSkj"
server_url = "https://api.upbit.com"
#시가(open), 고가(high), 저가(low), 종가(close), 거래량(volume) 거래대금(value)




def get_target_price(ticker):
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
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1) # 1분당 캔들조회

    if df.iloc[0]['volume']!=None:
        return df.iloc[0]['volume']

def get_target_open(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1) # 1분당 캔들조회

    return df.iloc[0]['open']

def get_dispersion():
    """내 자산"""

    krw = upbit.get_balance() #보유중인 현금

    
    return krw
    

def get_target_sell(ticker):
    """매도하는 코ㅗㅗㅗ드"""
    price = 0.0075

    balan = upbit.get_balance_t('%s'%ticker)  # 거래 코인 갯수 float
    avg = upbit.get_avg_buy_price('%s'%ticker)# 거래 평균가
    compare = round((avg * price) + avg,2) 

    if compare >= 1000000:
        upbit.sell_limit_order(
             ("%s" % ticker),math.trunc((avg * price + avg)), balan) # 지정가 매도코드 100만이상

    elif compare >= 100000 and compare < 1000000:
        upbit.sell_limit_order(
             ("%s" % ticker),math.trunc((avg * price + avg)), balan) # 지정가 매도코드 10만원 이상 100만 미만

    elif compare >= 1000 and compare < 100000:
        upbit.sell_limit_order(
             ("%s" % ticker),math.trunc((avg * price + avg)), balan)  # 지정가 매도코드 1천원 이상 10만 미만
    
    elif compare >= 100 and compare < 1000:
        upbit.sell_limit_order(
            ("%s" % ticker),math.trunc((avg * price + avg)), balan)  # 지정가 매도코드 100원 이상 1천원 미만
    
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
while True:
    try: 
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        #손절 ask
        bal = upbit.get_balances()
        for b in bal:
            ticker = (b['currency']) #거래 코인명
            buy_price = (b['avg_buy_price']) # 코인 매수금액

            if ticker!='KRW'and ticker!='GTO'and ticker!='QTCON' and ticker!='VTHO' and ticker!='APENFT':
                    time.sleep(0.1)    
                    cancel = upbit.get_order('KRW-%s'%ticker)
                    price_avg = (get_target_price('KRW-%s'%ticker)-buy_price)/buy_price*100
                    if price_avg <= -2:
                        for ca in cancel:
                            
                            upbit.cancel_order(ca['uuid'])
                            time.sleep(0.2)
                            balanc = upbit.get_balance(ticker)
                            upbit.sell_market_order("KRW-%s" %ticker, balanc)
                            print("KRW-%s 2퍼손절" %ticker) 
        for n in bal:
            if ('KRW-%s' % n['currency']) == KrCoin[max] or 'KRW-OMG'== KrCoin[max] or 'KRW-SRM'== KrCoin[max] or 'KRW-XRP'== KrCoin[max]or'KRW-GLM'== KrCoin[max] or 'KRW-DOGE'== KrCoin[max]: # 이미 가지고 있는 코인인가?
                if max == limit:
                    max = 0
                else:
                    max += 1
                continue
        
        #매수 부분
        if get_dispersion() >= 7000 and get_target_price(KrCoin[max]) < 100000:
            if get_target_value(KrCoin[max]) >= 10000000000: #거래대금이 10,000백만 이상인가
                buy_price = get_target_price(KrCoin[max])
                while True:
                    try:
                        df = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=16)# 1분당 캔들조회
                        df1 = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=106) # 1분당 캔들조회
                        ma60 = round(df1['close'].rolling(window=100 ,min_periods=1).mean(),1)#60분 거래평균
                        ma5 = round(df['close'].rolling(window=12 ,min_periods=1).mean(),1) #5분 거래평균
                        break
                    except Exception as e:
                        continue
                    
                buy_avg_per = (ma5.iloc[-1] - ma60.iloc[-1])/ma5.iloc[-1]*100
                    
                #골든크로스 매수 
                if  buy_avg_per < -0.4 and get_target_now_volume(KrCoin[max]) > 2000:#매수
                    upbit.buy_market_order(KrCoin[max],7000)
                    print("시간 : %s %s 골든크로스 매수" %(now,KrCoin[max]))
                    time.sleep(1)
                    get_target_sell(KrCoin[max])

                    

                                              
        time.sleep(0.2)
        if max ==limit:
            max = 0
        else:
            max += 1
    
    except Exception as e:
        time.sleep(1)