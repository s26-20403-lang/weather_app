from flask import Flask, render_template, jsonify, request
from weather import get_weather, REGIONS
from google import genai
from dotenv import load_dotenv
import os


# =========================================================
# .env 읽기
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# =========================================================
# Gemini API 설정
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    print("✅ Gemini API 키를 불러왔습니다.")
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("❌ GEMINI_API_KEY를 찾지 못했습니다.")
    client = None


# =========================================================
# Flask
# =========================================================

app = Flask(__name__)


# =========================================================
# 메인 화면
# =========================================================

@app.route("/")
def home():
    return render_template(
        "index.html",
        regions=list(REGIONS.keys())
    )


# =========================================================
# 날씨 API
# =========================================================

@app.route("/api/weather")
def weather_api():

    region = request.args.get("region", "수원")

    try:

        weather = get_weather(region)

        return jsonify({
            "ok": True,
            "weather": weather
        })

    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# =========================================================
# Gemini AI 코디 추천
# =========================================================

@app.route("/api/outfit")
def outfit_api():

    region = request.args.get(
        "region",
        "수원"
    )

    try:

        # Gemini API 키 확인
        if not client:

            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 확인하세요."
            )


        # 날씨 가져오기
        weather = get_weather(region)

        today = weather["today"]


        # Gemini에게 전달할 프롬프트
        prompt = f"""
너는 한국 10대 남학생을 위한 데일리 코디 추천 AI야.

지역: {region}
날짜: {today["date"]}
날씨: {today["sky"]}
최저기온: {today["min_temp"]}°C
최고기온: {today["max_temp"]}°C
강수확률: {today["max_pop"]}%
습도: {today["min_humidity"]}~{today["max_humidity"]}%
최대풍속: {today["max_wind"]}m/s

위 날씨에 맞는 현실적인 데일리 코디를 추천해줘.

너무 비싸거나 특별한 옷보다는
일반적인 학생이 입기 좋은 옷으로 추천해줘.

비가 올 가능성이 있으면
우산이나 방수 신발 등도 고려해줘.

반드시 아래 형식으로 짧고 읽기 쉽게 답해줘.

👕 상의:
👖 하의:
👟 신발:
🧢 추가 아이템:

💡 추천 이유:
"""


        # =================================================
        # Gemini 호출
        # =================================================

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        # Gemini 응답
        recommendation = response.text


        return jsonify({
            "ok": True,
            "recommendation": recommendation
        })


    except Exception as e:

        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


# =========================================================
# 서버 실행
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )