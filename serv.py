import socket, threading

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
        
    def new_con(self, i):
        latest = self.connections[len(self.connections)-1][1]
        if len(self.connections) > i:
            #st = addr[0] + " " + str(addr[1]) + " is connected"
            st = latest[0] + " " + str(latest[1]) + " is connected. \n"
            print(st)
            self.send2_clients(st)
            i+=1

    def client_input(self, con, addr):
        while True:
            data = con.recv(2048)
            if not data:
                pass
            else:
                if data.decode('UTF-8').lower() == "quit":
                    con.close()
                    break
                message =  addr[0] + " >>> "  + data.decode("UTF-8").strip() +"\n"
                print(message)
                for j in range(0, len(self.connections)):
                    if self.connections[j][0] != con:
                        self.connections[j][0].sendall(message.encode("UTF-8"))
        con.close()        

    def run(self):
        self.s.listen(self.num)
        i=0
        while True:
            con, addr = self.s.accept()
            self.connections.append((con, addr))
            thread = threading.Thread(target=self.client_input, args=(con, addr))
            thread.start()
            self.new_con(i)

            

if __name__ == "__main__":
    s=Server("127.0.0.1", 6667, 16)
    s.run()


