#!/bin/bash

import sys, os, subprocess

OUTPUT_PREFIX = "PixelPi> "

class SettingsFile():
    def __init__(self, settings_for, settings_file_name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        settings_file_location = os.path.abspath(os.path.join(current_directory, os.pardir)) + "/Application/" + settings_file_name + ".txt"

        if os.path.isfile(settings_file_location):
            ## If file exists, open the file, read all the lines and delete it
            f = open(settings_file_location, "r")
            self.lines = f.readlines()
            f.close()
            
            if len(self.lines) > 0:
                os.remove(settings_file_location)
                self.is_new_file = False
            else:
                self.is_new_file = True
            
        else:
            self.is_new_file = True
            
        
        self.settings_file = open(settings_file_location, "w")
        self.settings_file.write(settings_for.upper() + " SETTINGS")
            
            
    def printPrompt(self, prompt, key):
        if self.is_new_file:
            value_for_key = ""
            
        else:
            line = self.lines[0].replace('\n', '')
            
            
            while line:
                if key in line:
                    split_line = line.split(":")
                    temp_label = split_line[0].rstrip()
                    temp_value = split_line[1].rstrip('\n')
                    value_for_key = " - Currently: " + temp_value
                
                line = self.lines.readline().replace('\n', '')
        
            print(OUTPUT_PREFIX + prompt + value_for_key)
            response = input("").lower()

##            if response == "":
##        
            self.writeLine(key, response)
            

    def writeLine(self, key, new_value):
        self.settings_file.write("\n" + key + ": " + new_value)
        
    def closeFile(self):
        self.settings_file.close()


def setupMySQL():
    print(OUTPUT_PREFIX + "PixelPi Server requires access to MySQL to function properly")
    print(OUTPUT_PREFIX + "The database password is needed to grant access!")
    
    mysql_install_status = subprocess.Popen("dpkg -s  mysql-server", stdout=subprocess.PIPE, shell=True)
    (mysql_install_output, mysql_install_error) = mysql_install_status.communicate()
    
    if "Status: install ok installed" not in str(mysql_install_output):
        response = input(OUTPUT_PREFIX + "Would you like to install MySQL server (MariaDB)? (y/n)").lower()
            
        if response == "y" or response == "yes":
            
            subprocess.Popen("sudo apt-get install mysql-server", shell=True).wait()
            print("-------------------------ATTENTION!------------------------------")
            print(OUTPUT_PREFIX + "You will need to reset your password! Please enter the following commands into MariaDB to do so:")
            print(OUTPUT_PREFIX + "use mysql \nupdate user set plugin='' where User='root';")
            print(OUTPUT_PREFIX + "flush privileges \nexit")
            subprocess.Popen("sudo mysql -u root", shell=True).wait()
##            subprocess.Popen("ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';", shell=True).wait()

             
        else:
            print(OUTPUT_PREFIX + "Please install MySQL server!")
            print(OUTPUT_PREFIX + "try running: sudo apt-get install mysql-server")
            print(OUTPUT_PREFIX + "and follow the instructions on the screen!")
            sys.exit()

    
    
    settings.printPrompt("What is your MySQL password?", "MySQL Password")

def installRequirements(req_type):
    print(OUTPUT_PREFIX + "Installing requirements...")
    subprocess.call("sudo pip3 install -r " + os.path.dirname(os.path.abspath(__file__)) + "/" + req_type +"_requirements.txt", shell=True)


##    
##    req_location = os.path.dirname(os.path.abspath(__file__)) + "/" + req_type + "_requirements.txt"
##    requirements_file = open(req_location, "r")
##
##    line = requirements_file.readline().replace('\n', '')
##
##    while line:
##        subprocess.call("sudo pip3 install " + line, shell=True)
##        print("--->" + line + "<---")
##        line = requirements_file.readline().replace('\n', '')
##
##        
##        
##
##    requirements_file.close()


def setupRebootSchedule():
    while(True):
        print(OUTPUT_PREFIX + "Would you like instructions to set up a standard reboot time? (y/n)")
        response = input("").lower()
    
        if response == "y" or response == "yes":
            response = input(OUTPUT_PREFIX + "Please open a new terminal.")
            response = input(OUTPUT_PREFIX + "Run the command: crontab -e")
            response = input(OUTPUT_PREFIX + "Scroll to the bottom.")
            response = input(OUTPUT_PREFIX + "Enter the desired reboot time in cron time with the command: sudo reboot")
            return
        elif response == "n" or response == "no":
            return
        
        else:
            print(OUTPUT_PREFIX + "Response not understood, please enter: y or n")
        
    
def setupStartupPrefrences(program_to_setup):
    while(True):
        print(OUTPUT_PREFIX + "Would you like instructions to start the program automatically on startup? (y/n)")
        response = input("").lower()
        
    
        if response == "y" or response == "yes":
            response = input(OUTPUT_PREFIX + "Please enter the crontime when you want to reboot:")
            os.system('(crontab -l 2>/dev/null; echo "' + response + ' sudo reboot") | crontab -')
##            response = input(OUTPUT_PREFIX + "Please open a new terminal.")
##            response = input(OUTPUT_PREFIX + "Run the command: crontab -e")
##            response = input(OUTPUT_PREFIX + "Scroll to the bottom.")
##            print(OUTPUT_PREFIX + "Enter the desired reboot time in cron time with the command:")
##            response = input(OUTPUT_PREFIX + "sudo python3 " + os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + "/Application/" + program_to_setup + ".py")
            return
        elif response == "n" or response == "no":
            return
        
        else:
            print(OUTPUT_PREFIX + "Response not understood, please enter: y or n")
    
def closeProgram():
    settings.closeFile()
    print(OUTPUT_PREFIX + "Goodbye!")
    sys.exit()


print(OUTPUT_PREFIX + "Welcome to PixelPi setup!")




while(True):
    print(OUTPUT_PREFIX + "Please enter the program you wish to setup:")
    print(OUTPUT_PREFIX + "S for server, M for matrix, N for Neopixel, 5 for 5050 rgb, E to exit")
    response = input("").lower()

    if response == "s" or response == "server":
        program_to_setup = "Server"
        print(OUTPUT_PREFIX + "Installing server functionality...")

        settings = SettingsFile(program_to_setup.lower(), "server_settings")
        print(OUTPUT_PREFIX + "Settings for " + program_to_setup + " already exist.  Do you wish to continue with setup? (y/n)")
        
        setupMySQL()
        installRequirements("server")

    elif response == "n" or response == "neopixel":
        program_to_setup = "Client"
        
    elif response == "e" or response == "exit":
        closeProgram()
        
    else:
        print(OUTPUT_PREFIX + "Response not understood, please select from the list below:")
        continue
    
    setupRebootSchedule()
    setupStartupPrefrences(program_to_setup)
        
    while(True):
        print(OUTPUT_PREFIX + "Are you done setting up PixelPi? (y/n)")
        response = input("").lower()

        if response == "y" or response == "yes":
            closeProgram()
        elif response == "n" or response == "no":
            break;
        else:
            print(OUTPUT_PREFIX + "Response not understood, please enter: y or n")


