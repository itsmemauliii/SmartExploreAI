import streamlit as st
import requests
import json

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="Local Discovery App", page_icon="📍", layout="wide")
st.title("📍 Local Discovery App")
st.write("Find restaurants, cafes, and interesting places near you!")

# Input fields
location = st.text_input("Enter location (e.g., Ahmedabad, India)", "Ahmedabad, India")
category = st.selectbox("Select Category", ["Restaurant", "Cafe", "Hotel", "Park", "Shopping Mall"])

# Your Foursquare API Key (Make sure this is a valid FSQ Places API key)
FOURSQUARE_API_KEY = "fsq3HkSKnobCiEEZdDKEO9WA8xUMxxlzCpOBbt/dczhhp1s="  # Your actual API key

# Category mapping for better search results
CATEGORY_MAPPING = {
    "Restaurant": "restaurant",
    "Cafe": "cafe",
    "Hotel": "hotel",
    "Park": "park",
    "Shopping Mall": "shopping mall"
}

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        try:
            # Use the current FSQ Places API endpoint
            url = "https://api.foursquare.com/v3/places/search"
            headers = {
                "Authorization": FOURSQUARE_API_KEY,
                "Accept": "application/json"
            }
            params = {
                "query": CATEGORY_MAPPING.get(category, category.lower()),
                "near": location,
                "limit": 10,
                "sort": "DISTANCE"  # Sort by distance for better results
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    st.success(f"Found {len(results)} places!")
                    
                    for i, place in enumerate(results, 1):
                        # Create columns for better layout
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
                            
                            # Additional info if available
                            if 'rating' in place:
                                st.write(f"⭐ **Rating:** {place['rating']}/10")
                        
                        with col2:
                            # Display category icon if available
                            if categories and 'icon' in categories[0]:
                                icon_info = categories[0]['icon']
                                if 'prefix' in icon_info and 'suffix' in icon_info:
                                    icon_url = f"{icon_info['prefix']}64{icon_info['suffix']}"
                                    st.image(icon_url, width=64)
                        
                        st.markdown("---")
                else:
                    st.warning("No results found! Try another location or category.")
                    
            elif response.status_code == 401:
                st.error("❌ Invalid API key. Please check your Foursquare API credentials.")
                st.info("Make sure you're using a valid FSQ Places API key from https://developer.foursquare.com/")
            elif response.status_code == 403:
                st.error("❌ Access forbidden. Check if your API key has Places API access.")
            elif response.status_code == 410:
                st.error("❌ API endpoint deprecated. This might indicate an issue with the API version or endpoint.")
                st.info("Please verify you're using the latest Foursquare Places API documentation.")
            elif response.status_code == 429:
                st.error("❌ Rate limit exceeded. Please wait and try again later.")
            else:
                st.error(f"❌ Error fetching data. Status code: {response.status_code}")
                st.error(f"Response: {response.text}")
                
                # Additional debugging info
                if st.checkbox("Show debug info"):
                    st.write("Request URL:", url)
                    st.write("Request headers:", headers)
                    st.write("Request params:", params)
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: {str(e)}")
        except json.JSONDecodeError as e:
            st.error(f"❌ Error parsing response: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")

# Add footer with instructions
st.markdown("---")
st.markdown("### 📝 Instructions:")
st.markdown("""
1. Enter a location (city, address, or landmark)
2. Select a category you're interested in
3. Click Search to find nearby places
4. Make sure you have a valid Foursquare API key

**Note:** You need a valid Foursquare API key to use this app. Get one from [Foursquare Developer Portal](https://developer.foursquare.com/).
""")

# Test API connection (optional - for debugging)
if st.checkbox("🔧 Test API Connection"):
    st.write("Testing API connection...")
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Authorization": FOURSQUARE_API_KEY,
            "Accept": "application/json"
        }
        params = {
            "query": "restaurant",
            "near": "Ahmedabad, India",
            "limit": 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        st.write(f"Status Code: {response.status_code}")
        st.write(f"Request URL: {response.url}")
        
        if response.status_code == 200:
            st.success("✅ API connection successful!")
            data = response.json()
            st.json(data)
        elif response.status_code == 410:
            st.error("❌ API endpoint is deprecated. Please check Foursquare documentation for updates.")
        elif response.status_code == 401:
            st.error("❌ Authentication failed. Please verify your API key.")
        else:
            st.error(f"❌ API connection failed: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Connection test failed: {str(e)}")

# Alternative: Try Google Places API as backup
st.markdown("---")
st.markdown("### 🔄 Alternative: Google Places API")
st.markdown("""
If Foursquare API continues to have issues, you can also use Google Places API:
1. Get a Google Places API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Places API
3. Use the endpoint: `https://maps.googleapis.com/maps/api/place/textsearch/json`
""")

if st.button("🔄 Try Alternative API Demo (requires Google API key)"):
    google_api_key = st.text_input("Enter Google Places API Key:", type="password")
    if google_api_key:
        try:
            google_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            google_params = {
                "query": f"{category} in {location}",
                "key": google_api_key
            }
            
            google_response = requests.get(google_url, params=google_params)
            if google_response.status_code == 200:
                google_data = google_response.json()
                if google_data.get("results"):
                    st.success(f"✅ Found {len(google_data['results'])} places with Google Places API!")
                    for place in google_data["results"][:5]:  # Show first 5 results
                        st.write(f"📍 **{place['name']}**")
                        st.write(f"Address: {place.get('formatted_address', 'N/A')}")
                        st.write(f"Rating: {place.get('rating', 'N/A')}/5")
                        st.markdown("---")
                else:
                    st.warning("No results found with Google Places API.")
            else:
                st.error(f"Google Places API error: {google_response.status_code}")
        except Exception as e:
            st.error(f"Error with Google Places API: {str(e)}")
