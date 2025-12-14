import pprint
import requests

def get_seoul_weather():
    api_key = '2f7922c6ee918b5904d3a188767ced3f'

    # 서울의 위도
    lat = 37.56
    # 서울의 경도
    lon = 126.97

    # API 요청 URL
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'

    # API 요청 보내기
    response = requests.get(url).json()
    return response


if __name__ == '__main__':
    # json 형태의 데이터 반환
    result = get_seoul_weather()
    # prrint.prrint(): json 을 보기 좋은 형식으로 출력
    pprint.pprint(result)
