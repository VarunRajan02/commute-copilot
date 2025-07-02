
import streamlit as st
import requests
from datetime import datetime, timedelta

# === Streamlit UI ===
st.title("🚆 Commute Copilot")
st.markdown("Get real-time train recommendations between Düsseldorf Hbf and Essen Hbf based on your working hours.")

api_key = st.text_input("Enter your Deutsche Bahn API Key", type="password")

if api_key:
    BASE_URL = "https://api.deutschebahn.com/freeplan/v1"
    HOME_STATION = "Düsseldorf Hbf"
    OFFICE_STATION = "Essen Hbf"
    WORK_START = "09:00"
    WORK_END = "17:00"

    def get_station_id(station_name):
        url = f"{BASE_URL}/location.name?input={station_name}"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data[0]['id'] if data else None
        return None

    def get_departures(station_id, direction_id, time):
        url = f"{BASE_URL}/departureBoard?id={station_id}&direction={direction_id}&dateTime={time}"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def recommend_train(departures, after_time):
        for train in departures:
            try:
                dep_time = datetime.fromisoformat(train['dateTime'])
                if dep_time.time() > after_time:
                    return train
            except:
                continue
        return None

    now = datetime.now()
    today_5pm = now.replace(hour=17, minute=0, second=0, microsecond=0)
    tomorrow_9am = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

    home_id = get_station_id(HOME_STATION)
    office_id = get_station_id(OFFICE_STATION)

    if home_id and office_id:
        # Evening commute
        evening_departures = get_departures(office_id, home_id, today_5pm.isoformat())
        evening_train = recommend_train(evening_departures, today_5pm.time())

        # Morning commute
        morning_departures = get_departures(home_id, office_id, tomorrow_9am.isoformat())
        morning_train = recommend_train(morning_departures, datetime.strptime(WORK_START, "%H:%M").time())

        st.subheader("📅 Evening Commute (Today)")
        if evening_train:
            st.write(f"**Train:** {evening_train.get('name')}")
            st.write(f"**Departure:** {evening_train.get('dateTime')}")
            st.write(f"**Platform:** {evening_train.get('platform')}")
            st.write(f"**Direction:** {evening_train.get('direction')}")
        else:
            st.write("No suitable evening train found.")

        st.subheader("📅 Morning Commute (Tomorrow)")
        if morning_train:
            st.write(f"**Train:** {morning_train.get('name')}")
            st.write(f"**Departure:** {morning_train.get('dateTime')}")
            st.write(f"**Platform:** {morning_train.get('platform')}")
            st.write(f"**Direction:** {morning_train.get('direction')}")
        else:
            st.write("No suitable morning train found.")
    else:
        st.error("Could not retrieve station IDs. Please check your API key and try again.")
