import threading
import socket 
import pymongo
import dns
mongoclient = pymongo.MongoClient("mongodb+srv://mydb:amit955raja@cluster0.gwlqy.mongodb.net/mydb2?retryWrites=true&w=majority")
db = mongoclient["mydb2"]
col = db["users"]
colG = db["groups"]

def newConnection(c):
    c.send("Enter HELP to see commands\n".encode())
    username = ""
    connectedTo = ""
    while(True):
        try:
            message = (c.recv(1024)).decode().split()
        except:
            c.close()
            break
        if(message[0] == "HELP"):
            c.send("LOGIN username password   - to login into existing account\n".encode())
            c.send("CREATE username password  - to create a new account\n".encode())
            c.send("CONNECTUSER username      - to connect to an existing user\n".encode())
            c.send("CONNECTGROUP groupname    - to connect to an existing group\n".encode())
            c.send("CREATEGROUP groupname     - to create a new group\n".encode())
            c.send("JOINGROUP groupname       - to join a group\n".encode())
            c.send("ADDFRIEND username        - to add a friend\n".encode())
            c.send("FRIENDS                   - to get list of friends\n".encode())
            c.send("GROUPS                    - to get list of groups\n".encode())
            c.send("HISTORY                   - to see chat history\n".encode())
            c.send("LOGOUT                    - to logout\n".encode())
        elif(message[0] == "LOGIN"):
            isLoggedIn = False
            if(len(message) != 3):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({"$and" : [{ "username": message[1]}, {"password": message[2]}]})
                for i in res:
                    isLoggedIn = True
                
                if(isLoggedIn):
                    username = message[1]
                    c.send(("Logged in as " + username + "\n").encode())
                else:
                    c.send("Invalid Credentials\n".encode())
        elif(message[0] == "CREATE"):
            accountExists = False
            if(len(message) != 3):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({ "username": message[1] })
                for i in res:
                    accountExists = True

                if(accountExists):
                    c.send("Username already taken\n".encode())   
                else:
                    col.insert_one({"username" : message[1], "password" : message[2], "friends" : [], "groups" : []})
                    username = message[1]  
                    c.send(("Logged in as " + username + "\n").encode())  	
        elif(message[0] == "ADDFRIEND"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 2):
                c.send("Invalid Details\n".encode())
            else:
                userExists = False
                res = col.find({"username" : message[1]})
                for user in res:
                    userExists = True

                if(message[1] == username):
                    c.send("Could not perform the action\n".encode())
                elif(not(userExists)):
                    c.send("User does not exist\n".encode())
                elif(message[1] in user["friends"]):
                    c.send("User is already a friend\n".encode())
                else:
                    col.update_one({ "username" : username},{ "$push": { "friends":  message[1]} })
                    col.update_one({ "username" : message[1]},{ "$push": { "friends":  username} })
                    c.send(("Added " + message[1] + " as friend\n").encode())
        elif(message[0] == "CREATEGROUP"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 2):
                c.send("Invalid Details\n".encode())
            else:
                groupExists = False
                res = colG.find({"groupname" : message[1]})
                for group in res:
                    groupExists = True
                
                if(groupExists):
                    c.send("Group already exists\n".encode())
                else:
                    colG.insert_one({"groupname" : message[1], "users" : [username]})
                    col.update_one({ "username" : username},{ "$push": { "groups":  message[1]} })
                    c.send(("Group " + message[1] + " created\n").encode())
        elif(message[0] == "JOINGROUP"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 2):
                c.send("Invalid Details\n".encode())
            else:
                groupExists = False
                res = colG.find({"groupname" : message[1]})
                for group in res:
                    groupExists = True

                if(not(groupExists)):
                    c.send("Group does not exist\n".encode())
                elif(username in group["users"]):
                    c.send("Already a member of the group\n".encode())
                else:
                    col.update_one({ "username" : username},{ "$push": { "groups":  message[1]} })
                    colG.update_one({ "groupname" : message[1]},{ "$push": { "users":  username} })
                    c.send(("Joined " + message[1] + " group\n").encode())
        elif(message[0] == "FRIENDS"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 1):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({"username" : username})
                for user in res:
                    continue

                for i in user["friends"]:
                    c.send((i +"\n").encode())
        elif(message[0] == "GROUPS"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 1):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({"username" : username})
                for user in res:
                    continue

                for i in user["groups"]:
                    c.send((i +"\n").encode())
        else:
            c.send("MESSAGE".encode())


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
print ("Socket successfully created")
port = 12345              
s.bind(('', port))         
print ("socket binded to %s" %(port))  
s.listen(5)     
print ("socket is listening")            
while True: 
    c, addr = s.accept()    
    t = threading.Thread(target=newConnection, args=(c,), daemon = True)
    t.start()
    t.join()