import requests
from datetime import datetime
from collections import defaultdict
from tabulate import tabulate

def guide_to_get_api_key():
    print("\n🔑 How to Get a Free API Key from OpenWeatherMap:")
    print("1. Visit https://openweathermap.org/api")
    print("2. Create an account or sign in.")
    print("3. Go to 'API keys' at https://home.openweathermap.org/api_keys")
    print("4. Click 'Create Key', name it, and copy the generated key.")
    print("5. Paste the key below when prompted.\n")

def get_forecast_data(location, api_key):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Error fetching forecast:", response.json().get("message", "Unknown error"))
        return None

def summarize_forecast(data):
    forecast_by_day = defaultdict(list)

    for entry in data['list']:
        date = datetime.fromtimestamp(entry['dt']).strftime('%A')
        temp = entry['main']['temp']
        humidity = entry['main']['humidity']
        condition = entry['weather'][0]['main']
        forecast_by_day[date].append((temp, humidity, condition))

    table = []
    for i, (day, records) in enumerate(forecast_by_day.items()):
        if i >= 3:  # Limit to 3 days
            break
        avg_temp = round(sum(r[0] for r in records) / len(records), 1)
        avg_humidity = round(sum(r[1] for r in records) / len(records))
        most_common_condition = max(set([r[2] for r in records]), key=[r[2] for r in records].count)
        table.append([day, f"{avg_temp} °C", f"{avg_humidity}%", most_common_condition])

    return table

def main():
    print("🌍 3-Day Weather Forecast App")
    guide_to_get_api_key()

    location = input("Enter city name or ZIP code: ")
    api_key = input("Enter your OpenWeatherMap API key: ")

    forecast_data = get_forecast_data(location, api_key)
    if forecast_data:
        table = summarize_forecast(forecast_data)
        print("\n📅 3-Day Forecast")
        print(tabulate(table, headers=["Day", "Avg Temp", "Avg Humidity", "Condition"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    main()
