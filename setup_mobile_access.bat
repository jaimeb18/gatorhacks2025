@echo off
echo Setting up firewall rule for Python Flask server...
echo This will allow incoming connections on port 5000

netsh advfirewall firewall add rule name="Python Flask Server" dir=in action=allow protocol=TCP localport=5000

echo.
echo Firewall rule added successfully!
echo You can now access the server from your phone at: http://10.136.89.219:5000
echo.
echo Press any key to continue...
pause > nul
