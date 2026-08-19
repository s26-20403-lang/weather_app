// =========================================================
// 날씨 불러오기
// =========================================================

async function loadWeather() {

    const loading = document.getElementById("loading");
    const error = document.getElementById("error");

    const todayCard = document.getElementById("todayCard");
    const tomorrowCard = document.getElementById("tomorrowCard");

    const regionSelect = document.getElementById("regionSelect");


    // 지역 선택창이 없으면 종료
    if (!regionSelect) {
        console.error("❌ regionSelect를 찾을 수 없습니다.");
        return;
    }


    const region = regionSelect.value;


    // 로딩 시작
    if (loading) {
        loading.classList.remove("hidden");
    }

    if (error) {
        error.classList.add("hidden");
    }

    if (todayCard) {
        todayCard.classList.add("hidden");
    }

    if (tomorrowCard) {
        tomorrowCard.classList.add("hidden");
    }


    try {

        const response = await fetch(
            `/api/weather?region=${encodeURIComponent(region)}&t=${Date.now()}`,
            {
                cache: "no-store"
            }
        );


        if (!response.ok) {
            throw new Error(
                `날씨 서버 오류 (${response.status})`
            );
        }


        const data = await response.json();


        if (!data.ok) {
            throw new Error(
                data.error || "날씨를 불러오지 못했습니다."
            );
        }


        const today = data.weather.today;
        const tomorrow = data.weather.tomorrow;


        // 오늘
        fillDay(
            "today",
            today
        );


        // 내일
        fillDay(
            "tomorrow",
            tomorrow
        );


        // 로딩 종료
        if (loading) {
            loading.classList.add("hidden");
        }


        // 카드 표시
        if (todayCard) {
            todayCard.classList.remove("hidden");
        }

        if (tomorrowCard) {
            tomorrowCard.classList.remove("hidden");
        }


    } catch (e) {

        console.error("❌ 날씨 오류:", e);


        if (loading) {
            loading.classList.add("hidden");
        }


        if (error) {

            error.textContent =
                "오류: " + e.message;

            error.classList.remove("hidden");

        }

    }

}


// =========================================================
// 날짜별 날씨 카드 표시
// =========================================================

function fillDay(prefix, day) {

    if (!day) {
        console.warn(
            `${prefix} 날씨 데이터가 없습니다.`
        );
        return;
    }


    // 날짜
    const dateElement =
        document.getElementById(
            `${prefix}Date`
        );

    if (dateElement) {
        dateElement.textContent =
            day.date ?? "-";
    }


    // 날씨 상태
    const skyElement =
        document.getElementById(
            `${prefix}Sky`
        );

    if (skyElement) {
        skyElement.textContent =
            day.sky ?? "-";
    }


    // 강수
    const precipitationElement =
        document.getElementById(
            `${prefix}Precipitation`
        );

    if (precipitationElement) {
        precipitationElement.textContent =
            day.precipitation ?? "-";
    }


    // 최고기온
    const max =
        day.max_temp == null
            ? "-"
            : Math.round(
                Number(day.max_temp)
            );


    // 최저기온
    const min =
        day.min_temp == null
            ? "-"
            : Math.round(
                Number(day.min_temp)
            );


    const maxElement =
        document.getElementById(
            `${prefix}Max`
        );

    if (maxElement) {
        maxElement.textContent = max;
    }


    // 두 번째 최고기온 표시 영역
    const max2Element =
        document.getElementById(
            `${prefix}Max2`
        );

    if (max2Element) {
        max2Element.textContent = max;
    }


    // 최저기온 표시
    const minElement =
        document.getElementById(
            `${prefix}Min`
        );

    if (minElement) {
        minElement.textContent = min;
    }


    // 강수확률
    const popElement =
        document.getElementById(
            `${prefix}Pop`
        );


    if (popElement) {

        if (day.max_pop == null) {

            popElement.textContent = "-";

        } else {

            popElement.textContent =
                `${Math.round(
                    Number(day.max_pop)
                )}%`;

        }

    }


    // 습도
    const humidityElement =
        document.getElementById(
            `${prefix}Humidity`
        );


    if (humidityElement) {

        if (
            day.min_humidity == null ||
            day.max_humidity == null
        ) {

            humidityElement.textContent = "-";

        } else {

            humidityElement.textContent =
                `${Math.round(
                    Number(day.min_humidity)
                )}~${Math.round(
                    Number(day.max_humidity)
                )}%`;

        }

    }


    // 최대풍속
    const windElement =
        document.getElementById(
            `${prefix}Wind`
        );


    if (windElement) {

        if (day.max_wind == null) {

            windElement.textContent = "-";

        } else {

            windElement.textContent =
                `${Number(
                    day.max_wind
                ).toFixed(1)}m/s`;

        }

    }

}


// =========================================================
// 지역 변경
// =========================================================

const regionSelect =
    document.getElementById(
        "regionSelect"
    );


if (regionSelect) {

    regionSelect.addEventListener(
        "change",
        loadWeather
    );

}


// =========================================================
// Groq AI 코디 추천
// =========================================================

const recommendBtn =
    document.getElementById(
        "recommendBtn"
    );


if (recommendBtn) {

    recommendBtn.addEventListener(
        "click",
        async () => {

            const button =
                document.getElementById(
                    "recommendBtn"
                );


            const text =
                document.getElementById(
                    "recommendText"
                );


            const regionElement =
                document.getElementById(
                    "regionSelect"
                );


            if (!regionElement) {

                console.error(
                    "❌ regionSelect를 찾을 수 없습니다."
                );

                return;

            }


            const region =
                regionElement.value;


            // 버튼 잠금
            button.disabled = true;


            // 버튼 문구
            button.textContent =
                "🤖 Groq가 코디를 생각하는 중...";


            // 추천 영역 표시
            if (text) {

                text.classList.remove(
                    "hidden"
                );


                text.textContent =
                    "오늘 날씨를 분석하고 있어요...";

            }


            try {

                // =========================================
                // Flask의 /api/outfit 호출
                // =========================================

                const response =
                    await fetch(
                        `/api/outfit?region=${encodeURIComponent(region)}&t=${Date.now()}`,
                        {
                            method: "GET",
                            cache: "no-store"
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        `AI 서버 오류 (${response.status})`
                    );

                }


                const data =
                    await response.json();


                if (!data.ok) {

                    throw new Error(
                        data.error ||
                        "AI 코디 추천에 실패했습니다."
                    );

                }


                // =========================================
                // Groq 답변 출력
                // =========================================

                if (text) {

                    text.textContent =
                        data.recommendation ||
                        "코디 추천 결과가 없습니다.";

                }


            } catch (error) {

                console.error(
                    "❌ Groq 코디 추천 오류:",
                    error
                );


                if (text) {

                    text.textContent =
                        "❌ 코디 추천에 실패했어요.\n\n" +
                        error.message;

                }

            } finally {

                // 버튼 다시 활성화
                button.disabled = false;


                button.textContent =
                    "🤖 AI 코디 추천받기";

            }

        }
    );

}


// =========================================================
// 페이지가 열리면 날씨 자동 로딩
// =========================================================

loadWeather();