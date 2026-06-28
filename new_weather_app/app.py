from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "51a6cfcc3c5914eeae03cd61943630b1"
BASE_URL = "https://api.openweathermap.org/data/2.5/"

def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15, 1)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    alerts = []

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            # Current weather
            weather_response = requests.get(f"{BASE_URL}weather?q={city}&appid={API_KEY}").json()
            
            if weather_response.get("cod") == 200:
                weather_data = {
                    "city": weather_response["name"],
                    "temp": kelvin_to_celsius(weather_response["main"]["temp"]),
                    "description": weather_response["weather"][0]["description"].title(),
                    "humidity": weather_response["main"]["humidity"],
                    "wind_speed": weather_response["wind"]["speed"]
                }
                
                # Weather alerts (simple example)
                if "rain" in weather_response["weather"][0]["main"].lower():
                    alerts.append("⚠️ Heavy rain expected today! Take precautions.")
                elif weather_data["temp"] > 35:
                    alerts.append("⚠️ Heat alert! Stay hydrated.")

                # 5-day forecast
                forecast_response = requests.get(f"{BASE_URL}forecast?q={city}&appid={API_KEY}").json()
                forecast_data = []
                if forecast_response.get("cod") == "200":
                    # Pick data around midday for each day
                    for i in range(0, 40, 8):
                        item = forecast_response["list"][i]
                        forecast_data.append({
                            "date": item["dt_txt"].split(" ")[0],
                            "temp": kelvin_to_celsius(item["main"]["temp"]),
                            "description": item["weather"][0]["description"].title()
                        })

            else:
                alerts.append("⚠️ City not found. Please enter a valid city name.")

    return render_template("index.html", weather=weather_data, forecast=forecast_data, alerts=alerts)

if __name__ == "__main__":
    app.run(debug=True)
