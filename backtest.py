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

# def get_dispersion():
#     """분산 매수"""

#     krw = upbit.get_balance() #보유중인 현금

    
#     if krw  <= 440000: 
#         return krw
#     else:
#         return 440000
    

def get_target_sell(ticker):
    """매도하는 코ㅗㅗㅗ드"""
    price = 0.007

    balan = upbit.get_balance_t('%s'%ticker)  # 거래 코인 갯수 float
    avg = upbit.get_avg_buy_price('%s'%ticker)# 거래 평균가
    compare = round((avg * price) + avg,2) 
    
    if compare >= 1000 and compare < 100000:
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

def time_limit():
    KrCoin = pyupbit.get_tickers(fiat="KRW") #원화거래 코인 조회
    for coin in KrCoin:
        cancel = upbit.get_order('%s'%coin)
        time.sleep(0.2)
        if cancel!=[]:
            for ca in cancel:      
                upbit.cancel_order(ca['uuid'])
                time.sleep(1)

    bal = upbit.get_balances()
    for b in bal:
        ticker = (b['currency']) #거래 코인명
        balan = float(b['balance']) #거래 코인 갯수

        if ticker!='KRW'and ticker!='GTO'and ticker!='QTCON' and ticker!='VTHO':
            upbit.sell_market_order("KRW-%s" %ticker, balan)
            time.sleep(1)         
    sys.exit()  

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("로그인 확인")
max = 0
KrCoin = pyupbit.get_tickers(fiat="KRW") #원화거래 코인 조회
limit = len(KrCoin)-1 # 조회된 원화거래코인 최대개수확인

slimittime = datetime.timedelta(seconds=30) #미체결 시간 매수
rlimittime = datetime.timedelta(minutes=5) #5분

now = datetime.datetime.now(timezone('Asia/Seoul'))

btime = datetime.datetime(1,1,1,1,1,1)  #매수 시간 초기화값을 모름 임시
stime = datetime.datetime(1,1,1,1,1,1)  #매도 시간 초기화값을 모름 임시
paretime = datetime.datetime(1,1,1,1,1,1) #시간비교를 위한 변수

while True:
    try: 
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        #손절 ask
        bal = upbit.get_balances()
        for b in bal:
            ticker = (b['currency']) #거래 코인명
            balan = (b['balance']) #거래 코인 갯수
            buy_avg = (b['avg_buy_price']) #매수가격

            if ticker!='KRW'and ticker!='GTO'and ticker!='QTCON' and ticker!='VTHO' and ticker!='APENFT':
                    time.sleep(0.01)    
                    cancel = upbit.get_order('KRW-%s'%ticker)
                    
                    return_price = (get_target_price("KRW-%s" %ticker)) #현재가격
                    buy_price = float (buy_avg)
                    price_avg = (return_price - buy_price) / buy_price * 100
    
                    while True:
                        try:
                            ddf = pyupbit.get_ohlcv("%s-%s"%("KRW",ticker), interval="minute1", count=16)# 1분당 캔들조회
                            ddf1 = pyupbit.get_ohlcv("%s-%s"%("KRW",ticker), interval="minute1", count=106) # 1분당 캔들조회
                            ma60 = round(ddf1['close'].rolling(window=100 ,min_periods=1).mean(),1)#60분 거래평균
                            ma5 = round(ddf['close'].rolling(window=12 ,min_periods=1).mean(),1) #5분 거래평균
                            break
                        except Exception as e:
                            continue
                    
                    for ca in cancel:
                        daedcross1 = ma5.iloc[-1]-ma60.iloc[-1]
                        if ma5.iloc[-1] == ma60.iloc[-1] and ma5[-2] > ma5[-1]:
                            upbit.cancel_order(ca['uuid'])
                            time.sleep(0.2)
                            balanc = upbit.get_balance(ticker)
                            upbit.sell_market_order("KRW-%s" %ticker, balanc)
                            print("KRW-%s 데드크로스 매도" %ticker)

                    if price_avg <= -3:
                        for ca in cancel:
                            
                            upbit.cancel_order(ca['uuid'])
                            time.sleep(0.2)
                            balanc = upbit.get_balance(ticker)
                            upbit.sell_market_order("KRW-%s" %ticker, balanc)
                            print("KRW-%s 3퍼손절" %ticker)        
        
        
        for n in bal:
            if ('KRW-%s' % n['currency']) == KrCoin[max] or 'KRW-OMG'== KrCoin[max] or 'KRW-SRM'== KrCoin[max]: # 이미 가지고 있는 코인인가?
                if max == limit:
                    max = 0
                else:
                    max += 1
                continue
        
        #매수 부분
        if get_target_value(KrCoin[max]) >= 50000000000: #거래대금이 60,000백만 이상인가
                
                while True:
                    try:
                        df = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=16)# 1분당 캔들조회
                        df1 = pyupbit.get_ohlcv(KrCoin[max], interval="minute1", count=76) # 1분당 캔들조회
                        ma60 = round(df1['close'].rolling(window=70 ,min_periods=1).mean(),1)#60분 거래평균
                        ma5 = round(df['close'].rolling(window=12 ,min_periods=1).mean(),1) #5분 거래평균
                        break
                    except Exception as e:
                        continue
                
                
                #골든크로스 매수 
                if ma5.iloc[-1] > ma5.iloc[-2]  and ma5.iloc[-1] == ma60.iloc[-1]:#골든 크로스 매수   
                    upbit.buy_market_order(KrCoin[max],440000)
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
