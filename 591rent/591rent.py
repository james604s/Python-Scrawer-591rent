#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 23:16:23 2019

@author: squid504s
"""
'''
由原本變數刪減至13個變數
其中變數如下
id 標題 行政區 地址 總價 單價 總坪數 主建物坪數 房數 樓層
屋齡 使用分區 建物型態

地址轉換出經緯度
房數切割成房廳衛3個變數欄位 並且刪除0衛的資料
樓層切割為總樓層與移轉樓層 並且刪除透天 與 1樓資料
ID刪除重複資料
標題刪除有含車位的關鍵字
建物型態刪除透天

除了id相同 由於591的資料有很多仲介或屋主刊登
因此透過程式比對變數藉此刪除重複資料 	
如相同總價 坪數 移轉樓層 總樓層 屋齡 地址 則視為相同資料



'''

import requests
import pandas as pd
import numpy as np
import json
import time

#%%
#抓第一頁資料
url = 'https://sale.591.com.tw/home/search/list?type=2&&shType=list&regionid=1&firstRow=0'

headers = {
   'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36' 
}

res = requests.get(url, headers = headers)
jd = res.json()
row_range = int(round(int(jd["data"]["total"])/30, 0)) #只會到倒數第二頁
row_end = int(jd["data"]["total"]) #最後一頁

del url, headers, jd

#%%
#這裡只會抓到倒數第二頁
start = time.time()

for z in range(0,row_range):
    #設定與獲取資料
    url = 'https://sale.591.com.tw/home/search/list?type=2&&shType=list&regionid=1&firstRow=' + str(30*z)
    
    headers = {
       'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36' 
    }
    
    res = requests.get(url, headers = headers)
    jd = res.json()
    
    
    df = pd.DataFrame(jd["data"]["house_list"])
    
    #處理多抓的奇怪資料
    drop_number = []
    for j in range(0,len(df)):
        
        if(type(df["address"].iloc[j]) == float):
            drop_number.append(j)
    
    df = df.drop(drop_number, axis = 0).reset_index(drop = True)
    del drop_number
    
    
    #資料整理 13欄位
    #need_list = ["address", "area", "floor", "houseage", "houseid", "kind_name", "mainarea", "price", "room", "section_name", "shape_name", "title", "unitprice"]
    need_list = ["houseid", "title", "section_name", "address", "price", "unitprice", "area", "mainarea", "room", "floor", "houseage", "kind_name", "shape_name"]
    
    df_need = df[need_list]
    
    df_need["unitprice"] = df_need["unitprice"].apply(float)
    
    #只留下 住宅 住辦 套房
    df_need = df_need[df_need["kind_name"].isin(["住宅", "住辦", "套房"])].reset_index(drop = True)
    
    
    #處理房數
    df_a = pd.DataFrame(df_need["room"])
    
    df_b = pd.DataFrame()
    
    for i in range(0,len(df_a)):
        
        #遺失值 或 開放空間
        if(df_a["room"].iloc[i] == ""): #補充 因為isnan不能判斷字串 因此改用字串長度
            pass
        
        
        if(df_a["room"].iloc[i] == "開放式格局"):
            df_b = pd.concat([df_b, pd.DataFrame([1,0,1]).T.rename(columns = {0:"Room", 1:"Hall", 2:"Toilet"})], axis = 0)
        
        
        #正常
        if(len(df_a["room"].iloc[i]) > 0 and df_a["room"].iloc[i] != "開放式格局"):
            #處理房數切割
            #房
            room = df_a["room"].iloc[i].split("房")
            
            #廳
            if(len(room) >= 2):
                hall = room[1].split("廳")
                
            if(len(room) == 1):
                hall = room[0].split("廳")
            
            #衛
            if(len(hall) >= 2):
                toilet = hall[1].split("衛")
            
            if(len(hall) == 1):
                toilet = hall[0].split("衛")
            
            #轉成數字
            
            if(len(room) == 2):
                room = int(room[0])
                
            if(type(room) == list):
                if(len(room) == 1):
                    room = 0
            
            if(len(hall) == 2):
                hall = int(hall[0])
            
            if(type(hall) == list):
                if(len(hall) == 1):
                    hall = 0
                
            if(len(toilet) == 2):
                toilet = int(toilet[0])
            
            if(type(toilet) == list):
                if(len(toilet) == 1):
                    toilet = 0
       
            df_c = pd.DataFrame([room,hall,toilet]).T.rename(columns = {0:"Room", 1:"Hall", 2:"Toilet"})
            df_b = pd.concat([df_b, df_c], axis = 0)
    
    df_room = df_b.reset_index(drop = True)
    
    del df_a, df_b, df_c, hall, i, room, toilet
    
    #處理樓層
    df_a = df_need["floor"]
    df_b = pd.DataFrame()
    
    for i in range(0,len(df_a)):
        
        if(df_a[i] != ""):
            floor_data = df_a[i].split("/")
            
            floor = floor_data[0].split("F")[0]
            tfloor = floor_data[1].split("F")[0]
            
            df_b = pd.concat([df_b, pd.DataFrame([floor, tfloor]).T.rename(columns = {0:"Floor", 1:"TFloor"})], axis = 0)
        
        
        if(df_a[i] == ""):
            floor_data = ""
            
            floor = ""
            tfloor = ""
            
            df_b = pd.concat([df_b, pd.DataFrame([floor, tfloor]).T.rename(columns = {0:"Floor", 1:"TFloor"})], axis = 0)
        
        
    df_floor = df_b.reset_index(drop = True)
    
    
    del df_a, df_b, floor, tfloor, floor_data
    
    
    #找出經緯度位置
    df_lat_lon = pd.DataFrame()
    
    for i in range(0,len(df_need)):
        
        #網址設定
        url_map = "https://sale.591.com.tw/home/house/detail/2/" + str(df["houseid"].iloc[i]) + ".html#detail-map"
        res_map = requests.get(url_map, headers = headers)
        
        #抓出經緯度
        map_start = res_map.text.find('src="//maps.google.com.tw/maps?f=q&hl=zh-TW&q=') #網址開頭
        map_end = res_map.text.find('output=embed"></iframe>') + len('output=embed"></iframe>') #網址結尾
        
        map_link = res_map.text[map_start:map_end] #合併出網址
        lat_lon = map_link[(map_link.find("TW&q=")+len("TW&q=")):map_link.find("&z=")]
        lat_lon = pd.DataFrame(lat_lon.split(",")).T.rename(columns = {0:"lat", 1:"lon"})
        
        df_lat_lon = pd.concat([df_lat_lon, lat_lon], axis = 0)
    
    
    df_lat_lon = df_lat_lon.reset_index(drop = True)  
    
    del url_map, res_map, map_start, map_end, map_link, lat_lon, headers, i, j, jd, url, df
    
    
    #合併
    if(z == 0):
        df_all = pd.concat([df_need[need_list[0:7]], df_room, df_floor, df_need[need_list[10:13]], df_lat_lon], axis = 1)
        df_all.columns = ["ID", "標題", "行政區", "地址", "總價", "每坪單價", "坪數", "房數", "廳數", "衛數", "移轉樓層", "總樓層", "屋齡", "主要用途", "建物型態", "緯度", "經度"]

    if(z != 0):
        df_save = pd.concat([df_need[need_list[0:7]], df_room, df_floor, df_need[need_list[10:13]], df_lat_lon], axis = 1)
        df_save.columns = ["ID", "標題", "行政區", "地址", "總價", "每坪單價", "坪數", "房數", "廳數", "衛數", "移轉樓層", "總樓層", "屋齡", "主要用途", "建物型態", "緯度", "經度"]
        
        df_all = pd.concat([df_all, df_save], axis = 0)


end = time.time()
(end - start)/60

#約78分鐘

del df_floor, df_lat_lon, df_need, df_room, df_save, end, need_list, row_range, start, z

#%%
#最後一頁
#設定與獲取資料
#Step 1 抓第一頁資料
url = 'https://sale.591.com.tw/home/search/list?type=2&&shType=list&regionid=1&firstRow=' + str(row_end)

headers = {
   'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36' 
}

res = requests.get(url, headers = headers)
jd = res.json()


df = pd.DataFrame(jd["data"]["house_list"])

#處理多抓的奇怪資料
drop_number = []
for j in range(0,len(df)):
    
    if(type(df["address"].iloc[j]) == float):
        drop_number.append(j)

df = df.drop(drop_number, axis = 0).reset_index(drop = True)
del drop_number

row_range = int(round(int(jd["data"]["total"])/30, 0)) #只會到倒數第二頁
row_end = int(jd["data"]["total"]) #最後一頁

#資料整理
#need_list = ["address", "area", "floor", "houseage", "houseid", "kind_name", "mainarea", "price", "room", "section_name", "shape_name", "title", "unitprice"]
need_list = ["houseid", "title", "section_name", "address", "price", "unitprice", "area", "mainarea", "room", "floor", "houseage", "kind_name", "shape_name"]

df_need = df[need_list]

df_need["unitprice"] = df_need["unitprice"].apply(float)

#只留下 住宅 住辦 套房
df_need = df_need[df_need["kind_name"].isin(["住宅", "住辦", "套房"])].reset_index(drop = True)

#處理房數
df_a = pd.DataFrame(df_need["room"])

df_b = pd.DataFrame()

for i in range(0,len(df_a)):
    
    
    #遺失值 或 開放空間
    if(df_a["room"].iloc[i] == ""): #補充 因為isnan不能判斷字串 因此改用字串長度
        pass
        
        
    if(df_a["room"].iloc[i] == "開放式格局"):
        df_b = pd.concat([df_b, pd.DataFrame([1,0,1]).T.rename(columns = {0:"Room", 1:"Hall", 2:"Toilet"})], axis = 0)
        
    
    #正常
    if(len(df_a["room"].iloc[i]) > 0 and df_a["room"].iloc[i] != "開放式格局"):
        #處理房數切割
        #房
        room = df_a["room"].iloc[i].split("房")
        
        #廳
        if(len(room) >= 2):
            hall = room[1].split("廳")
            
        if(len(room) == 1):
            hall = room[0].split("廳")
        
        #衛
        if(len(hall) >= 2):
            toilet = hall[1].split("衛")
        
        if(len(hall) == 1):
            toilet = hall[0].split("衛")
        
        #轉成數字
        
        if(len(room) == 2):
            room = int(room[0])
            
        if(type(room) == list):
            if(len(room) == 1):
                room = 0
        
        if(len(hall) == 2):
            hall = int(hall[0])
        
        if(type(hall) == list):
            if(len(hall) == 1):
                hall = 0
            
        if(len(toilet) == 2):
            toilet = int(toilet[0])
        
        if(type(toilet) == list):
            if(len(toilet) == 1):
                toilet = 0
   
        df_c = pd.DataFrame([room,hall,toilet]).T.rename(columns = {0:"Room", 1:"Hall", 2:"Toilet"})
        df_b = pd.concat([df_b, df_c], axis = 0)

df_room = df_b.reset_index(drop = True)

del df_a, df_b, df_c, hall, i, room, toilet

#處理樓層
df_a = df_need["floor"]
df_b = pd.DataFrame()

for i in range(0,len(df_a)):
    
    if(df_a[i] != ""):
        floor_data = df_a[i].split("/")
            
        floor = floor_data[0].split("F")[0]
        tfloor = floor_data[1].split("F")[0]
            
        df_b = pd.concat([df_b, pd.DataFrame([floor, tfloor]).T.rename(columns = {0:"Floor", 1:"TFloor"})], axis = 0)
        
        
    if(df_a[i] == ""):
        floor_data = ""
            
        floor = ""
        tfloor = ""
            
        df_b = pd.concat([df_b, pd.DataFrame([floor, tfloor]).T.rename(columns = {0:"Floor", 1:"TFloor"})], axis = 0)
        
        
df_floor = df_b.reset_index(drop = True)


del df_a, df_b, floor, tfloor, floor_data


#找出經緯度位置
df_lat_lon = pd.DataFrame()

for i in range(0,len(df_need)):
    
    #網址設定
    url_map = "https://sale.591.com.tw/home/house/detail/2/" + str(df["houseid"].iloc[i]) + ".html#detail-map"
    res_map = requests.get(url_map, headers = headers)
    
    #抓出經緯度
    map_start = res_map.text.find('src="//maps.google.com.tw/maps?f=q&hl=zh-TW&q=') #網址開頭
    map_end = res_map.text.find('output=embed"></iframe>') + len('output=embed"></iframe>') #網址結尾
    
    map_link = res_map.text[map_start:map_end] #合併出網址
    lat_lon = map_link[(map_link.find("TW&q=")+len("TW&q=")):map_link.find("&z=")]
    lat_lon = pd.DataFrame(lat_lon.split(",")).T.rename(columns = {0:"lat", 1:"lon"})
    
    df_lat_lon = pd.concat([df_lat_lon, lat_lon], axis = 0)


df_lat_lon = df_lat_lon.reset_index(drop = True)  

del url_map, res_map, map_start, map_end, map_link, lat_lon, headers, i, j, jd, url, df


#合併
df_save = pd.concat([df_need[need_list[0:7]], df_room, df_floor, df_need[need_list[10:13]], df_lat_lon], axis = 1)
df_save.columns = ["ID", "標題", "行政區", "地址", "總價", "每坪單價", "坪數", "房數", "廳數", "衛數", "移轉樓層", "總樓層", "屋齡", "主要用途", "建物型態", "緯度", "經度"]
    
df_all = pd.concat([df_all, df_save], axis = 0)

df_all = df_all.reset_index(drop = True)
    

del df_floor, df_lat_lon, df_need, df_room, df_save, need_list, row_end, row_range

#%%
#最後整理

#處理重複資料
df_all.drop_duplicates(subset = "ID", keep='first', inplace = True)
df_all = df_all.reset_index(drop = True)



#移轉樓層的處理 只留單一樓層
#利用判斷是否為數字 排除頂加與透天
drop_list = []

for i in range(0,len(df_all)):
    if(df_all["移轉樓層"].iloc[i].isdigit() == False):
        drop_list.append(i)


df_all = df_all.drop(drop_list).reset_index(drop = True)

del drop_list, i

#處理非id相同的重複資料
save_data = pd.DataFrame()

for i in range(0,len(df_all)):
    
    sign = df_all.iloc[i]
    
    df_part = df_all[df_all["行政區"] == sign["行政區"]]
    df_part = df_part[df_part["坪數"] == sign["坪數"]]
    df_part = df_part[df_part["移轉樓層"] == sign["移轉樓層"]]
    df_part = df_part[df_part["總樓層"] == sign["總樓層"]]
    
    #判斷是否為重複的資料 若一筆就是 直接存
    if(len(df_part) == 1):
        save_data = pd.concat([save_data, pd.DataFrame(df_part.iloc[0]).T], axis = 0)
    
    
    #判斷是否為重複的資料 若一筆就是不是
    if(len(df_part) > 1): 
        
        if(i == 0): #第一次直接抓 並且以第一筆為結果
            save_data = pd.concat([save_data, pd.DataFrame(df_part.iloc[0]).T], axis = 0)
        
        if(i != 0): #非第一次 因此用相同資料的第一筆去判斷之前是否有抓取過(補充 第一筆與過去為相同的資料 所以用第一筆核對)
            if(sum(df_part["ID"].iloc[0] == save_data["ID"]) == 0):
                save_data = pd.concat([save_data, pd.DataFrame(df_part.iloc[0]).T], axis = 0)


#%%

del df_part, i, sign


#%%

save_data = save_data[save_data["衛數"] != 0].reset_index(drop =True)
save_data = save_data[save_data["移轉樓層"] != "1"].reset_index(drop =True)
save_data = save_data[save_data["建物型態"] != "透天厝"].reset_index(drop =True)



#刪除標題帶車位
drop_car_list = []

for i in range(0,len(save_data)):
    if(save_data["標題"].iloc[i].find("車位") != -1):
        drop_car_list.append(i)


save_data = save_data.drop(drop_car_list, axis = 0).reset_index(drop = True)


del drop_car_list, i



#%%
#計算

#各行政區平均單價 與 每個行政區價格分配比例
r_list = pd.DataFrame(save_data["行政區"])
r_list.drop_duplicates(subset = "行政區", keep='first', inplace = True)
r_list = r_list.reset_index(drop = True)


t_list = pd.DataFrame(save_data["建物型態"])
t_list.drop_duplicates(subset = "建物型態", keep='first', inplace = True)
t_list = t_list.reset_index(drop = True)

df_type = pd.DataFrame()
df_price = pd.DataFrame()
df_mean = pd.DataFrame()

for i in range(0,len(r_list)):
    
    r_data = save_data[save_data["行政區"] == r_list["行政區"].iloc[i]].reset_index(drop = True)
    price_mean = r_data["每坪單價"].mean()
    
    price_50 = []
    price_50_75 = []
    price_75_100 = []
    price_100 = []
    
    type_5 = []
    type_10 =[]
    type_11 = []
    type_other = []
    
    for j in range(0,len(r_data)):
        
        #分類價格區間位置
        if(r_data["每坪單價"].iloc[j] >= 100):price_100.append(j)
        if(100 > r_data["每坪單價"].iloc[j] and r_data["每坪單價"].iloc[j] >= 75):price_75_100.append(j)
        if(75 > r_data["每坪單價"].iloc[j] and r_data["每坪單價"].iloc[j] >= 50):price_50_75.append(j)
        if(50 > r_data["每坪單價"].iloc[j]):price_50.append(j)


        #各類別區間
        if(r_data["建物型態"].iloc[j] == "公寓"):type_5.append(j)
        if(r_data["建物型態"].iloc[j] == "華廈" or r_data["建物型態"].iloc[j] == "住宅大樓"):type_10.append(j)
        if(r_data["建物型態"].iloc[j] == "電梯大樓"):type_11.append(j)
        if(r_data["建物型態"].iloc[j] != "公寓" and r_data["建物型態"].iloc[j] != "華廈" and r_data["建物型態"].iloc[j] != "住宅大樓" and r_data["建物型態"].iloc[j] != "電梯大樓"):type_other.append(j)

    
    save_mean = pd.DataFrame([r_list["行政區"].iloc[i], price_mean]).T
    save_price = pd.DataFrame([r_list["行政區"].iloc[i], len(r_data.iloc[price_50]["每坪單價"]), len(r_data.iloc[price_50_75]["每坪單價"]), len(r_data.iloc[price_75_100]["每坪單價"]), len(r_data.iloc[price_100]["每坪單價"])]).T
    save_type = pd.DataFrame([r_list["行政區"].iloc[i], r_data.iloc[type_5]["每坪單價"].mean(), r_data.iloc[type_10]["每坪單價"].mean(), r_data.iloc[type_11]["每坪單價"].mean(), r_data.iloc[type_other]["每坪單價"].mean()]).T

    df_price = pd.concat([df_price, save_price], axis = 0)
    df_type = pd.concat([df_type, save_type], axis = 0)
    df_mean = pd.concat([df_mean, save_mean], axis = 0)


df_price = df_price.rename(columns = {0:"行政區", 1:"100萬以上", 2:"˙75~100萬", 3:"50~75萬", 4:"50萬以下"})
df_type = df_type.rename(columns = {0:"行政區", 1:"公寓平均單價", 2:"華廈平均單價", 3:"電梯大樓平均單價", 4:"其他類平均單價"})
df_mean = df_mean.rename(columns = {0:"行政區", 1:"平均單價"})


#%%

del i, j, price_100, price_50, price_50_75, price_75_100, price_mean, r_data, r_list, save_mean, save_price, save_type, t_list, type_10, type_11, type_5, type_other




















