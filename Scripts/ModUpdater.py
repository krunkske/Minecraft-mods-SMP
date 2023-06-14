import os
import zipfile
import io
import shutil
import subprocess
import pkg_resources
import sys
import tkinter as tk
from tkinter import filedialog
import json

#this has to be here before bc we need them immediatly
appdata = os.getenv('APPDATA')
json_config = appdata + '/ModUpdater/config.json'

def install_packages():
    if os.path.exists(json_config):
        pass
    else:
        required = {'requests', 'PySimpleGUI', 'win10toast_click'}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed

        print(missing)

        if missing:
            install_lib_yn = str(input("The requierd libraries are not installed. Install them? If you have done this befor you can just press enter because this message will display even if you have installed them. (Y/n): "))
            if install_lib_yn == "y" or install_lib_yn == "Y" or install_lib_yn == "yes" or install_lib_yn == "Yes":
                python = sys.executable
                subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
            else:
                pass

install_packages()

import requests
import PySimpleGUI as ui

#vars
current_version = 0.1
Minecraft_folder = appdata + "/.minecraft"
mod_folder = Minecraft_folder + "/mods"
TEMP_folder = Minecraft_folder + "/mods/TEMP"
fabric_fileplace = TEMP_folder + "/fabric_loader"
version_exist = 0
json_preferences = appdata + '/ModUpdater/preferences.json'


def update_vars(Minecraft_folder):
    mod_folder = Minecraft_folder + "/mods"
    TEMP_folder = Minecraft_folder + "/mods/TEMP"
    fabric_fileplace = TEMP_folder + "/fabric_loader"
    return mod_folder, TEMP_folder, fabric_fileplace

#init program

#make appdata directory if not exist
if not os.path.exists(appdata + '\\ModUpdater'):
    os.mkdir(appdata + '\\ModUpdater')

#make preferences.json file if not exists
if not os.path.exists(json_preferences):
    with open(json_preferences, "w") as f:
        f.write('[{"install_mods" : "False","install_all_mods" : "False","install_reqierd" : "False","install_recommended" : "False","install_cosmetic" : "False","current_version" : 0.1 , "minecraft_folder" : ""}]')

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
fabric_url = data_json_config[0]['Fabric_url']
MC_version = data_json_config[0]['version']
auto_update_startup_url = data_json_config[0]['auto_update_startup_url']

#get minecraft folder from pref
if data_json_pref[0]['minecraft_folder'] != "": 
    Minecraft_folder = data_json_pref[0]['minecraft_folder']
    mod_folder, TEMP_folder, fabric_fileplace = update_vars(Minecraft_folder)


#check if new version exists
latest_version = data_json_config[0]['latest_version']


if float(latest_version) > float(current_version):
    str(input("There is a new version available! Press enter to continue"))



#functions
def download_and_install_mods():
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
            else:
                print(file + ' is not a .jar file.')

    print("all mods have been installed.")

def install_fabric_loader():

    version_exist = 0

    MC_versions = os.listdir(appdata + '/.minecraft/versions')
    for foldername in MC_versions:
        if '1.20' in foldername and 'fabric-loader' in foldername and not '1.20.1' in foldername and version_exist < 1:
            print("1.20 has already been installed and does not need to be installed again")
            version_exist =+ 1
            break
        

    if version_exist == 0:
        #gets the file(s) from the link, downloads them and unzips them
        print("downloading fabric loader")

        if not os.path.exists(fabric_fileplace):
            os.makedirs(fabric_fileplace)


        response = requests.get(fabric_url)
        with open(fabric_fileplace + "/fabric-installer.jar", 'wb') as f:
            f.write(response.content)

        #subprocess with fabric install command. it will be installed in the default location, no other place is posseble atm due to it not working
        command = "java -jar " + fabric_fileplace + "/fabric-installer.jar client -mcversion " + MC_version
        output = subprocess.run(command)

        print(output)
        print("Fabric Loader has been installed!")

        
        if os.path.isdir(TEMP_folder):
            print("Deleting TEMP folder")
            shutil.rmtree(TEMP_folder)

def delete_all_mods():
    if os.path.isdir(mod_folder):
        print("Deleting MOD folder")
    shutil.rmtree(mod_folder)

#creating the GUI
ui.theme('LIghtGrey1')
root = tk.Tk()
root.withdraw()

#ui stuff

#all tabs
tab1 = [[ui.Text('Path to Minecraft folder:'), ui.Button(Minecraft_folder + '  Browse', key='browse1')],
        [ui.Text('Install all mods'), ui.Checkbox('',key='installAllMods')],
        [ui.Text('Delete all mods'),ui.Checkbox('',key='deleteAllMods')]]

tab2 = [[ui.Text('Install fabric loader'), ui.Checkbox('',key='installFabric')]]

tab3 = [[ui.Text('Auto check for new mods on startup?'), ui.Checkbox('',key='Autostartup')],
        [ui.Text('Delete startup script?'), ui.Checkbox('',key='delstartup')]]

ui_layout = [[ui.TabGroup([[ui.Tab('Mods', tab1), ui.Tab('Fabric Loader', tab2),ui.Tab('Settings', tab3) ]], key='-TABGROUP-')],
            [ui.Button('Go'), ui.Button('Close')]]
window = ui.Window('ModUpdater', ui_layout)

while True:
    event, values = window.read()

    #if user pressed close, close the program
    if event == ui.WIN_CLOSED or event == 'Close': # if user closes window or clicks cancel
        sys.exit()
    if event == 'browse1':
        Minecraft_folder = filedialog.askdirectory()
        if  Minecraft_folder:
            window['browse1'].update(Minecraft_folder)
            mod_folder, TEMP_folder, fabric_fileplace = update_vars(Minecraft_folder)
    if event == 'Go':
        if values['installFabric'] == True:
            install_fabric_loader()
        if values['deleteAllMods'] == True:
            delmod = str(input("do you want te delete the mods folder? THIS WILL DELETE ALL CURRENTLY INSTALLED MODS! (Y/n) "))
            if delmod == "y" or delmod == "Y" or delmod == "yes" or delmod == "Yes":
                delete_all_mods()
        if values['installAllMods'] == True:
            download_and_install_mods()
        
        if values['Autostartup'] == True:
            response = requests.get(auto_update_startup_url)
            with open(appdata + '/Microsoft/Windows/Start Menu/Programs/Startup/AutoUpdateMods.pyw', 'wb') as f:
                f.write(response.content)
        
        if values['delstartup'] == True:
            if os.path.exists(appdata + '/Microsoft/Windows/Start Menu/Programs/Startup/AutoUpdateMods.pyw'):
                os.remove(appdata + '/Microsoft/Windows/Start Menu/Programs/Startup/AutoUpdateMods.pyw')

        data_json_pref[0]['minecraft_folder'] = Minecraft_folder
        with open(json_preferences, 'w') as f:
            json.dump(data_json_pref, f, indent=4)
        break
window.close()

#the code hell


if os.path.isdir(TEMP_folder):
    print("Deleting TEMP folder")
    shutil.rmtree(TEMP_folder)


