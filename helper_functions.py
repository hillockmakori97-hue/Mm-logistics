import math
def calculate_cost(cargo_type,estimated_distance,weight):
    # Check the cargo type and assign the baseline rate
    if cargo_type == "General Cargo (FMCG & Retail Goods)":
        base_rate = 14.00
    elif cargo_type == "Heavy Industrial & Breakbulk (Metals & Machinery)":
        base_rate = 16.00
    elif cargo_type == "Dry Bulk & Agricultural Commodities":
        base_rate = 13.00
    elif cargo_type == "Cold Chain & Temperature-Controlled (Perishables)":
        base_rate = 22.00
    elif cargo_type == "Pharmaceutical & Medical Supplies":
        base_rate = 20.00
    elif cargo_type == "Hazardous Materials (HazMat)":
        base_rate = 30.00
    elif cargo_type == "Liquid Bulk":
        base_rate = 19.00
    elif cargo_type == "Automotive & Vehicles":
        base_rate = 18.00
    elif cargo_type == "High-Value & Secure Cargo":
        base_rate = 35.00
    else:
        base_rate = 12.00
    cost=(base_rate*estimated_distance*weight)
    return cost



def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the straight-line distance between two points on the Earth 
    using their decimal latitude and longitude coordinates.
    """
    # Earth's radius in kilometers
    R = 6371.0 
    
    # Convert degrees to radians (Python math requires radians)
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate the differences between the points
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # The core Haversine mathematical equations
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Calculate the absolute straight line distance
    straight_line_distance = R * c
    
    # Road routing factor: add 25% extra padding to turn a 
    # straight flight path into a realistic twisting highway distance
    actual_driving_estimate = straight_line_distance * 1.25
    
    return round(actual_driving_estimate, 2)