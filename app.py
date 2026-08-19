from flask import Flask, render_template, jsonify, request
from weather import get_weather, REGIONS
from dotenv import load_dotenv
from groq import Groq
import os


# =========================================================
# 기본 설정
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# =========================================================
# Groq API 설정
# =========================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    print("✅ Groq API 키를 불러왔습니다.")
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("❌ GROQ_API_KEY를 찾지 못했습니다.")
    client = None


# =========================================================
# Flask
# =========================================================

app = Flask(__name__)


# =========================================================
# 메인 페이지
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
# Groq 코디 추천
# =========================================================

@app.route("/api/outfit")
def outfit_api():

    region = request.args.get("region", "수원")

    try:

        # API 키 확인
        if client is None:

            return jsonify({
                "ok": False,
                "error": "GROQ_API_KEY가 설정되지 않았습니다. Vercel 환경 변수를 확인하세요."
            }), 500


        # 날씨 가져오기
        weather = get_weather(region)

        today = weather.get("today", {})


        # =================================================
        # AI에게 전달할 프롬프트
        # =================================================

        prompt = f"""
너는 한국 학생을 위한 날씨 기반 데일리 코디 추천 AI야.

지역:
{region}

오늘 날씨:

날짜:
{today.get("date", "-")}

날씨 상태:
{today.get("sky", "-")}

강수:
{today.get("precipitation", "-")}

최저기온:
{today.get("min_temp", "-")}°C

최고기온:
{today.get("max_temp", "-")}°C

강수확률:
{today.get("max_pop", 0)}%

습도:
{today.get("min_humidity", "-")}~{today.get("max_humidity", "-")}%

최대풍속:
{today.get("max_wind", "-")}m/s


위 날씨에 맞는 현실적인 학생용 데일리 코디를 추천해줘.

조건:

1. 너무 과하게 꾸민 코디는 추천하지 않는다.
2. 일반적인 학생이 쉽게 입을 수 있는 옷을 추천한다.
3. 상의를 구체적으로 추천한다.
4. 하의를 구체적으로 추천한다.
5. 신발을 추천한다.
6. 필요하다면 겉옷을 추천한다.
7. 비가 올 가능성이 있으면 우산을 언급한다.
8. 더운 날씨라면 통풍이 좋은 옷을 추천한다.
9. 추운 날씨라면 보온성을 고려한다.
10. 바람이 강하면 바람을 고려한다.
11. 마지막에 추천 이유를 짧게 설명한다.
12. 한국어로 답변한다.

반드시 다음 형식으로 답변한다.

👕 상의:
추천 내용

👖 하의:
추천 내용

👟 신발:
추천 내용

🧥 겉옷:
추천 내용

🧢 추가 아이템:
추천 내용

💡 추천 이유:
짧은 설명
"""


        # =================================================
        # Groq 호출
        # =================================================

        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "너는 한국 학생들의 날씨별 "
                        "데일리 코디를 추천하는 AI 스타일 도우미다. "
                        "현실적이고 편하게 입을 수 있는 코디를 추천한다."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.7,

            max_tokens=500
        )


        # =================================================
        # 답변 가져오기
        # =================================================

        answer = response.choices[0].message.content


        return jsonify({

            "ok": True,

            "recommendation": answer

        })


    except Exception as e:

        print("❌ Groq 오류:", e)

        return jsonify({

            "ok": False,

            "error": str(e)

        }), 500


# =========================================================
# 기존 /api/recommend도 지원
# =========================================================

@app.route("/api/recommend", methods=["POST"])
def recommend():

    region = request.args.get("region", "수원")

    try:

        if client is None:

            return jsonify({
                "ok": False,
                "error": "GROQ_API_KEY가 설정되지 않았습니다."
            }), 500


        data = request.get_json() or {}

        region = data.get("region", region)

        weather_data = data.get("weather")


        if weather_data:

            today = weather_data

        else:

            weather = get_weather(region)

            today = weather.get("today", {})


        prompt = f"""
한국 학생을 위한 날씨별 데일리 코디를 추천해줘.

지역: {region}

날짜: {today.get("date", "-")}
날씨: {today.get("sky", "-")}
강수: {today.get("precipitation", "-")}
최저기온: {today.get("min_temp", "-")}°C
최고기온: {today.get("max_temp", "-")}°C
강수확률: {today.get("max_pop", 0)}%
습도: {today.get("min_humidity", "-")}~{today.get("max_humidity", "-")}%
최대풍속: {today.get("max_wind", "-")}m/s

학생이 일상적으로 입을 수 있는 현실적인 코디를 추천해줘.

👕 상의:
👖 하의:
👟 신발:
🧥 겉옷:
🧢 추가 아이템:

💡 추천 이유:
"""


        response = client.chat.completions.create(

            model="openai/gpt-oss-120b",

            messages=[

                {
                    "role": "system",
                    "content": "학생용 데일리 코디를 추천하는 AI 스타일 도우미야. 너는 무조건적으로 한국어를 사용해야 하며 이외 외국어를 사용하면 안돼"
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.7,

            max_tokens=500
        )


        answer = response.choices[0].message.content


        return jsonify({

            "ok": True,

            "answer": answer,

            "recommendation": answer

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

    print("")
    print("====================================")
    print("       🌤 Weather Outfit AI")
    print("====================================")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )