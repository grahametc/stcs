import socket, threading, sys, os

class Server:
    
    global connections
    global s
    global num
    global host
    global port

    def __init__(self,  host, port, num):
        self.host=host
        self.port=port
        self.num=num
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.connections=[]
    
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
            st = "\033[0;36m" + latest_usr.strip() + " has connected. \033[0m\n"
            print(st)
            self.send2_clients(st)
            print("\033[0m")
            self.send2_clients("\033[0m")
            i+=1

    def kick(self, user):
        for con in self.connections:
            if(user == con[2]):
                print(user+" has been kicked")
                con.close()
                break
    def num_online(self):
        s = "\033[32m"+str(len(self.connections)) +" online. ("
        for i in range(0, len(self.connections)):
            if(i==len(self.connections)-1):
                s+=self.connections[i][2].strip()
            else:
                s+=self.connections[i][2].strip()+", "
        
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
        help = "------------------------------------------\n/kill  -  Shut down server \n/kick [user]  -  remove user from server\n/users  -  returns number and list of users\n------------------------------------------\n"
        inp=inp.strip()
        if(inp == "/kill"):
            self.kill()
            return True
        if(inp.find("/kick ")==0):
            usr = inp[5:len(inp)]
            for con in self.connections:
                if(con[2].strip()==usr):
                    self.kick(usr)
                    return False
        if(inp=="/help"):
            print(help)
            return False
        if(inp=="/users"):
            print(self.num_online())
            return False
        if(inp.find("/")!=-1):
            return False
            

    def server_input(self):
        while True:
            inp = input()
            if(self.cmnd(inp)): break
                
        
       

    
    def client_input(self, con, user):
        while True:
            try:
                data = con.recv(2048).decode("UTF-8").strip()
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
                    for i in range(0, len(self.connections)):
                        if(self.connections[i][0] == con):
                            self.connections.pop(i)
                    break
                message =  user + str(" " * (len(user)-1)) + "\033[1A >>> "  + data.strip() +"\n"
                print(message)
                for j in range(0, len(self.connections)):
                    if self.connections[j][0] != con:
                        self.connections[j][0].sendall(message.encode("UTF-8"))
        con.close()

    def user(self, con):
        con.send("enter user:".encode('UTF-8'))
        data = con.recv(512).decode("UTF-8")
        if(data.find(" ")>-1):
            data = data[0:data.index(" ")]
        if(data == ""): return self.connections[len(self.connections)-1]
        return data

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
            user = self.user(con)
            self.connections.append([con, addr, user])
            thread = threading.Thread(target=self.client_input, args=[con, user])
            thread.start()
            self.new_con(i)
            


            

if __name__ == "__main__":
    #if(str(sys.platform).index("win")): os.system("@ECHO OFF REG ADD HKCU\CONSOLE /f /v VirtualTerminalLevel /t REG_DWORD /d 1 > NUL 2>&1")
    server=Server(socket.gethostbyname(socket.gethostname()), 6667, 16)
    print("server ip:"+socket.gethostbyname(socket.gethostname()))
    server.run()














