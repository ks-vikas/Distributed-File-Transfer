import socket
import threading
import pickle
import time
import matplotlib.pyplot as plt


SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((SERVER,5051))

no_of_clients = 3

# Defining array lineno and time_array for the graph plot
lineno = [i for i in range(1000)]
time_array = [0 for i in range(1000)]

# Creating an empty dictionary to store the line no and the line
dic = {}
lines_remaining = 1000

# threads1 contains all the threads that handle the clients sending data to this master server
threads1 = []
# threads2 contains all the threads that handle this master server sending data to the other clients
threads2 = []

# Declaring lock to lock the thread while receiving from other clients
lock = threading.Lock()

print("SERVER STARTED")

#start time required for plotting graph
start_time = time.perf_counter()

def handle_clients(conn,addr):
    global lines_remaining
    global dic
    while True:
        ct= 0
        msg = ""
        while ( ct < 2):
            data = conn.recv(1024).decode("utf-8")
            ct += data.count('\n')
            msg+=data
        line_no =  int( str.split(msg,"\n")[0])
        sentence = ( str.split(msg,"\n")[1])
        with lock:
            if dic.get(line_no) is None:
                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                time_array[1000 - lines_remaining] = elapsed_time
                dic[line_no] = sentence
                lines_remaining -= 1
                #print(lines_remaining)
            if lines_remaining == 0:
                conn.send("1".encode("utf-8"))
                break
            else:
                conn.send("0".encode("utf-8"))
    plt.plot(lineno,time_array)
    plt.xlabel("Number of lines received")
    plt.ylabel("Time in seconds")
    plt.title(f"{no_of_clients} clients")
    plt.grid(True)
    plt.savefig('client.png')
    
thread_count = 0

def send_data(conn,addr):
    global dic
    global lines_remaining
    global thread_count
    print("INSIDE SEND_DATA FUNCTION")
    data_bytes = pickle.dumps(dic)
    conn.send(data_bytes)
    conn.send(b"END")

def start():
    global lines_remaining
    global thread_count
    server.listen(3)
    for _ in range(no_of_clients):
        conn, addr = server.accept()
        thread_count +=1
        xyz = 0 
        print(f"CONNECTED TO {conn} x::{thread_count}")
        thread = threading.Thread(target=handle_clients,args=(conn,addr))
        thread_send = threading.Thread(target=send_data,args=(conn,addr))
        thread.start()
        threads1.append(thread)
        print(thread_send)
        threads2.append(thread_send)
        print(f"CONN: {conn} BETWEEN Start and join")
        print(f"Active threads: {threading.active_count()}")
    # Waiting for the other clients to stop sending data since the master server has received all 1000 lines
    for t in threads1:
            t.join()
    # starting threads to send the dictionary from this master server to other clients
    for t in threads2:
        print(t)
        t.start()
    # waiting for all the clients to receive the dictionary
    for t in threads2:
        t.join()

#calling start function to begin
start()