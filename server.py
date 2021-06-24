import threading
import socket 
import pymongo
#import dns
mongoclient = pymongo.MongoClient("mongodb+srv://mydb:******@cluster0.xa7aq.mongodb.net/mydb?retryWrites=true&w=majority")
db = mongoclient["mydb2"]
col = db["users"]
colG = db["groups"]
colC = db["chats"]
connections = {}
def newConnection(c):
    c.send("Enter HELP to see commands\n".encode())
    username = ""
    connectedTo = ""
    connectedToUser = False
    connectedToGroup = False
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
            c.send("DISCONNECT                - to disconnect\n".encode())
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
                    connections[username] = c
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
                    connections[username] = c 	
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
                    colC.insert_one({"type" : "userToUser", "name" : username + "&" + message[1], "sender" : [], "message" : []})
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
                    colC.insert_one({"type" : "group", "name" : message[1], "sender" : [], "message" : []})
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
        elif(message[0] == "CONNECTUSER"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 2):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({"username" : username})
                for user in res:
                    continue

                connectedTo = ""
                connectedToUser = False
                connectedToGroup = False
                for i in user["friends"]:
                    if(i == message[1]):
                        connectedToUser = True
                        connectedTo = message[1]
                        break
                
                if(connectedTo == ""):
                    c.send("User is not a friend\n".encode())
                else:
                    c.send(("Connected to " + message[1] + "\n").encode())
        elif(message[0] == "CONNECTGROUP"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 2):
                c.send("Invalid Details\n".encode())
            else:
                res = col.find({"username" : username})
                for user in res:
                    continue
                
                connectedTo = ""
                connectedToUser = False
                connectedToGroup = False
                for i in user["groups"]:
                    if(i == message[1]):
                        connectedToGroup = True
                        connectedTo = message[1]
                        break
                
                if(connectedTo == ""):
                    c.send("Join the group to send messages\n".encode())
                else:
                    c.send(("Connected to " + message[1] + "\n").encode())
        elif(message[0] == "DISCONNECT"):
            if(len(message) != 1):
                c.send("Invalid Details\n".encode())
            elif(connectedTo == ""):
                c.send("Your are not connected to any user or group\n".encode())
            else:
                connectedTo = ""
                c.send("Successfully disconnected\n".encode())
        elif(message[0] == "HISTORY"):
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(len(message) != 1):
                c.send("Invalid Details\n".encode())
            elif(connectedTo == ""):
                c.send("Connect to user or a group to see history\n".encode())
            else:
                if(connectedToUser):
                    res = colC.find({"$or" : [{ "name": username + "&" + connectedTo}, {"name": connectedTo + "&" +username}]})
                    for chat in res:
                        continue
                else:
                    res = colC.find({"name" : connectedTo})
                    for chat in res:
                        continue
                
                sender = chat["sender"]
                messages = chat["message"]

                for i in range(0, len(sender)):
                    c.send((sender[i] + " : " + messages[i] + "\n").encode())
        else:
            if(username == ""):
                c.send("Login to perform the action\n".encode())
            elif(connectedTo == ""):
                c.send("You are not connected to any user or group\n".encode())
            else:
                if(connectedToUser):
                    clist = [connectedTo]
                    colC.update_one({"$or" : [{ "name": username + "&" + clist[0]}, {"name": clist[0] + "&" +username}]},{"$push": { "sender":  username}})
                    colC.update_one({"$or" : [{ "name": username + "&" + clist[0]}, {"name": clist[0] + "&" +username}]},{"$push": { "message":  " ".join(message)}})
                else:
                    res = colG.find({"groupname" : connectedTo})
                    for group in res:
                        continue

                    clist = group["users"]
                    colC.update_one({"name" : connectedTo},{"$push": { "sender":  username}})
                    colC.update_one({"name" : connectedTo},{"$push": { "message":  " ".join(message)}})

                for i in clist:
                    if i in connections:
                        if(i != username):
                            try:
                                connections[i].send((username + " : " + " ".join(message) + "\n").encode())
                            except:
                                print(connections[i])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
print ("Socket successfully created")
port = 12345              
s.bind(('', port))         
print ("socket binded to %s" %(port))  
s.listen(5)     
print ("socket is listening")            
while True: 
    c, addr = s.accept()    
    print("Connection received from" , addr)
    t = threading.Thread(target=newConnection, args=(c,), daemon = True)
    t.start()
    print("Connection successful")
