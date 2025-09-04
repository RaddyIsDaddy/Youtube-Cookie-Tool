from cookiecreator.script import main
import os
import json

def menu():
    print("Youtube Cookie Bot")
    print("1: Create cookie from email:password accounts        2: Compress multiple cookie files into 1")
    print("3: Convert copied JSON cookie into TXT")
    option = input("\nSelect an option: ")
    if option == 1:
        print("Be sure you put your accounts in accounts.txt in the cookiecreator folder.")
        main()
    elif option == 2:
        print("Be sure you put your cookies in the cookies folder.")
        compress()
    elif option == 2:
        print("Be sure you copied your json formatted cookie into cookie.json")
        convert()

# COMPRESSOR

def compress():
    folder = "cookies"
    output_file = "cookies.txt"
    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(folder, filename)
                with open(filepath, "r", encoding="utf-8") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")

    print(f"All .txt files from '{folder}' combined into '{output_file}'")
    menu()

#------------------------------------------------------

# CONVERTER

def convert():
    input_file = "cookies.json"
    output_file = "cookies.txt"
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    cookies = data.get("Request Cookies", {})
    cookie_string = ";".join([f"{k}={v}" for k, v in cookies.items()])
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cookie_string)
    print("Cookies saved to", output_file)
    menu()


#------------------------------------------------------


menu()