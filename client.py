import socket
import pickle

# Connecting to vayu server via port 9801
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('10.17.7.134',9801))

# client.send("SESSION RESET\n".encode("utf-8"))
# x = client.recv(4096).decode()
# print(x)

# connecting to the master server via port 5051
client1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client1.connect(('10.194.62.147',5051))

#Declaring an empty dictionary
dic = {}
#Number of lines remaining 
lines_remaining = 1000

# This variable checks whether the master server has recieved all 1000 lines
server_received = 0

while True: 
    client.send("SENDLINE\n".encode("utf-8"))

    ct= 0
    msg = ""
    # Receiving data until we encounter 2 endlines
    while ( ct < 2):
        data = client.recv(1024).decode("utf-8")
        ct += data.count('\n')
        msg+=data

    #Checks if the msg variable is empty or not
    if(msg != ''):
        line_no = int( str.split(msg,"\n")[0])
        
        sentence = ( str.split(msg,"\n")[1])
        if ( line_no != -1):
            if dic.get(line_no) is None:
                client1.send(msg.encode("utf-8"))
                dic[line_no] = sentence
                lines_remaining -= 1
                server_received	 = int (client1.recv(1).decode("utf-8"))


            if lines_remaining == 0 or server_received == 1:
                break


while True: 
    temp = b''
    while True:
        chunk = client1.recv(4096)
        if chunk.endswith(b"END"):
            x = chunk[:-3]
            temp += x
            break
        temp += chunk
    
    dic = pickle.loads(temp)
    break

# Closing connection to master server
client1.close()

dic = dict(sorted(dic.items()))


client.send("SUBMIT\n2023MCS2492@avengers\n1000\n".encode("utf-8"))

for key,value in dic.items():
    client.send(f"{key}\n{value}\n".encode("utf-8"))

submit_msg = client.recv(4096).decode("utf-8")

print(submit_msg)

# Closing connection to vayu server

client.close()
