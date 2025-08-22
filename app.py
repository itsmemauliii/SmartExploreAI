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

# Your Foursquare API Key (Make sure this is a valid current FSQ Places API key)
FOURSQUARE_API_KEY = "fsq3HkSKnobCiEEZdDKEO9WA8xUMxxlzCpOBbt/dczhhp1s="

# Category mapping for better search results
CATEGORY_MAPPING = {
    "Restaurant": "restaurant",
    "Cafe": "cafe", 
    "Hotel": "hotel",
    "Park": "park",
    "Shopping Mall": "shopping"
}

# Multiple endpoint attempts - trying different API versions
FOURSQUARE_ENDPOINTS = [
    "https://api.foursquare.com/v3/places/search",  # Current v3 endpoint
    "https://api.foursquare.com/places/search",     # Possible new endpoint without version
    "https://api.foursquare.com/v4/places/search",  # Possible v4 endpoint
]

# Trigger search
if st.button("🔍 Search"):
    with st.spinner("Fetching places..."):
        success = False
        
        for i, endpoint_url in enumerate(FOURSQUARE_ENDPOINTS):
            if success:
                break
                
            try:
                st.info(f"Trying endpoint {i+1}/{len(FOURSQUARE_ENDPOINTS)}: {endpoint_url}")
                
                # Correct headers format as per Foursquare documentation
                headers = {
                    "Accept": "application/json",
                    "Authorization": FOURSQUARE_API_KEY
                }
                
                # Parameters for the search
                params = {
                    "query": CATEGORY_MAPPING.get(category, category.lower()),
                    "near": location,
                    "limit": 10
                }
                
                response = requests.get(endpoint_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    if results:
                        st.success(f"✅ Found {len(results)} places using endpoint: {endpoint_url}")
                        success = True
                        
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
                        st.warning(f"No results found with endpoint: {endpoint_url}")
                        
                elif response.status_code == 410:
                    st.warning(f"❌ Endpoint deprecated: {endpoint_url}")
                    continue  # Try next endpoint
                    
                elif response.status_code == 401:
                    st.error("❌ Invalid API key. This affects all endpoints.")
                    break  # Don't try other endpoints if auth fails
                    
                elif response.status_code == 429:
                    st.error("❌ Rate limit exceeded.")
                    break
                    
                else:
                    st.warning(f"❌ Endpoint failed: {endpoint_url} (Status: {response.status_code})")
                    continue  # Try next endpoint
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Network error with {endpoint_url}: {str(e)}")
                continue  # Try next endpoint
            except Exception as e:
                st.error(f"❌ Error with {endpoint_url}: {str(e)}")
                continue  # Try next endpoint
        
        if not success:
            st.error("❌ **All Foursquare endpoints failed!**")
            st.warning("""
            🚨 **Critical Issue**: All known Foursquare API endpoints are returning errors.
            
            **Immediate Actions Required:**
            
            1. **Check Your Developer Console**: 
               - Visit https://developer.foursquare.com/
               - Look for migration notices or API updates
               - Verify your API key status
            
            2. **API Key Issues**:
               - Your API key may be expired or invalid
               - You may need to generate a new key for the updated API
               - Ensure Places API access is enabled
            
            3. **API Migration**:
               - Foursquare has announced major API changes
               - You may need to migrate to new endpoints
               - Check the migration guide: https://docs.foursquare.com/developer/reference/upcoming-changes
               
            4. **Alternative**: 
               - Consider creating a new Foursquare developer account
               - Generate fresh API keys for the new system
            """)
                
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

# Test API connection with multiple endpoints
if st.checkbox("🔧 Test All API Endpoints"):
    st.write("Testing all known Foursquare API endpoints...")
    
    for i, endpoint_url in enumerate(FOURSQUARE_ENDPOINTS):
        st.write(f"**Testing Endpoint {i+1}: {endpoint_url}**")
        
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": FOURSQUARE_API_KEY
            }
            
            params = {
                "query": "restaurant",
                "near": "New York, NY",
                "limit": 1
            }
            
            response = requests.get(endpoint_url, headers=headers, params=params, timeout=10)
            
            st.write(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                st.success(f"✅ Working endpoint: {endpoint_url}")
                data = response.json()
                st.write(f"Results found: {len(data.get('results', []))}")
                if data.get('results'):
                    st.json(data['results'][0])
                    
            elif response.status_code == 410:
                st.error(f"❌ Deprecated: {endpoint_url}")
                
            elif response.status_code == 401:
                st.error(f"❌ Auth failed: {endpoint_url}")
                st.write("Check your API key")
                
            elif response.status_code == 404:
                st.warning(f"⚠️ Not found: {endpoint_url}")
                
            else:
                st.warning(f"⚠️ Status {response.status_code}: {endpoint_url}")
                st.code(response.text[:200] + "..." if len(response.text) > 200 else response.text)
                
        except requests.exceptions.Timeout:
            st.error(f"❌ Timeout: {endpoint_url}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
        st.markdown("---")

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
