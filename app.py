import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="SmartExploreAI", page_icon="📍", layout="wide")
st.title("📍 SmartExploreAI Prototype")
st.write("Discover nearby places using open data sources.")

# Input fields
location = st.text_input("Enter location (e.g., Ahmedabad, India)", "Ahmedabad, India")
category = st.selectbox("Select Category", ["Restaurant", "Cafe", "Hotel", "Park", "Shopping Mall"])

# Overpass tags for each category
OVERPASS_TAGS = {
    "Restaurant": "amenity=restaurant",
    "Cafe": "amenity=cafe",
    "Hotel": "tourism=hotel",
    "Park": "leisure=park",
    "Shopping Mall": "shop=mall"
}

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Locating places..."):
        try:
            # Geocode location using Photon
            geo_url = "https://photon.komoot.io/api/"
            geo_params = {"q": location}
            geo_response = requests.get(geo_url, params=geo_params, timeout=10)

            if geo_response.status_code == 200 and geo_response.json().get('features'):
                lat = geo_response.json()['features'][0]['geometry']['coordinates'][1]
                lon = geo_response.json()['features'][0]['geometry']['coordinates'][0]

                # Build Overpass query
                tag = OVERPASS_TAGS.get(category, "amenity=restaurant")
                overpass_query = f"""
                [out:json];
                node[{tag}](around:3000,{lat},{lon});
                out;
                """
                overpass_url = "https://overpass-api.de/api/interpreter"
                response = requests.post(overpass_url, data=overpass_query, timeout=20)

                if response.status_code == 200:
                    data = response.json()
                    elements = data.get("elements", [])

                    if elements:
                        st.success(f"✅ Found {len(elements)} {category.lower()}s near {location}")
                        map = folium.Map(location=[lat, lon], zoom_start=13)
                        places_data = []

                        for i, place in enumerate(elements, 1):
                            name = place.get("tags", {}).get("name", "Unnamed")
                            lat_p = place.get("lat", lat)
                            lon_p = place.get("lon", lon)
                            distance_km = geodesic((lat, lon), (lat_p, lon_p)).km

                            folium.Marker(
                                location=[lat_p, lon_p],
                                popup=f"{name}",
                                tooltip=name
                            ).add_to(map)

                            st.subheader(f"{i}. {name}")
                            st.write(f"📏 **Distance:** {distance_km:.2f} km")
                            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={lat_p},{lon_p}"
                            st.markdown(f"[🗺️ Get Directions]({maps_url})", unsafe_allow_html=True)
                            st.markdown("---")

                            places_data.append({
                                "Name": name,
                                "Distance (km)": round(distance_km, 2),
                                "Latitude": lat_p,
                                "Longitude": lon_p
                            })

                        st.subheader("🗺️ Map View")
                        st_folium(map, width=700, height=500)

                        df = pd.DataFrame(places_data)
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button("📥 Download Results as CSV", data=csv, file_name="places.csv", mime="text/csv")
                    else:
                        st.warning(f"No {category.lower()}s found near {location}.")
                else:
                    st.error(f"❌ Overpass API error. Status code: {response.status_code}")
            else:
                st.error("❌ Could not get location coordinates. Please check the spelling.")

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 📝 Notes:")
st.markdown("""
- This prototype uses open data from OpenStreetMap via Overpass API.
- No API key is required.
- Results may vary based on location coverage.
""")
