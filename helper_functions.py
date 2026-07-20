import math
def calculate_cost(cargo_type, estimated_distance, weight):
    if cargo_type == "1":
        base_rate = 0.40  
    elif cargo_type == "2":
        base_rate = 0.48  
    elif cargo_type == "3":
        base_rate = 0.44     
    elif cargo_type == "4":
        base_rate = 0.60  
    elif cargo_type == "5":
        base_rate = 0.56  
    elif cargo_type == "6":
        base_rate = 0.80  
    elif cargo_type == "7":
        base_rate = 0.52  
    elif cargo_type == "8":
        base_rate = 0.50 
    elif cargo_type == "9":
        base_rate = 0.72  
    elif cargo_type == "10": 
        base_rate = 0.40  
    else:
        base_rate = 0.40

    dist = float(estimated_distance)
    w = float(weight)

    calculated = 15.0 + (dist * w * base_rate)
    
    total = max(95000.0, calculated)
    total = round(total, 2)
    return total

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
   
    R = 6371.0 
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    straight_line_distance = R * c
    
    actual_driving_estimate = straight_line_distance * 1.25
    
    return round(actual_driving_estimate, 2)
