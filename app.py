import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="Flight Bot (автопогода)", layout="wide")
st.title("Flight Bot: запис польотів")

# --- Вибір міста --- або GPS
city = st.text_input("Місто для погоди (залишити пустим для Kyiv)", "")

if city.strip() == "":
    city = "Kyiv"

weather = {}
api_key = "8cbaf4b112413073b4cce23af5f84b24"  # встав свій ключ OpenWeatherMap
url = f"https://api.openweathermap.org/data/2.5/weather?q={city.strip()}&units=metric&appid={api_key}"

try:
    data = requests.get(url).json()
    if data.get("main"):
        deg = data["wind"].get("deg", 0)
        directions = ["Пн", "ПнСх", "Сх", "ПдСх", "Пд", "ПдЗх", "Зх", "ПнЗх"]
        wind_dir = directions[round(deg / 45) % 8]

        weather = {
            "Температура": data["main"]["temp"],
            "Вологість": data["main"]["humidity"],
            "Швидкість вітру": data["wind"]["speed"],
            "Напрямок вітру": wind_dir,
            "Видимість": data.get("visibility", "N/A")
        }
        st.subheader(f"Погода у {city}")
        st.write(weather)
    else:
        st.error("Не вдалося отримати дані погоди")
except Exception as e:
    st.error(f"Помилка при отриманні погоди: {e}")

# --- Дані польоту ---
flight_date = st.date_input("Дата польоту", datetime.today())
flight_time = st.time_input("Час польоту", datetime.now().time())
pilot = st.text_input("Пілот")
crew = st.text_area("Додатковий екіпаж (через кому)")
complex_choice = st.selectbox("Виберіть комплекс", ["Комплекс A", "Комплекс B", "Комплекс C"])
board_number = st.text_input("Номер борта")
flights_count = st.number_input("Кількість вильотів", min_value=1, step=1)
flight_duration = st.text_input("Час у повітрі (год:хв)")
flight_distance = st.number_input("Дальність (км)", min_value=0)
flight_altitude = st.number_input("Висота (м)", min_value=0)
flight_type = st.selectbox("Тип вильоту", ["Тренувальний", "Бойовий", "Транспортний"])
board_status = st.text_area("Стан борта після польоту")

# --- Збереження у CSV ---
if st.button("Зберегти запис"):
    data_row = {
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

    df = pd.DataFrame([data_row])
    df.to_csv("flight_log.csv", mode='a', index=False, header=not pd.io.common.file_exists("flight_log.csv"))
    st.success("Запис збережено!")
