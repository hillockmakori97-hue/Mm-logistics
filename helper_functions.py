import math
def calculate_cost(cargo_type, estimated_distance, weight):
    if cargo_type == "General Cargo (FMCG & Retail Goods)":
        base_rate = 1.4
    elif cargo_type == "Heavy Industrial & Breakbulk (Metals & Machinery)":
        base_rate = 1.6
    elif cargo_type == "Dry Bulk & Agricultural Commodities":
        base_rate = 1.3
    elif cargo_type == "Cold Chain & Temperature-Controlled (Perishables)":
        base_rate = 2.2
    elif cargo_type == "Pharmaceutical & Medical Supplies":
        base_rate = 2.0
    elif cargo_type == "Hazardous Materials (HazMat)":
        base_rate = 3.0
    elif cargo_type == "Liquid Bulk":
        base_rate = 1.9
    elif cargo_type == "Automotive & Vehicles":
        base_rate = 1.8
    elif cargo_type == "High-Value & Secure Cargo":
        base_rate = 3.5
    elif cargo_type == "Other": 
        base_rate = 1.2
    else:
        base_rate = 1.2      
    cost = base_rate * estimated_distance * weight
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