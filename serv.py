import socket, threading, sys, os, re, argparse
from datetime import datetime, timezone
class Server:
    
    global connections
    global s
    global num
    global host
    global port
    global blacklist
    global pw 

    def __init__(self,  host, port, num, pw,pwr):
        self.host=host
        self.port=port
        self.num=num
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.connections=[]
        self.blacklist=[]
        self.pw=pw
        self.pwr=pwr
    def send2_clients(self, msg):
        for j in range(0, len(self.connections)):
            self.connections[j][0].sendall(msg.encode("UTF-8"))


    def close_all(self):
        for i in range(0, len(self.connections)):
            self.connections[i][0].close()

    def new_con(self, i):
        latest_usr = self.connections[len(self.connections)-1][2]
        if len(self.connections) > i:
            #st = addr[0] + " " + str(addr[1]) + " is connected"
            spacing = " " * (20 - len(latest_usr))
            st = "\033[0;36m" + latest_usr.strip() + " has connected." +spacing+ self.get_utc() + "\033[0m\n"
            print(st)
            self.send2_clients(st)
            print("\033[0m")
            self.send2_clients("\033[0m")
            i+=1

    def kick(self, con, user):
        msg = "\033[0;31m" + user+ " has been kicked.\033[0m\n"
        print(msg)
        self.send2_clients(msg)
        con.close()
        self.remove_client(con)
        
    def blacklist_ip(self, addr):
        ip = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}$", addr)
        if ip:
            if ip not in self.blacklist:
                self.blacklist.append(addr)
            print(f"\033[0;31mblacklist: {self.blacklist}\033[0m")
        else:
            print("\033[0;31mInvalid IP address.\033[0m\n")
    
    def num_online(self):
        s = "\033[32m"+str(len(self.connections)) +" online. ("
        for i in range(0, len(self.connections)):
            if(i==len(self.connections)-1):
                s+=self.connections[i][2].strip() + " [" + self.connections[i][1][0]+"]"
            else:
                s+=self.connections[i][2].strip()+" [" + self.connections[i][1][0]+"], "
        
        return s+")\033[0m\n"
    
    def kill(self):
        self.send2_clients("\033[0;31mServer has been shut down by host.\033[0m\n")
        try:
            self.s.shutdown(socket.SHUT_WR)
        except OSError:
            pass
        self.s.close()
        
    def is_closed(self, con):
        if(str(con).find("closed")!=-1):
            return True
        return False
    

    def cmnd(self, inp):
        help = "------------------------------------------\n/kill  -  Shut down server \n/kick [user]  -  remove user from server\n/users  -  returns number and list of users\n/blacklist [ip] - blacklist ip from server\n------------------------------------------\n "
        inp=inp.strip()
        if(inp == "/kill"):
            self.kill()
            return True
        if(inp.find("/kick ")==0):
            usr = inp[6:len(inp)]
            for i in range(0, len(self.connections)):
                if(self.connections[i][2].strip()==usr):
                    self.kick(self.connections[i][0], usr)
                    return False
                else:
                    print(f'\033[0;31mCannot find user {usr}. See /users\033[0m\n')
        if(inp.find("/blacklist ")==0):
            addr=inp[11:len(inp)]
            self.blacklist_ip(addr)
            return False
        if(inp=="/help"):
            print(help)
            return False
        if(inp=="/users"):
            print(self.num_online())
            return False
        if(inp.find("/")==0):
            print("\033[0;31mCommand unrecognized. Try '/help'\033[0m")
            return False
        

    def server_input(self):
        while True:
            inp = input()
            if(self.cmnd(inp)): break
            if inp.find("/")==0: pass
            else: self.send2_clients("host >>> "+inp+"\n")
            
    def sanitize(self, data):
        d=data
        d = d.replace("\033[A", "")
        d = d.replace("\033[B", "")
        d = d.replace("\033[C", "")
        d = d.replace("\033[D", "")             
        return d
    
    def remove_client(self, con):
       for i in range(0, len(self.connections)):
            if(self.connections[i][0] == con):
                self.connections.pop(i)    
                break
    
    def client_input(self, con, user):
        while True:
            try:
                data = con.recv(2048).decode("UTF-8").strip()
                data = self.sanitize(data)
            except OSError:
                data=""
            if not data:
                if(self.is_closed(con)): break
                pass
            else:
                if str(data) == "quit":
                    discon="\033[0;31m" + user.strip() + " has disconnected \033[0m\n"
                    print(discon)
                    self.send2_clients(discon)
                    con.close()
                    self.remove_client(con)
                    break
                message =  user.strip() + " >>> " + data.strip() +"\n"
                print(message)
                for j in range(0, len(self.connections)):
                    if self.connections[j][0] != con:
                        self.connections[j][0].sendall(message.encode("UTF-8"))
        con.close()

    def user(self, con, addr):
        con.send("enter user:".encode('UTF-8'))
        data = con.recv(512).decode("UTF-8")
        data = self.sanitize(data)
        data = data[0:16]
        bs=re.findall(r"\w", data)
        if not bs: return addr.strip()
        return data
    
    def passwd(self,pw, con):
        con.send("password:".encode('UTF-8'))
        data=con.recv(512).decode('UTF-8')
        if(data.strip()==pw):
            return True
        con.send("\033[0;31mincorrect password.\033[0m\n".encode('UTF-8'))
        return False
    
    def run(self):
        self.s.listen(self.num)
        i=0
        serv_thread = threading.Thread(target=self.server_input)
        serv_thread.start()
        while True:
            try:
                con, addr = self.s.accept()
            except OSError:
                self.close_all()
                break
            if addr[0] in self.blacklist:
                con.close()
                continue
            if self.pwr:
                auth = self.passwd(self.pw, con)
                if not auth:
                    con.close()
                    continue
            user = self.user(con, addr[0])
            self.connections.append([con, addr, user])
            thread = threading.Thread(target=self.client_input, args=[con, user])
            thread.start()
            self.new_con(i)
            
    def get_utc(self):
        now = datetime.now(timezone.utc)
        return str(now.hour) + ":" + str(now.minute) +":"+ str(now.second) + " UTC" 

            

if __name__ == "__main__":
    #if(str(sys.platform).index("win")): os.system("@ECHO OFF REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1 > NUL 2>&1")
    parser = argparse.ArgumentParser(description = "scts, like irc but a lot worse")
    parser.add_argument("-passwd", "-pw", required = False)
    parser.add_argument("-port", "-p", default = 6667)
    pwr=False
    args=parser.parse_args()
    if args.passwd: pwr=True
    server=Server(socket.gethostbyname(socket.gethostname()), int(args.port), 16, args.passwd, pwr)
    print("server ip:"+socket.gethostbyname(socket.gethostname()))
    server.run()














