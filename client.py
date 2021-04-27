import threading
import socket 

def receive(s):
    while(True):
        try:
            message = s.recv(1024)
            if(message == b''):
                s.close()
                break
            else:
                print(message.decode(), end="")
        except:
            break
def send(s):
    while(True):
        msg = input()
        if(msg == "LOGOUT"):
            s.close()
            break
        else:
            try:
                s.send(msg.encode())
            except:
                break
                    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
port = 12345                
s.connect(('127.0.0.1', port)) 

t1 = threading.Thread(target=send, args=(s,), daemon = True)
t2 = threading.Thread(target=receive, args=(s,), daemon = True)

t1.start()
t2.start()

t1.join()
t2.join()

s.close()
