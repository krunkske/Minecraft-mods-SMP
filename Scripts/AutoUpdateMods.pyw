import os
import shutil
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
current_version = 0.3
Minecraft_folder = appdata + "/.minecraft"
mod_folder = Minecraft_folder + "/mods"
TEMP_folder = Minecraft_folder + "/mods/TEMP"
json_preferences = appdata + '/ModUpdater/preferences.json'
all_mods_json = appdata + '/ModUpdater/all_mods.json'
updated_mods = 0


toaster = ToastNotifier()


#update vars
def update_vars(Minecraft_folder):
    mod_folder = Minecraft_folder + "/mods"
    TEMP_folder = Minecraft_folder + "/mods/TEMP"
    fabric_fileplace = TEMP_folder + "/fabric_loader"
    all_mods_json = appdata + '/ModUpdater/all_mods.json'
    return mod_folder, TEMP_folder, fabric_fileplace, all_mods_json



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
all_mods_url = data_json_config[0]['all_mods_url']



#get minecraft folder from pref
if data_json_pref[0]['minecraft_folder'] != "": 
    Minecraft_folder = data_json_pref[0]['minecraft_folder']
    mod_folder, TEMP_folder, fabric_fileplace, all_mods_json = update_vars(Minecraft_folder)

#make temp dir bc something doesnt work
if not os.path.exists(TEMP_folder):
    os.mkdir(TEMP_folder)

#download and open All_mods.json
response = requests.get(all_mods_url)
with open(all_mods_json, 'wb') as f:
    f.write(response.content)

with open(all_mods_json, 'r') as file_all_mods:
    data_json_all_mods = json.load(file_all_mods)



def download_and_install_mods():
    global updated_mods

    print("Downloading and uzipping files")

    all_installed_mods = os.listdir(mod_folder)


    for file in data_json_all_mods:
        if file['name'] in all_installed_mods:
            pass
            #print(file['name'] + ' is installed')
        else:
            print(file["name"])
            print(file['download_url'])
            response = requests.get(file['download_url'])
            with open(TEMP_folder + '/' + file['name'], 'wb') as f:
                f.write(response.content)
        
        all_files_in_temp = os.listdir(TEMP_folder)

        updated_mods = set()
        for mod in all_files_in_temp:
            if mod.endswith('.jar'):
                shutil.copy(TEMP_folder + '/' + mod, mod_folder)
                updated_mods.add(mod)

        

    #show popup
    toaster.show_toast(
    "Your mods have been updated!", # title
    str(len(updated_mods)) + " mods have been installed", # message
    duration=5, # for how many seconds toast should be visible; None = leave notification in Notification Center
    threaded=True, # True = run other code in parallel; False = code execution will wait till notification disappears 
    )


    if os.path.isdir(TEMP_folder):
        print("Deleting TEMP folder")
        shutil.rmtree(TEMP_folder)

def Newversion():
    #show popup
    toaster.show_toast(
    "There is a new version available!", # title
    "Version " + str(latest_version) + " is availabe", # message
    duration=5, # for how many seconds toast should be visible; None = leave notification in Notification Center
    threaded=False, # True = run other code in parallel; False = code execution will wait till notification disappears 
    )


#check if new version exists
latest_version = data_json_config[0]['latest_version']


if float(latest_version) > float(current_version):
    Newversion()


download_and_install_mods()

if os.path.isdir(TEMP_folder):
    print("Deleting TEMP folder")
    shutil.rmtree(TEMP_folder)
