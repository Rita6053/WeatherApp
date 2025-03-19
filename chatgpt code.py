import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
from datetime import datetime, timedelta

# Define image size constants
IMAGE_WIDTH = 300
IMAGE_HEIGHT = 250


def get_weather():
    # Coordinates for Durbanville, South Africa
    latitude = "-33.83"
    longitude = "18.65"

    # OpenMeteo API URL - free, no authentication needed
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min&current_weather=true&timezone=auto&past_days=1&forecast_days=2"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # Process the data
        current_weather = weather_data['current_weather']
        daily_weather = weather_data['daily']

        # Get today's weather
        current_temp = current_weather['temperature']
        current_weathercode = current_weather['weathercode']
        current_windspeed = current_weather['windspeed']
        current_desc = get_weather_description(current_weathercode)

        weather_label.config(text=f"Today: {current_desc}, {current_temp}°C, Wind: {current_windspeed} km/h")

        # Get yesterday's weather (index 0 because of past_days=1)
        yesterday_weathercode = daily_weather['weathercode'][0]
        yesterday_temp_max = daily_weather['temperature_2m_max'][0]
        yesterday_temp_min = daily_weather['temperature_2m_min'][0]
        yesterday_desc = get_weather_description(yesterday_weathercode)

        weather_yesterday_label.config(text=f"Yesterday: {yesterday_desc}, {yesterday_temp_min}-{yesterday_temp_max}°C")

        # Get tomorrow's weather (index 2 because index 1 is today)
        tomorrow_weathercode = daily_weather['weathercode'][2]
        tomorrow_temp_max = daily_weather['temperature_2m_max'][2]
        tomorrow_temp_min = daily_weather['temperature_2m_min'][2]
        tomorrow_desc = get_weather_description(tomorrow_weathercode)

        weather_tomorrow_label.config(text=f"Tomorrow: {tomorrow_desc}, {tomorrow_temp_min}-{tomorrow_temp_max}°C")

        # Update background based on current conditions
        update_background(current_desc)

    except requests.exceptions.RequestException as e:
        weather_label.config(text=f"Error: {e}")
        messagebox.showerror("Error", f"Failed to fetch weather data: {e}")


def get_weather_description(weathercode):
    # WMO Weather interpretation codes (WW)
    # https://open-meteo.com/en/docs
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(weathercode, "Unknown")


def update_background(weather_info):
    weather_info = weather_info.lower()
    if "clear" in weather_info or "mainly clear" in weather_info:
        image_path = "sun.jpg"
    elif "rain" in weather_info or "drizzle" in weather_info or "shower" in weather_info:
        image_path = "rain.jpg"
    elif "cloud" in weather_info or "overcast" in weather_info:
        image_path = "cloud.jpg"
    else:
        image_path = "default.jpg"

    try:
        bg_image = Image.open(image_path)
        bg_image = bg_image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        background_label.config(image=bg_photo)
        background_label.image = bg_photo
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {e}")


# Create the main application window
root = tk.Tk()
root.title("Weather App")
root.geometry(f"{IMAGE_WIDTH}x{IMAGE_HEIGHT + 50}")  # Add a small padding for the button
root.resizable(False, False)  # Prevent window resizing

# Create a frame to hold all elements
main_frame = tk.Frame(root, width=IMAGE_WIDTH, height=IMAGE_HEIGHT + 50)
main_frame.pack(fill="both", expand=True)

# Add background image
background_label = tk.Label(main_frame)
background_label.place(x=0, y=0, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)

# Create a frame for the text labels with a border
text_frame = tk.Frame(main_frame, bd=2, relief=tk.RIDGE, bg="white")
text_frame.place(relx=0.5, rely=0.3, anchor="center", width=IMAGE_WIDTH * 0.8, height=IMAGE_HEIGHT * 0.4)

# Add text labels inside the text frame with smaller font size
weather_yesterday_label = tk.Label(text_frame, text="Fetching yesterday's weather...",
                                   wraplength=IMAGE_WIDTH * 0.7, justify="center", bg="white", font=("Arial", 8))
weather_yesterday_label.pack(pady=3)

weather_label = tk.Label(text_frame, text="Fetching weather...",
                         wraplength=IMAGE_WIDTH * 0.7, justify="center", bg="white", font=("Arial", 9, "bold"))
weather_label.pack(pady=3)

weather_tomorrow_label = tk.Label(text_frame, text="Fetching tomorrow's weather...",
                                  wraplength=IMAGE_WIDTH * 0.7, justify="center", bg="white", font=("Arial", 8))
weather_tomorrow_label.pack(pady=3)

# Add refresh button at the bottom
refresh_button = tk.Button(main_frame, text="Refresh Weather", command=get_weather)
refresh_button.place(relx=0.5, rely=0.95, anchor="center")

get_weather()
root.mainloop()