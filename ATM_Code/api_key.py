import requests

def get_nearby_atms(location, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Constructing an Overpass QL query to find ATMs within the specified radius
    overpass_query = f"""
        [out:json];
        (
            node["amenity"="atm"](around:{radius},{location});
            way["amenity"="atm"](around:{radius},{location});
            relation["amenity"="atm"](around:{radius},{location});
        );
        out;
    """

    params = {
        'data': overpass_query
    }

    response = requests.get(overpass_url, params=params)
    data = response.json()

    # Extracting relevant information from the response
    atms = []
    for element in data.get('elements', []):
        atm_info = {
            'name': element.get('tags', {}).get('name', 'N/A'),
            'lat': element.get('lat'),
            'lon': element.get('lon'),
        }
        atms.append(atm_info)

    return atms

def display_atm_info(atms):
    for index, atm in enumerate(atms, start=1):
        print(f"{index}. {atm['name']}")
        print(f"   Location: Latitude {atm['lat']}, Longitude {atm['lon']}")
        print("------------------------")
# include the above codes in the atm class using the self parameters or ask chatgpt
# under the elif c==3:
    
location = '32.70265,74.9242 '  

atms = get_nearby_atms(location)

if atms:
    print("Nearby ATMs (under 5000 meters):")
    display_atm_info(atms)
else:
    print("No ATMs found nearby.")
