import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Local Discovery App", page_icon="📍", layout="wide")
st.title("📍 Local Discovery App")
st.write("Find restaurants, cafes, and interesting places near you!")

# Input fields
location = st.text_input("Enter location (e.g., Ahmedabad, India)", "Ahmedabad, India")
category = st.selectbox("Select Category", ["Restaurant", "Cafe", "Hotel", "Park", "Shopping Mall"])
min_rating = st.slider("Minimum Rating", 0.0, 10.0, 4.0)

# Foursquare Service API Key
FOURSQUARE_API_KEY = "X5IILNDSTQROTBHVS52WA1W32EAYAE4NP42OH1VDAX3OBKVS"

CATEGORY_ID_MAPPING = {
    "Restaurant": "13065",
    "Cafe": "13032",
    "Hotel": "19014",
    "Park": "16032",
    "Shopping Mall": "19009"
}

FOURSQUARE_ENDPOINT = "https://api.foursquare.com/v3/places/search"

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        try:
            geo_url = "https://photon.komoot.io/api/"
            geo_params = {"q": location}
            geo_response = requests.get(geo_url, params=geo_params, timeout=10)

            if geo_response.status_code == 200 and geo_response.json().get('features'):
                lat = geo_response.json()['features'][0]['geometry']['coordinates'][1]
                lon = geo_response.json()['features'][0]['geometry']['coordinates'][0]

                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Bearer {FOURSQUARE_API_KEY}"
                }

                params = {
                    "ll": f"{lat},{lon}",
                    "categories": CATEGORY_ID_MAPPING.get(category, "13065"),
                    "limit": 20,
                    "fields": "fsq_id,name,location,categories,rating,photos,geocodes,hours"
                }

                response = requests.get(FOURSQUARE_ENDPOINT, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])

                    # Filter by rating
                    filtered_results = [place for place in results if place.get("rating", 0) >= min_rating]

                    if filtered_results:
                        st.success(f"✅ Found {len(filtered_results)} places with rating ≥ {min_rating}")
                        map = folium.Map(location=[lat, lon], zoom_start=13)
                        places_data = []

                        for i, place in enumerate(filtered_results, 1):
                            name = place.get("name", "Unknown")
                            loc = place.get("location", {})
                            address = loc.get("formatted_address", "Address not available")
                            categories = place.get("categories", [])
                            category_name = categories[0].get("name", "N/A") if categories else "N/A"
                            rating = place.get("rating", "Not rated")
                            lat_p = place.get("geocodes", {}).get("main", {}).get("latitude", lat)
                            lon_p = place.get("geocodes", {}).get("main", {}).get("longitude", lon)
                            is_open = place.get("hours", {}).get("is_open", None)

                            # Distance
                            distance_km = geodesic((lat, lon), (lat_p, lon_p)).km

                            # Map marker
                            folium.Marker(
                                location=[lat_p, lon_p],
                                popup=f"{name}\n{address}",
                                tooltip=name
                            ).add_to(map)

                            # Display
                            st.subheader(f"{i}. {name}")
                            st.write(f"📍 **Address:** {address}")
                            st.write(f"🏷️ **Category:** {category_name}")
                            st.write(f"⭐ **Rating:** {rating}")
                            st.write(f"📏 **Distance:** {distance_km:.2f} km")

                            if is_open is not None:
                                st.write("🟢 Open Now" if is_open else "🔴 Closed")

                            # Photo
                            photos = place.get("photos", [])
                            if photos:
                                photo = photos[0]
                                photo_url = f"{photo['prefix']}original{photo['suffix']}"
                                st.image(photo_url, width=300)

                            # Google Maps link
                            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat_p},{lon_p}"
                            st.markdown(f"[🗺️ Get Directions]({maps_url})", unsafe_allow_html=True)

                            st.markdown("---")

                            # Collect for export
                            places_data.append({
                                "Name": name,
                                "Address": address,
                                "Category": category_name,
                                "Rating": rating,
                                "Distance (km)": round(distance_km, 2),
                                "Open Now": "Yes" if is_open else "No",
                                "Latitude": lat_p,
                                "Longitude": lon_p
                            })

                        # Map view
                        st.subheader("🗺️ Map View")
                        st_folium(map, width=700, height=500)

                        # Export
                        df = pd.DataFrame(places_data)
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button("📥 Download Results as CSV", data=csv, file_name="places.csv", mime="text/csv")

                    else:
                        st.warning(f"No places found with rating ≥ {min_rating} near {location}.")
                else:
                    st.error(f"❌ API Request Failed. Status code: {response.status_code}")
                    st.code(response.text)
            else:
                st.error("❌ Could not get location coordinates. Please check the spelling of the location.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 📝 Tips:")
st.markdown("""
- Use precise location names for better results.
- Ratings and photos may not be available for all places.
- You can download the results and use them for analysis or sharing.
""")
