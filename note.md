

# 設計

## 資料庫保存
* User id
* Node status
* Conversation Entity

## 連續對話設計
* 順序
* 回應檢查
* State -> Conversation -> Question
    * State
	* 保存Conversation並控制State的移動
    * Conversation
	* 保存Questions控制問題的走向


# API-THSR

## 1. 取得車站的基本資料
* GET /v2/Rail/THSR/Station
* select: "StationID,StationName"
* filter(optional): StationName/Zh_tw eq "台北"

## 2. 取得當天所有車次的車次資料
* GET /v2/Rail/THSR/DailyTrainInfo/Today
* filter(optional): StationName/Zh_tw eq "台北"

## 3. 取得指定[日期]所有車次的車次資料
* GET /v2/Rail/THSR/DailyTrainInfo/TrainDate/{TrainDate}
* TrainDate: 'yyyy-MM-dd'
* filter(optional): StationName/Zh_tw eq "台北"

## 4. 取得指定[日期],[車站]的站別時刻表資料
* GET /v2/Rail/THSR/DailyTimetable/Station/{StationID}/{TrainDate}
* StationID: '0660'
* TrainDate: 'yyyy-MM-dd'
* filter(optional): StationName/Zh_tw eq "台北"

## 5. 取得指定[日期],[起迄站間]之時刻表資料
* GET /v2/Rail/THSR/DailyTimetable/OD/{OriginStationID}/to/{DestinationStationID}/{TrainDate}
* OriginStationID: 0660
* DestinationStationID: 0990
* TrainDate: 'yyyy-MM-dd'
* select(optional): "DailyTrainInfo"
* filter(optional): StationName/Zh_tw eq "台北"

## 6. 取得即時通阻事件資料
* GET /v2/Rail/THSR/AlertInfo

## 7. 取得動態指定[車站]的對號座剩餘座位資訊看板資料
* GET /v2/Rail/THSR/AvailableSeatStatusList/{StationID}

## Ignore
* GET /v2/Rail/THSR/ODFare 取得票價資料
* GET /v2/Rail/THSR/ODFare/{OriginStationID}/to/{DestinationStationID} 取得指定[起訖站間]之票價資料
* GET /v2/Rail/THSR/GeneralTimetable 取得所有車次的定期時刻表資料
* GET /v2/Rail/THSR/GeneralTimetable/TrainNo/{TrainNo} 取得指定[車次]的定期時刻表資料
* GET /v2/Rail/THSR/DailyTrainInfo/Today/TrainNo/{TrainNo} 取得當天指定[車次]的車次資料
* GET /v2/Rail/THSR/DailyTrainInfo/TrainNo/{TrainNo}/TrainDate/{TrainDate} 取得指定[日期],[車次]的車次資料
* GET /v2/Rail/THSR/News 取得高鐵最新消息資料
* GET /v2/Rail/THSR/Shape 取得軌道路網實體路線圖資資料
* GET /v2/Rail/THSR/StationExit 取得車站出入口基本資料
