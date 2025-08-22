import streamlit as st
import requests
import json

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Local Discovery App", page_icon="📍", layout="wide")
st.title("📍 Smart Explore AI App")
st.write("Find restaurants, cafes, and interesting places near you!")

# Input fields
location = st.text_input("Enter location (e.g., Ahmedabad, India)", "Ahmedabad, India")
category = st.selectbox("Select Category", ["Restaurant", "Cafe", "Hotel", "Park", "Shopping Mall"])

# Your Foursquare API Key - IMPORTANT: Replace this with your actual key!
# NOTE: The provided key is being used. If it still doesn't work, please generate a new one from Foursquare.
FOURSQUARE_API_KEY = "5MUE3OVKAH1OVEOGWRVKDXBU1VTEGKCQZBGZ3T4AJZ4P0XYU"

# Category mapping for better search results
CATEGORY_MAPPING = {
    "Restaurant": "restaurant",
    "Cafe": "cafe",
    "Hotel": "hotel",
    "Park": "park",
    "Shopping Mall": "shopping"
}

# The single, correct V3 endpoint. The others are deprecated.
FOURSQUARE_ENDPOINT = "https://api.foursquare.com/v3/places/search"

# Trigger search
if st.button("🔍 Search"):
    if FOURSQUARE_API_KEY == "YOUR_API_KEY_HERE":
        st.error("Please replace 'YOUR_API_KEY_HERE' with your actual Foursquare API key.")
    else:
        with st.spinner("Fetching places..."):
            try:
                # IMPORTANT: Foursquare V3 API requires 'Bearer' prefix for the authorization header
                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {FOURSQUARE_API_KEY}"
                }

                # Parameters for the search
                params = {
                    "query": CATEGORY_MAPPING.get(category, category.lower()),
                    "near": location,
                    "limit": 10
                }

                response = requests.get(FOURSQUARE_ENDPOINT, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])

                    if results:
                        st.success(f"✅ Found {len(results)} places!")
                        for i, place in enumerate(results, 1):
                            # Create columns for a clean layout
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                st.subheader(f"{i}. {place.get('name', 'Unknown Name')}")

                                # Address
                                location_info = place.get('location', {})
                                address = location_info.get('formatted_address', 'Address not available')
                                st.write(f"📍 **Address:** {address}")

                                # Category
                                categories = place.get('categories', [])
                                if categories:
                                    category_name = categories[0].get('name', 'N/A')
                                    st.write(f"🏷️ **Category:** {category_name}")

                                # Distance (if available)
                                if 'distance' in place:
                                    st.write(f"📏 **Distance:** {place['distance']} meters")

                            with col2:
                                # Display category icon if available
                                if categories and 'icon' in categories[0]:
                                    icon_info = categories[0]['icon']
                                    if 'prefix' in icon_info and 'suffix' in icon_info:
                                        icon_url = f"{icon_info['prefix']}64{icon_info['suffix']}"
                                        st.image(icon_url, width=64)

                            st.markdown("---")
                    else:
                        st.warning(f"No results found for {category} near {location}.")

                elif response.status_code == 401:
                    st.error("❌ Invalid API Key. Please check your Foursquare API key and ensure it's valid.")
                    st.write("For the v3 API, the key must be placed in the 'Authorization' header with a 'Bearer' prefix.")

                elif response.status_code == 429:
                    st.error("❌ Rate limit exceeded. Please try again later.")

                else:
                    st.error(f"❌ API Request Failed. Status code: {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Network error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

