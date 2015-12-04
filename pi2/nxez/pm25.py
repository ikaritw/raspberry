#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'ikaritw@gmail.com'

import traceback
from datetime import datetime
import time,urllib, urllib2, json
import sys,signal
def signal_handler(signal, frame):
    print('\nYou pressed Ctrl+C!')

    print('關閉led!')
    SAKS.ledrow.off()

    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

'''
測試LED燈
'''

#載入SAKS的SDK
sys.path.insert(0, './SAKS_SDK')
from sakshat import SAKSHAT


#環境資源資料開放平台
weather_url = 'http://opendata2.epa.gov.tw/AQX.json'
sitename = u'新店'
'''
    "CO": "0.55",
    "County": "新北市",
    "FPMI": "3",
    "MajorPollutant": "懸浮微粒",
    "NO": "3.75",
    "NO2": "14",
    "NOx": "17.62",
    "O3": "23",
    "PM10": "92",
    "PM2.5": "37",
    "PSI": "53",
    "PublishTime": "2015-12-03 12:00",
    "SiteName": "新店",
    "SO2": "3.5",
    "Status": "普通",
    "WindDirec": "125",
    "WindSpeed": "3.7"
}]'''
def get_pm25():
    global weather_url,sitename
    headers = { "User-Agent" : "Mozilla/5.0 (raspberry pi 2)","Accept":"application/json, text/javascript, */*; q=0.01" }
    
    try:
        req = urllib2.Request(url=weather_url,headers=headers)
        #print req.get_full_url()
        resp = urllib2.urlopen(req)
        content = resp.read()
        if(content):
            #print(content)
            weatherJSON = json.JSONDecoder().decode(content)
            try:

                if len(weatherJSON) > 0:
                    for site in weatherJSON:
                        #site = weatherJSON[0]
                        if site.has_key('PM2.5') and site['SiteName'] == sitename:
                            msg = site['SiteName'] + ',' + site['Status'] + ',' + site['PM2.5'] + ',' + site['PublishTime']
                            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' {' + msg + '}')
                            return int(site['PM2.5'])
                    return -1
                else:
                    return -1
            except:
                return -1
    except:
        print("oh oh~get_pm25 is fail~")
        traceback.print_exc()
        return -1


#擷取間隔1800秒
update_interval = 1800

#Declare the SAKS Board
SAKS = SAKSHAT()

if __name__ == "__main__":

    #print len(SAKS.ledrow.items)
    print('>>>>' + weather_url)
    print('擷取PM2.5數值....')
    while True:
        pm25 = get_pm25()
        if pm25 == -1:
            time.sleep(30)
            continue

        SAKS.ledrow.off() # 關燈

        #严重污染，红灯亮蜂鸣器Beep
        if pm25 >= 250:
            SAKS.ledrow.off()
            SAKS.ledrow.items[7].on()
            SAKS.buzzer.beepAction(0.05,0.05,3)
        #重度污染，红灯亮
        if pm25 < 250:
            SAKS.ledrow.off()
            SAKS.ledrow.items[7].on()
        #中度污染，红灯亮
        if pm25 < 150:
            SAKS.ledrow.off()
            SAKS.ledrow.items[7].on()
        #轻度污染，黄灯亮
        if pm25 < 115:
            SAKS.ledrow.off()
            SAKS.ledrow.items[6].on()
        #良，1绿灯亮
        if pm25 < 75:
            SAKS.ledrow.off()
            SAKS.ledrow.items[4].on()
        #优，2绿灯亮
        if pm25 < 35:
            SAKS.ledrow.off()
            SAKS.ledrow.items[4].on()
            SAKS.ledrow.items[5].on()

        #print (("%4d" % pm25).replace(' ','#'))
        #数码管显示PM2.5数值
        SAKS.digital_display.show(("%4d" % pm25).replace(' ','#'))

        time.sleep(update_interval)

    SAKS.ledrow.off()
