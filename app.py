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
FOURSQUARE_API_KEY = "fsq3HkSKnobCiEEZdDKEO9WA8xUMxxlzCpOBbt/dczhhp1s="

# Category mapping for better search results
CATEGORY_MAPPING = {
    "Restaurant": "restaurant",
    "Cafe": "cafe", 
    "Hotel": "hotel",
    "Park": "park",
    "Shopping Mall": "shopping"
}

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        try:
            # Current Foursquare Places API v3 endpoint
            url = "https://api.foursquare.com/v3/places/search"
            
            # Correct headers format as per Foursquare documentation
            headers = {
                "Accept": "application/json",
                "Authorization": FOURSQUARE_API_KEY  # API key directly, no Bearer prefix
            }
            
            # Parameters for the search
            params = {
                "query": CATEGORY_MAPPING.get(category, category.lower()),
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
                st.info("Make sure you're using a valid FSQ Places API key from https://developer.foursquare.com/")
            elif response.status_code == 403:
                st.error("❌ Access forbidden. Check if your API key has Places API access.")
            elif response.status_code == 410:
                st.error("❌ API endpoint deprecated or unavailable.")
                st.warning("🚨 **Important Notice**: Foursquare is migrating to new API endpoints.")
                st.info("""
                **Migration Info**: 
                - Foursquare v3 APIs are being migrated to new FSQ OS Places endpoints
                - Your API key might need to be updated for the new endpoints
                - Check your Foursquare developer dashboard for migration details
                - Visit: https://docs.foursquare.com/developer/reference/upcoming-changes
                """)
                
                # Show exact request details for debugging
                st.error("**Debug Info:**")
                st.code(f"URL: {response.url}")
                st.code(f"Headers: {dict(response.request.headers)}")
                st.code(f"Status: {response.status_code}")
                st.code(f"Response: {response.text}")
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
4. Use the API test feature if you encounter issues

**⚠️ Important**: Foursquare is currently migrating their API endpoints. If you get a 410 error:
- Your API key may need to be updated
- Check your Foursquare Developer Console for migration notices
- Visit the [Foursquare migration guide](https://docs.foursquare.com/developer/reference/upcoming-changes)
""")

st.markdown("**📚 Resources:**")
st.markdown("- [Foursquare Developer Console](https://developer.foursquare.com/)")
st.markdown("- [API Documentation](https://docs.foursquare.com/developer/reference/place-search)")  
st.markdown("- [Migration Guide](https://docs.foursquare.com/developer/reference/upcoming-changes)")

# Test API connection with detailed debugging
if st.checkbox("🔧 Test API Connection"):
    st.write("Testing current Foursquare API connection...")
    
    # Test with minimal parameters first
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Accept": "application/json",
            "Authorization": FOURSQUARE_API_KEY
        }
        
        # Simple test parameters
        params = {
            "query": "restaurant",
            "near": "New York, NY",  # Use a well-known location for testing
            "limit": 1
        }
        
        st.write("**Request Details:**")
        st.code(f"URL: {url}")
        st.code(f"Headers: {headers}")
        st.code(f"Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        st.write(f"**Response Status:** {response.status_code}")
        st.write(f"**Response Headers:** {dict(response.headers)}")
        
        if response.status_code == 200:
            st.success("✅ API connection successful!")
            data = response.json()
            st.write(f"**Results found:** {len(data.get('results', []))}")
            if data.get('results'):
                st.write("**Sample result:**")
                st.json(data['results'][0])
            else:
                st.warning("API connected but no results returned")
                
        elif response.status_code == 401:
            st.error("❌ **Authentication Error (401)**")
            st.write("Your API key is invalid or expired.")
            st.info("Solutions:\n1. Check your API key in Foursquare Developer Console\n2. Verify the key hasn't expired\n3. Ensure Places API is enabled for your key")
            
        elif response.status_code == 410:
            st.error("❌ **Endpoint Gone (410)**") 
            st.write("This specific endpoint is no longer available.")
            st.warning("🚨 **Critical**: Foursquare v3 APIs are being deprecated!")
            st.info("""
            **What to do:**
            1. Check Foursquare Developer Console for API updates
            2. Look for migration notices in your account
            3. Your API key may need to be regenerated for new endpoints
            4. Visit: https://docs.foursquare.com/developer/reference/upcoming-changes
            """)
            
        elif response.status_code == 429:
            st.error("❌ Rate limit exceeded")
            
        else:
            st.error(f"❌ Unexpected error: {response.status_code}")
            st.write("**Full Response:**")
            st.code(response.text)
            
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

# API Key Validator
st.markdown("---")
st.markdown("### 🔑 API Key Information")

# Show API key format info
if st.checkbox("Show API Key Info"):
    st.info("""
    **Foursquare API Key Format:**
    - Should start with 'fsq3' for v3 APIs
    - Length: Usually 47-50 characters
    - Example: fsq3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
    **Your API Key Analysis:**
    """)
    
    api_key = FOURSQUARE_API_KEY.strip()
    st.write(f"- Length: {len(api_key)} characters")
    st.write(f"- Starts with 'fsq3': {'✅' if api_key.startswith('fsq3') else '❌'}")
    st.write(f"- Format appears valid: {'✅' if len(api_key) > 40 and api_key.startswith('fsq3') else '❌'}")
    
    if not api_key.startswith('fsq3'):
        st.error("⚠️ Your API key doesn't start with 'fsq3' - this might be an old format or invalid key")
    
    st.markdown("**Get a new API key:**")
    st.markdown("1. Go to [Foursquare Developer Console](https://developer.foursquare.com/)")
    st.markdown("2. Create or select your app")
    st.markdown("3. Generate a new API key")
    st.markdown("4. Make sure Places API is enabled")

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
