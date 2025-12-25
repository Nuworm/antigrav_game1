import json
import hex_lib

def save_map(filename, hex_map):
    """
    Saves a dict {Hex: type_int} to a JSON file.
    """
    data = []
    for h, t in hex_map.items():
        data.append({"q": h.q, "r": h.r, "type": t})
    
    with open(filename, "w") as f:
        json.dump(data, f)
    print(f"Map saved to {filename}")

def load_map(filename):
    """
    Loads a JSON file and returns a dict {Hex: type_int}.
    """
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        
        hex_map = {}
        for item in data:
            h = hex_lib.Hex(item["q"], item["r"])
            hex_map[h] = item["type"]
        
        print(f"Map loaded from {filename}")
        return hex_map
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
