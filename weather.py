import requests
import os
from datetime import datetime, timedelta


# ==========================================
# 기상청 API KEY
# ==========================================

SERVICE_KEY = os.getenv("KMA_SERVICE_KEY")


# ==========================================
# 경기도 지역
# ==========================================

REGIONS = {
    "수원": (60, 121),
    "성남": (62, 123),
    "용인": (64, 119),
    "고양": (57, 128),
    "화성": (57, 119),
    "안양": (59, 123),
    "부천": (56, 126),
    "안산": (58, 121),
    "평택": (62, 114),
    "광명": (58, 126),
    "시흥": (57, 123),
    "군포": (59, 122),
    "의왕": (60, 122),
    "하남": (64, 127),
    "남양주": (64, 128),
    "구리": (62, 127),
    "파주": (56, 131),
    "의정부": (61, 130),
    "양주": (61, 131),
    "이천": (68, 121),
    "광주": (65, 123),
    "김포": (55, 128),
    "오산": (62, 118),
    "여주": (71, 121)
}


BASE_TIMES = [
    "0200",
    "0500",
    "0800",
    "1100",
    "1400",
    "1700",
    "2000",
    "2300"
]


def get_latest_base_datetime():

    now = datetime.now()

    for time_str in reversed(BASE_TIMES):

        hour = int(time_str[:2])

        base = now.replace(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0
        )

        if base + timedelta(minutes=10) <= now:
            return now.strftime("%Y%m%d"), time_str

    yesterday = now - timedelta(days=1)

    return yesterday.strftime("%Y%m%d"), "2300"


def get_weather(region):

    if not SERVICE_KEY:
        raise RuntimeError(
            "KMA_SERVICE_KEY가 설정되지 않았습니다. "
            "Vercel 환경 변수를 확인하세요."
        )

    if region not in REGIONS:
        raise ValueError(
            "지원하지 않는 지역입니다."
        )

    nx, ny = REGIONS[region]

    base_date, base_time = get_latest_base_datetime()

    url = (
        "https://apis.data.go.kr/1360000/"
        "VilageFcstInfoService_2.0/getVilageFcst"
    )

    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    header = data["response"]["header"]

    if header["resultCode"] != "00":
        raise RuntimeError(
            header["resultMsg"]
        )

    items = data["response"]["body"]["items"]["item"]

    today = datetime.now().strftime("%Y%m%d")

    tomorrow = (
        datetime.now() + timedelta(days=1)
    ).strftime("%Y%m%d")

    return {
        "region": region,

        "today": make_day_data(
            items,
            today
        ),

        "tomorrow": make_day_data(
            items,
            tomorrow
        )
    }


def make_day_data(items, target_date):

    temps = []
    pops = []
    humidity = []
    winds = []
    skies = []
    precipitation = []

    for item in items:

        if item["fcstDate"] != target_date:
            continue

        category = item["category"]
        value = item["fcstValue"]

        if category == "TMP":
            temps.append(float(value))

        elif category == "POP":
            pops.append(float(value))

        elif category == "REH":
            humidity.append(float(value))

        elif category == "WSD":
            winds.append(float(value))

        elif category == "SKY":
            skies.append(value)

        elif category == "PTY":
            precipitation.append(value)


    # 하늘 상태
    sky_names = {
        "1": "맑음",
        "3": "구름많음",
        "4": "흐림"
    }

    if skies:

        sky_code = max(
            set(skies),
            key=skies.count
        )

        sky = sky_names.get(
            sky_code,
            "알 수 없음"
        )

    else:
        sky = "알 수 없음"


    # 강수 상태
    if precipitation:

        if any(
            x in ["1", "2", "4"]
            for x in precipitation
        ):
            precipitation_text = "비 또는 눈"

        else:
            precipitation_text = "강수 없음"

    else:
        precipitation_text = "강수 정보 없음"


    return {

        "date": (
            f"{target_date[:4]}-"
            f"{target_date[4:6]}-"
            f"{target_date[6:]}"
        ),

        "min_temp": (
            min(temps)
            if temps
            else None
        ),

        "max_temp": (
            max(temps)
            if temps
            else None
        ),

        "max_pop": (
            max(pops)
            if pops
            else 0
        ),

        "min_humidity": (
            min(humidity)
            if humidity
            else None
        ),

        "max_humidity": (
            max(humidity)
            if humidity
            else None
        ),

        "max_wind": (
            max(winds)
            if winds
            else None
        ),

        "sky": sky,

        "precipitation": precipitation_text
    }