### stcs
sh*tty terminal chat server

## For windows users
run ``` REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1``` in your terminal to enable ansi 


## Use
For server:
``` python3 serv.py```
Connect to server:
``` telnet {ip address} {port}``` OR ```nc {ip address} {port}``` 
## Port Forwarding
Use intermediary service like ngrok
