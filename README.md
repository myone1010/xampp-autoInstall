#import module
pip install mysql
pip install psutil

#build
pip install pyinstaller
pyinstaller --onefile --icon=E:\task\test-03\php-autointall\phpAutoinstall\logo-sif.ico auto.py

#function
1.  check if the xampp is installed in c:\ and skip installation if the xampp is already installed
2. check if xampp-win32-5.6.32-0-VC11-installer.exe exists in the same directory and if not download it.install xampp and install it.
3. copy config file fpr apache and mysql auto start
4. copy or extract DB file to xampp/htdocs
5. Read DB config file 
6. run xampp and create DB
7. import sql to DB
8. create task for xampp autostart when PC starts up
