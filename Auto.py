import tkinter as tk
from tkinter import ttk
import requests
import os
import subprocess
import shutil
import mysql.connector
import configparser
import ctypes
import sys
import winreg
import zipfile
import time
import psutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(argv=None, debug=False):
    if argv is None:
        argv = sys.argv
    if hasattr(sys, '_MEIPASS'):
        # Support pyinstaller wrapped program.
        arguments = map(str, argv[1:])
    else:
        arguments = map(str, argv)
    cmd = ' '.join(arguments)
    shell_cmd = 'python "{}" {}'.format(argv[0], cmd)  # or sys.executable for the python interpreter path
    if debug:
        print("Command to run:", shell_cmd)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, shell_cmd, None, 1)

def get_xampp_install_path():
    try:
        # Open the registry key where XAMPP stores its installation path
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\XAMPP") as reg:
            # Attempt to read the value that stores the installation directory
            path, reg_type = winreg.QueryValueEx(reg, "Install_Dir")
            return path
    except FileNotFoundError:
        pass
    except OSError:
        pass
    
    # Return None if the path wasn't found or an error occurred
    return None


    
def download_file(url, dest_folder):
    # Make a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Get the total file size in bytes
        filename = url.split("/")[-1]
        file_path = os.path.join(dest_folder, filename)
        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = 0
        previous_progress = -1
        
        # Open the destination file in binary write mode
        print(f"{GREEN}---------------Downloading Xampp --version 5.6.32------------------{RESET}")
        with open(os.path.join(dest_folder, url.split("/")[-1]), 'wb') as f:
            # Iterate over the response content and write to file
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    # Write chunk to file
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    progress = min(100, int(bytes_downloaded / total_size * 100))
                    if previous_progress!=progress:
                        previous_progress = progress
                        print(f"......... {progress}% downloaded")
        print(f"{GREEN}------------------Downloaded successfully---------------------{RESET}")
        return file_path
    else:
        print(f"{RED}Failed to download file")
        return None
    
def install_xampp_silent(command):
    try:
        # Launch PowerShell as administrator and execute the command
        process = subprocess.run(["powershell", "-Command", f"Start-Process powershell -Verb runAs -Wait -ArgumentList '-NoProfile','-Command \"{command}\"'"], check=True)
        print(f"{GREEN}-----------xampp has installed successfully.------------{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}---------------Failed to execute PowerShell command-------------{RESET}")
       
        

def is_target_file(search_folder_path, target_folder_path):
    # Check if the default XAMPP directory exists
    if os.path.exists(search_folder_path):
        # Look for the XAMPP control panel executable
        control_panel_exe = os.path.join(search_folder_path, target_folder_path)
        if os.path.exists(control_panel_exe):
            return True
    return False

def extract_zip(zip_path, extract_to):

    # Ensure the target directory exists
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # Open the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"{GREEN}--------------Extracted all files in {zip_path} to {extract_to}----------------{RESET}")

def copy_folder(source_folder, destination_folder):
    try:
        shutil.copytree(source_folder, destination_folder)
        print(f"{GREEN}---------------Folder '{source_folder}' copied to '{destination_folder}' successfully--------------{RESET}")

    except Exception as e:
        print(f"{RED}Failed to copy folder:", e)

def copy_file(source_path, destination_folder):
    try:
        shutil.copy2(source_path, destination_folder)
        print(f"{GREEN}--------------------File copied successfully------------------{RESET}")
    except Exception as e:
        print(f"Error copying file: {e}")

def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"{GREEN}-------------------Folder '{folder_path}' deleted successfully----------------{RESET}")
    except OSError as e:
        print(f"Error: {folder_path} : {e.strerror}")

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"{GREEN}-------------------File '{file_path}' deleted successfully-----------------------{RESET}")
    except OSError as e:
        print(f"{RED}Error: {file_path} : {e.strerror}")


def get_config_info(config_file_path):
    try:
        with open(config_file_path, 'r') as file:
        # Iterate through each line in the file
            for line in file:
                # Process the line (in this case, just print it)
                if "(HOST," in line:
                    text = line.split(",")[1].strip()
                    lastindex = text.rfind("'")
                    host = text[1:lastindex]
                if "(USER," in line:
                    text = line.split(",")[1].strip()
                    lastindex = text.rfind("'")
                    user = text[1:lastindex]
                if "(PASS," in line:
                    text = line.split(",")[1].strip()
                    lastindex = text.rfind("'")
                    password = text[1:lastindex]
        print(f"{GREEN}-------------Get database Info from config -- {host}, {user}, {password} -----------------{RESET}")
        return host, user, password

    except:
        host = "localhost"
        user = "root"
        password = "admin"
        print(f"{RED}Not found config file{RESET}")
        return host, user, password
    
def modify_conf_file(file_path):
    # Read the entire file into a list of paragraphs
    with open(file_path, 'r') as file:
        content = file.read()
        paragraphs = content.split('\n\n')

    # Modify paragraphs containing the target text
    modified_paragraphs = []
    for paragraph in paragraphs:
        if 'DocumentRoot "C:/xampp/htdocs"' in paragraph:
            modified_paragraphs.append('DocumentRoot "C:/xampp/htdocs/wpv_mactos"')
        if '<Directory "C:/xampp/htdocs">' in paragraph:
            modified_paragraphs.append('<Directory "C:/xampp/htdocs/wpv_mactos">')
        else:
            modified_paragraphs.append(paragraph)

    modified_content = '\n\n'.join(modified_paragraphs)
    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(modified_content)

def create_database(host, user, database_name):
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=host,
            user=user,
        )

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute SQL query to create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

        print(f"{GREEN}-----------------Database '{database_name}' created successfully-------------{RESET}")

    except mysql.connector.Error as error:
        print("--------------Reconnecting to Mysql-----------")
        print(f"{RED}Failed to create database:", error)

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def import_sql_dump(dump_file_path, database_name, user, host='localhost'):
    try:
        # Command to import SQL dump file
        command = f'C:/xampp/mysql/bin/mysql.exe -u {user} -h {host} {database_name} < {dump_file_path}'
        
        # Execute the command
        subprocess.run(command, shell=True, check=True)
        print(f"{GREEN}---------------Successfully imported SQL dump into database '{database_name}'----------------{RESET}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

def set_xampp_services_autostart(ini_file_path):

    # Ensure the .ini file exists
    if not os.path.isfile(ini_file_path):
        print(f"{RED}-------------------The xampp-control.ini file was not found in {ini_file_path}-----------------{RESET}")
        return

    # Initialize the config parser
    config = configparser.ConfigParser()
    config.read(ini_file_path)

    # Check if the [Autostart] section exists, if not, create it
    if 'Autostart' not in config.sections():
        config.add_section('Autostart')

    # Set Apache and MySQL to autostart
    config.set('Autostart', 'Apache', '1')
    config.set('Autostart', 'MySql', '1')

    # Write the changes back to the file
    with open(ini_file_path, 'w') as configfile:
        config.write(configfile)

    print(f"{GREEN}-----------------XAMPP Control Panel configured to auto-start Apache and MySQL-----------------{RESET}")

def is_process_running_with_text(search_text):
    # Iterate over all running processes
    for proc in psutil.process_iter(attrs=['name', 'cmdline']):
        try:
            # Process name or command line arguments contain the search text
            if search_text.lower() in proc.info['name'].lower() or \
               any(search_text.lower() in arg.lower() for arg in (proc.info['cmdline'] or [])):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_program_running(program_name):
    try:
        process = subprocess.Popen(['tasklist'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if program_name.lower() in stdout.lower():
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return False



def create_startup_task(task_name, executable_path):
    try:
        # Create a scheduled task to run at system logon
        command = f'schtasks /create /tn "{task_name}" /tr "{executable_path}" /sc onstart /ru System'
        subprocess.run(command, check=True, shell=True)
        print(f"{GREEN}-------------Task '{task_name}' created successfully-------------------{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Failed to create task. Error: {e}")


def config_env():
    # URL of the XAMPP installer
    url = "https://deac-fra.dl.sourceforge.net/project/xampp/XAMPP%20Windows/5.6.32/xampp-win32-5.6.32-0-VC11-installer.exe"
    
    global RED, GREEN, RESET
    RED = '\033[31m'  # Red text
    GREEN = '\033[32m'  # Green text
    RESET = '\033[0m'  # Reset to default color
    
    if getattr(sys, 'frozen', False):
        # Executable is frozen (e.g., PyInstaller)
        script_path = sys.executable
    else:
        # Executable is not frozen
        script_path = os.path.abspath(sys.argv[0])

    # script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    # Destination folder where you want to save the file
    xampp_path = get_xampp_install_path()
    if xampp_path and is_target_file(xampp_path, "xampp_start.exe"):
        print(f"{GREEN}-------------------XAMPP is already installed at: {xampp_path}------------------{RESET}")
    else:
        print(f"{GREEN}----------------XAMPP is not installed on this PC--------------------------{RESET}")
        file_to_delete = f"c:/xampp"
        delete_folder(file_to_delete)
        time.sleep(1)
        delete_file(file_to_delete)
        time.sleep(1)

    
    # Download the file
        if is_target_file(script_dir, "xampp-win32-5.6.32-0-VC11-installer.exe"):
            downloaded_file_path = f"{script_dir}/xampp-win32-5.6.32-0-VC11-installer.exe"
            print("---------------xampp is already downloaded--------------------")
        else:
            downloaded_file_path = download_file(url, script_dir)
        print("xampp is installing...")
        powershell_command = f"{downloaded_file_path} --mode unattended"
        install_xampp_silent(powershell_command)
        time.sleep(5)
        
    #Copy config file
    control_ini_path = f"{script_dir}/config/xampp-control.ini"
    control_log_path = f"{script_dir}/config/xampp-control.log"
    config_destination_folder = f"C:/xampp"
    copy_file(control_ini_path, config_destination_folder)
    copy_file(control_log_path, config_destination_folder)

    apache_config_path = f"C:/xampp/apache/conf/httpd.conf"

    # Modify the .conf file
    # try:
    #     modify_conf_file(apache_config_path)
    # except:
    #     print("-------Modify localhost has been failed------------")
    # else:
    #     print(f"{GREEN}------wpv_mactos has been set as the localhost-------------{RESET}")

    set_xampp_services_autostart(f'C:\\xampp\\xampp-control.ini')
    
    if is_target_file(script_dir, "wpv_mactos"):
         # # Call the function to copy the folder
        source_folder = f"{script_dir}/wpv_mactos"
        destination_folder = "C:/xampp/htdocs/wpv_mactos"
        print(f"Copying the folder to {destination_folder}..................{RESET}")
        copy_folder(source_folder, destination_folder)
    else:
        if is_target_file(script_dir, "wpv_mactos.zip"):
            zip_path = f"{script_dir}/wpv_mactos.zip"
            extract_to = "C:/xampp/htdocs/wpv_mactos"
            print(f"Extracting the file to {extract_to}..................{RESET}")
            extract_zip(zip_path, extract_to)
        else:
            print(f"{RED}The App file doesn't exist. Please copy the file in the same directory as exe file")


    if is_target_file(script_dir, "db.sql"):
        print("The sql file exists.")
    else:
        print(f"{RED}The sql file doesn't exist. Please copy the file in the same directory as exe file")
    
    
    sql_file = f"{script_dir}/db.sql"

    database_name = "wpv_modelo"

    source_folder = f"{script_dir}/wpv_mactos"
    config_file_path = f"C:/xampp/htdocs/wpv_mactos/config/config.php"
    host, user, password = get_config_info(config_file_path)

    #run xampp.exe
    try:
        process = subprocess.Popen([f"C:/xampp/xampp-control.exe"])
        time.sleep(10)
    except:
        print(f"{RED}-------------Xampp_start.exe execution has failed. Tryagain---------------{RESET}")  
    else:
        print(f"{GREEN}-------------Xampp_start.exe has executed---------------{RESET}")

    create_database(host, user, database_name)
    time.sleep(3)
    # # Call the function to import SQL file

    import_sql_dump(sql_file, database_name, user, host)
    time.sleep(3)
    # #stop the xampp.exe
    # subprocess.run([f"C:/xampp/xampp_stop.exe"], check=True)
    # time.sleep(3)

    task_name = "xampp"
    executable_path = f"C:/xampp/xampp-control.exe"
    
    if is_process_running_with_text(task_name):
        print(f"{task_name} is currently running.")
    else:
        print(f"{task_name} is not running.")
        create_startup_task(task_name, executable_path)
        time.sleep(3)
        print(f"{GREEN}--------------Auto start xampp when startup.----------.{RESET}")
        
    print(f"{GREEN}Configuration successfully completed.{RESET}")
    # subprocess.run([executable_path], check=True)
    # sys.exit(0)

def draw_interface():
    # Create a Tkinter windo
    root = tk.Tk()
    root.title("Configuration")
    root.geometry("500x400")  # Set window size to 500x400

    # Create a label
    label = tk.Label(root, text="Introduction", font=("Arial", 16))
    label.pack(pady=15)

    # Create a text field
    introduction_box = tk.Text(root, width=48, height=16, font=("Arial", 12))  # Adjust height and width as needed
    introduction_text1 = f"Copy wpv_mactos folder or wpv_mactos.zip file in the same \n  directory as the exe file. The name has to be correct".rjust(10)
    introduction_text2 = f"Copy db.sql file in the same directory as the exe file.\n  The name has to be correct".rjust(10)
    introduction_text3 = f"Copy config folder in the same directory as the exe file.".rjust(10)
    introduction_text4 = f"You can start the app on browser:".rjust(10)
    introduction_text5 = f"'https://localhost/wpv_mactos'"
    introduction_box.insert(tk.END, f"\nCommand 1:\n {introduction_text1}\n\nCommand 2:\n {introduction_text2}\n\nCommand 3:\n {introduction_text3}\n\nCommand 4:\n {introduction_text4}\n {introduction_text5}")
    introduction_box.tag_config("redtext", foreground="red")
    introduction_box.tag_add("redtext", "2.0", "2.10", "6.0", "6.10", "10.0", "10.10", "13.0", "13.10")
    introduction_box.tag_config("greentext", foreground="green")
    introduction_box.tag_add("greentext", "3.6", "3.23", "3.27", "3.41", "7.6", "7.17", "11.6", "11.19", "15.1", "15.31")
    introduction_box.config(state="disabled")
    introduction_box.place(x=30, y=45)
    # Create a button
    button = tk.Button(root, text="Start Configuration", command=config_env)

    button.place(x=350, y=350)
    root.mainloop()

# draw_interface()

    
if __name__ == "__main__":
    if is_admin():
        print("Running as admin")
        draw_interface()
    else:
        print("Not running as admin, trying to elevate")
        run_as_admin(debug=True) 













