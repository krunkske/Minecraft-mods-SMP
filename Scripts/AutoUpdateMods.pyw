import os
import zipfile
import io
import shutil
import subprocess
import pkg_resources
import sys
import json
import requests
from win10toast_click import ToastNotifier 

appdata = os.getenv('APPDATA')
json_config = appdata + '/ModUpdater/config.json'


if os.path.exists(json_config):
    pass
else:
    sys.exit


#vars
Minecraft_folder = appdata + "/.minecraft"
mod_folder = Minecraft_folder + "/mods"
TEMP_folder = Minecraft_folder + "/mods/TEMP"
json_preferences = appdata + '/ModUpdater/preferences.json'
updated_mods = 0


toaster = ToastNotifier()

#update vars
def update_vars(Minecraft_folder):
    mod_folder = Minecraft_folder + "/mods"
    TEMP_folder = Minecraft_folder + "/mods/TEMP"
    fabric_fileplace = TEMP_folder + "/fabric_loader"
    return mod_folder, TEMP_folder, fabric_fileplace

#download and open config file as file_config
response = requests.get("https://raw.githubusercontent.com/krunkske/Minecraft-mods-SMP/main/config/config.json")
with open(json_config, 'wb') as f:
    f.write(response.content)

with open(json_config, 'r') as file_config:
     data_json_config = json.load(file_config)

#open preferences file as file_pref
with open(json_preferences, 'r') as file_pref:
     data_json_pref = json.load(file_pref)

#url vars

mods_url = data_json_config[0]['Mods_url']
config_url = data_json_config[0]['Config_url']

#get minecraft folder from pref
if data_json_pref[0]['minecraft_folder'] != "": 
    Minecraft_folder = data_json_pref[0]['minecraft_folder']
    mod_folder, TEMP_folder, fabric_fileplace = update_vars(Minecraft_folder)



def download_and_install_mods():
    global updated_mods

    print("Downloading and uzipping files")

    #gets the file(s) from the link, downloads them and unzips them
    response = requests.get(mods_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(TEMP_folder)

    print("Copying files")

    #gets all files in the directory (in a hacky way)
    temp_1_folder = os.listdir(TEMP_folder)
    all_files = os.listdir(TEMP_folder + '/' + temp_1_folder[0] + '/mods')

    #checks for all the files if they already exist
    for file in all_files:
        all_files_mod = os.listdir(mod_folder)

        if file in all_files_mod:
            print(file + " aready exist.")
        else:
            if file.endswith('.jar'):
                shutil.copy(TEMP_folder +  '/' + temp_1_folder[0] + '/mods/' + file , mod_folder)
                print(file + " has been installed.")
                updated_mods =+ 1
            else:
                print(file + ' is not a .jar file.')


    print("all mods have been installed.")

    toaster.show_toast(
    "Your mods have been updated!", # title
    str(updated_mods) + " mods have been installed", # message
    duration=5, # for how many seconds toast should be visible; None = leave notification in Notification Center
    threaded=True, # True = run other code in parallel; False = code execution will wait till notification disappears 
    )


    if os.path.isdir(TEMP_folder):
        print("Deleting TEMP folder")
        shutil.rmtree(TEMP_folder)

download_and_install_mods()