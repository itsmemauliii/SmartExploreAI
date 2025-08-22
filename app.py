import streamlit as st
import requests

# Load API key from Streamlit secrets
FOURSQUARE_API_KEY = st.secrets["FOURSQUARE_API_KEY"]
headers = {"Authorization": FOURSQUARE_API_KEY}

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Local Discovery App", page_icon="📍", layout="wide")

st.title("📍 Local Discovery App")
st.write("Find restaurants, cafes, and interesting places near you!")

# Input fields
location = st.text_input("Enter location (e.g., Ahmedabad, India)", "Ahmedabad, India")
category = st.selectbox("Select Category", ["Restaurant", "Cafe", "Hotel", "Park", "Shopping Mall"])

# Your Foursquare API Key
FOURSQUARE_API_KEY = "YOUR_API_KEY_HERE"  # 🔑 Replace with your key
headers = {"Authorization": FOURSQUARE_API_KEY}

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        url = "https://api.foursquare.com/v3/places/search"
        params = {
            "query": category,
            "near": location,
            "limit": 10
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                for place in results:
                    st.subheader(place["name"])
                    st.write(f"📍 Address: {place.get('location', {}).get('formatted_address', 'N/A')}")
                    st.write(f"⭐ Category: {place.get('categories', [{}])[0].get('name', 'N/A')}")
                    st.markdown("---")
            else:
                st.warning("No results found! Try another location or category.")
        else:
            st.error("Error fetching data. Check your API key or request limits.")
