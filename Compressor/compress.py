import os

# Folder with your txt files
folder = "cookies"
output_file = "cookies.txt"

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            with open(filepath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Add newline between files (optional)

print(f"All .txt files from '{folder}' combined into '{output_file}'")
