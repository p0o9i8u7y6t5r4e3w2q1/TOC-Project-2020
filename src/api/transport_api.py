from abc import ABCMeta, abstractmethod
import requests
from returns.maybe import Maybe  # use this library just for fun
from returns.result import safe, Result
from typing import Dict, Optional
from .odata_operators import equal, greater_or_equal, field
import pendulum


class TransportApi(metaclass=ABCMeta):
    base_headers: Dict[str, str] = {
        "User-Agent":  # avoid checking authorization of api usage
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }
    base_url: str = "https://ptx.transportdata.tw/MOTC/v2/Rail"
    trans_type: str = ""  # maybe THSR, TRA, Metro
    base_params: Dict[str, str] = {"$format": "JSON", "$top": "30"}

    def get_url(self, api: str) -> str:
        base = self.base_url
        if api[0] != '/':
            base += '/'
        return base + self.trans_type + api

    def get_params(self, params: Maybe[Dict[str, str]]) -> Dict[str, str]:
        # "map" to map value if params is not None
        # "value_or" to set default value if params is None
        return params.map(lambda p: {
            **self.base_params,
            **p,
        }).value_or(self.base_params)

    def get_headers(self, headers: Maybe[Dict[str, str]]) -> Dict[str, str]:
        # "map" to map value if headers is not None
        # "value_or" to set default value if headers is None
        return headers.map(lambda h: {
            **self.base_headers,
            **h,
        }).value_or(self.base_headers)

    def get(self,
            api: str,
            params: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict:
        print(self.get_params(Maybe.new(params)))
        response = requests.get(self.get_url(api),
                                params=self.get_params(Maybe.new(params)),
                                headers=self.get_headers(Maybe.new(headers)))
        response.raise_for_status()
        # print(response.json())
        return response.json()

    @abstractmethod
    def station_info(self, station_name: str) -> Result:
        return NotImplemented


class THSR_Api(TransportApi):
    trans_type = '/THSR'

    def all_station_info(self):
        self.get("/Station")

    def station_info(self, station_name: str):
        params = {
            '$filter': equal(["StationName", "Zh_tw"], station_name),
            '$select': 'StationName,StationID'
        }
        return self.get("/Station", params)[0]

    def query_train_info_by_time(self, start_station, end_station, time=None):
        if time is None:
            time = pendulum.now('Asia/Taipei')
            # time = pendulum.parse('2019-12-11T10:30')
        params = {
            '$filter':
            greater_or_equal(['OriginStopTime', 'DepartureTime'],
                             time.format("HH:00")),
            '$top': '5',
            '$orderby':
            field(['OriginStopTime', 'DepartureTime'])
        }
        print(params)
        return self.get(
            f"/DailyTimetable/OD/{start_station}/to/{end_station}/{time.format('YYYY-MM-DD')}",
            params)


class Metro_Api(TransportApi):
    trans_type = '/Metro'

    def all_station_info(self):
        metro_type = 'KRTC'
        self.get(f"/Station/{metro_type}")

    def station_info(self, station_name: str):
        metro_type = 'KRTC'
        params = {
            '$filter': equal(["StationName", "Zh_tw"], station_name),
            '$select': 'StationName,StationID'
        }
        return self.get(f"/Station/{metro_type}", params)[0]

    def query_waiting_time_info(self, station_id: str):
        metro_type = 'KRTC'
        params = {
            '$filter': equal(["StationID"], station_id),
        }
        return self.get(f"/LiveBoard/{metro_type}", params)


class TRA_Api(TransportApi):
    trans_type = '/TRA'

    def all_station_info(self):
        self.get(f"/Station")

    def station_info(self, station_name: str):
        params = {
            '$filter': equal(["StationName", "Zh_tw"], station_name),
            '$select': 'StationName,StationID'
        }
        return self.get(f"/Station", params)[0]

    def query_waiting_time_info(self, station_id: str):
        params = {
            '$top': '10',
        }
        return self.get(f"/LiveBoard/Station/{station_id}", params)


THSR = THSR_Api()
Metro = Metro_Api()
TRA = TRA_Api()
# print(THSR.query_train_info_by_time(1030, 1000, pendulum.parse('2019-12-10T10:30')))
# print(Metro.query_train_info('O13'))
# print(TRA.query_waiting_time_info('4220'))

def DirectionName(code: int):
    if code == 0:
        return "北上"
    elif code == 1:
        return "南下"
    return None
