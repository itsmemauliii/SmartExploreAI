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

# Your Foursquare API Key
FOURSQUARE_API_KEY = "fsq3HkSKnobCiEEZdDKEO9WA8xUMxxlzCpOBbt/dczhhp1s="  # Your actual API key

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        try:
            url = "https://api.foursquare.com/v3/places/search"
            headers = {"Authorization": FOURSQUARE_API_KEY}
            params = {
                "query": category.lower(),
                "near": location,
                "limit": 10
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
            elif response.status_code == 429:
                st.error("❌ Rate limit exceeded. Please wait and try again later.")
            else:
                st.error(f"❌ Error fetching data. Status code: {response.status_code}")
                st.error(f"Response: {response.text}")
                
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
        headers = {"Authorization": FOURSQUARE_API_KEY}
        params = {
            "query": "restaurant",
            "near": "Ahmedabad, India",
            "limit": 1
        }
        
        response = requests.get(url, headers=headers, params=params)
        st.write(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            st.success("✅ API connection successful!")
            data = response.json()
            st.json(data)
        else:
            st.error(f"❌ API connection failed: {response.text}")
            
    except Exception as e:
        st.error(f"❌ Connection test failed: {str(e)}")
