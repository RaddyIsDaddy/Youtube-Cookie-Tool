import json

# Input filename (your JSON)
input_file = "cookies.json"
# Output filename
output_file = "cookies.txt"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Get the cookies dict
cookies = data.get("Request Cookies", {})

# Join them into Cookie header format
cookie_string = ";".join([f"{k}={v}" for k, v in cookies.items()])

# Save to file
with open(output_file, "w", encoding="utf-8") as f:
    f.write(cookie_string)

print("Cookies saved to", output_file)
