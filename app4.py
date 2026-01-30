import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import os

# --------------------------------------------------
# ДОПОМІЖНІ ФУНКЦІЇ
# --------------------------------------------------
def safe_filename(text: str) -> str:
    return (
        str(text)
        .strip()
        .replace(" ", "_")
        .replace("/", "-")
        .replace("\\", "-")
    )

# --------------------------------------------------
# НАЛАШТУВАННЯ СТОРІНКИ
# --------------------------------------------------
st.set_page_config(
    page_title="Flight Bot",
    layout="wide"
)

st.title("✈️ Flight Bot — журнал польотів")

# --------------------------------------------------
# ЧАСОВА ЗОНА (УКРАЇНА)
# --------------------------------------------------
ukraine_tz = ZoneInfo("Europe/Kyiv")
now_ua = datetime.now(ukraine_tz)

# --------------------------------------------------
# ПОГОДА
# --------------------------------------------------
st.subheader("🌦️ Погодні умови")

city_input = st.text_input("Місто для погоди", "Kyiv")
city = city_input.strip()

weather = {}

API_KEY = "8cbaf4b112413073b4cce23af5f84b24"  # 🔴 ВСТАВ СВІЙ КЛЮЧ OpenWeatherMap

if city:
    try:
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&units=metric&appid={API_KEY}"
        )
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("main"):
            deg = data["wind"].get("deg", 0)
            directions = ["Пн", "ПнСх", "Сх", "ПдСх", "Пд", "ПдЗх", "Зх", "ПнЗх"]
            wind_dir = directions[int((deg + 22.5) // 45) % 8]

            weather = {
                "Температура": data["main"]["temp"],
                "Вологість": data["main"]["humidity"],
                "Швидкість вітру": data["wind"]["speed"],
                "Напрямок вітру": wind_dir,
                "Видимість": data.get("visibility", "Н/Д")
            }

            st.success(f"Погода у {city}")
            st.json(weather)
        else:
            st.error("Не вдалося отримати дані погоди")
    except Exception as e:
        st.error(f"Помилка погоди: {e}")

# --------------------------------------------------
# ДАНІ ПОЛЬОТУ
# --------------------------------------------------
st.subheader("🛫 Дані польоту")

flight_date = st.date_input("Дата польоту", now_ua.date())
flight_time = st.time_input("Час польоту", now_ua.time())

pilot = st.text_input("Пілот")
crew = st.text_area("Екіпаж (через кому)")

complex_choice = st.selectbox(
    "Комплекс",
    ["P1-SUN", "STING", "AHII-S", "БЛИСКАВКА"]
)

board_number = st.text_input("Номер борта")

flights_count = st.number_input(
    "Кількість вильотів",
    min_value=1,
    step=1
)

flight_duration = st.text_input("Час у повітрі (год:хв)")
flight_distance = st.number_input("Дальність (км)", min_value=0)
flight_altitude = st.number_input("Висота (м)", min_value=0)

flight_type = st.selectbox(
    "Тип вильоту",
    ["НТП", "БР", "Заміри МУ"]
)

board_status = st.text_area("Стан борта після польоту")

# --------------------------------------------------
# ІМʼЯ ФАЙЛУ
# --------------------------------------------------
complex_safe = safe_filename(complex_choice)
board_safe = safe_filename(board_number if board_number else "NOBOARD")

date_str = now_ua.strftime("%Y%m%d")
time_str = now_ua.strftime("%H%M")

file_base_name = f"{complex_safe}_{board_safe}_{date_str}_{time_str}"

# --------------------------------------------------
# ЗБЕРЕЖЕННЯ В CSV
# --------------------------------------------------
if st.button("💾 Зберегти запис"):
    row = {
        "Дата": flight_date,
        "Час": flight_time,
        "Місто": city,
        "Температура": weather.get("Температура", ""),
        "Вологість": weather.get("Вологість", ""),
        "Швидкість вітру": weather.get("Швидкість вітру", ""),
        "Напрямок вітру": weather.get("Напрямок вітру", ""),
        "Видимість": weather.get("Видимість", ""),
        "Пілот": pilot,
        "Екіпаж": crew,
        "Комплекс": complex_choice,
        "Номер борта": board_number,
        "Кількість вильотів": flights_count,
        "Час у повітрі": flight_duration,
        "Дальність": flight_distance,
        "Висота": flight_altitude,
        "Тип вильоту": flight_type,
        "Стан борта": board_status
    }

    df = pd.DataFrame([row])

    csv_name = f"{file_base_name}.csv"
    df.to_csv(csv_name, index=False)

    st.success(f"Запис збережено: {csv_name}")

# --------------------------------------------------
# TXT ЗВІТ
# --------------------------------------------------
st.subheader("📄 Текстовий звіт")

report_text = f"""
ЗВІТ ПРО ПОЛІТ
====================================

Дата: {flight_date}
Час: {flight_time}

ПОГОДА:
Місто: {city}
Температура: {weather.get("Температура", "")} °C
Вологість: {weather.get("Вологість", "")} %
Швидкість вітру: {weather.get("Швидкість вітру", "")} м/с
Напрямок вітру: {weather.get("Напрямок вітру", "")}
Видимість: {weather.get("Видимість", "")}

ЕКІПАЖ:
Пілот: {pilot}
Екіпаж: {crew}

БОРТ:
Комплекс: {complex_choice}
Номер борта: {board_number}

ПОЛІТ:
Кількість вильотів: {flights_count}
Час у повітрі: {flight_duration}
Дальність: {flight_distance} км
Висота: {flight_altitude} м
Тип вильоту: {flight_type}

СТАН ПІСЛЯ ПОЛЬОТУ:
{board_status}
"""

st.download_button(
    "⬇️ Завантажити TXT-звіт",
    report_text,
    file_name=f"{file_base_name}.txt",
    mime="text/plain"
)

# --------------------------------------------------
# РЕДАГУВАННЯ TXT
# --------------------------------------------------
st.subheader("✏️ Редагувати існуючий TXT")

uploaded_file = st.file_uploader(
    "Завантаж TXT файл",
    type=["txt"]
)

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")

    edited_text = st.text_area(
        "Редагування",
        content,
        height=350
    )

    st.download_button(
        "💾 Завантажити відредагований файл",
        edited_text,
        file_name="flight_report_edited.txt",
        mime="text/plain"
    )
