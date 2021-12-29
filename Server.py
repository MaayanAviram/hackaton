from socket import *
import time
import random
from threading import *
import struct
import colorama
import scapy.all

class Server:

    def __init__(self):
        '''constructor for the server that initalize the the
        data structures for the game'''
        self.clients = []
        self.is_1_correct = False
        self.is_2_correct = False
        self.time_1_answered = 0
        self.time_2_answered = 0
        self.my_ip = gethostbyname(gethostname())
        colorama.init()
        print(f'{colorama.Fore.GREEN} Server started,listening on IP address ' + self.my_ip)

    
    def spread_the_message(self):
        message_to_send = struct.pack('Ibh', 0xabcddcba, 0x2, 2095)
        send_until = time.time() + 10
        udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_socket.bind(('', 2095))
        while time.time() <= send_until:
            udp_socket.sendto(message_to_send, ('<broadcast>', 13117))
            time.sleep(1)
        udp_socket.close()



    def accept_clients(self, tcp_socket):
        '''method for accepting clients that recived the
        offer for join the game'''
        cnt = 0
        while cnt < 2:
            try:
                connection, addr = tcp_socket.accept()
                self.add_new_client(connection, addr)
                cnt += 1
            except:
                continue



    def add_new_client(self, client, addr):
        '''adding new client for the game'''
        client.settimeout(10)
        if len(self.clients) < 2:
            try:
                name = client.recv(1024)
                name = name.decode(encoding='utf-8')
                self.clients.append([name, client, addr])
            except:
                return


    def communicate_with_client(self, client):
        '''method for communicate with the clients during the game,
        send messages to the client about the game and receives the pressed keys
        from the clients and count them for their group during the game'''
        respond = f'{colorama.Fore.LIGHTMAGENTA_EX}Welcome to Quick Maths.\n'
        respond += "Player 1: " + str(self.clients[0][0]) + "\n Player 2: " + str(self.clients[1][0])
        respond += "\n==\nPlease answer the following question as fast as you can:\nHow much is "
        numbers = [i for i in range(10)]
        rand_nums = random.sample(numbers, 2)        
        question = str(rand_nums[0]) + "+" + str(rand_nums[1])
        respond += question
        ans = rand_nums[0]  + rand_nums[1]
        try:
            client.send(str.encode(respond))
        except:
            print(f'{colorama.Fore.RED}connection lost')
            return
        start = time.time()
        while time.time() < start + 10:
            try:
                msg = client.recv(1024).decode(encoding='utf-8')
                if msg is not None: 
                    if msg == str(ans):
                        if client == self.clients[0][1]:
                            self.is_1_correct = True
                            self.time_1_answered = time.time() - start
                        elif client == self.clients[1][1]:
                            self.is_2_correct = True
                            self.time_2_answered = time.time() - start
                        return
                    else:
                        if client == self.clients[0][1]:
                            self.time_1_answered = time.time() - start
                        elif client == self.clients[1][1]:
                            self.time_2_answered = time.time() - start
            except:
                return

    def server_main_func(self):
        '''method that manage the server, using all the functions above
        and arrange the game groups and starts the threads for each client'''
        dest_port = 2095
        flag = False
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        tcp_socket.bind(('', dest_port))
        tcp_socket.listen(100)
        tcp_socket.settimeout(1)  
        while not flag:
            t1 = Timer(0.1, self.spread_the_message)
            t2 = Timer(0.1, self.accept_clients, args=(tcp_socket,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            if len(self.clients) > 0:
                flag = True
                tcp_socket.close()
                tcp_socket = socket(AF_INET, SOCK_STREAM)
                tcp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                tcp_socket.bind((self.my_ip, dest_port))
                tcp_socket.listen(100)
                tcp_socket.settimeout(1)
        T1 = Timer(0.1, self.communicate_with_client, args=(self.clients[0][1]))
        T2 = Timer(0.1, self.communicate_with_client, args=(self.clients[1][1]))
        T1.start()
        T2.start()
        T1.join()
        T2.join()

        message = "Game Over!\n"
        winner = ""
        message += "The correct answer was 5!\n"

        if self.time_1_answered == 0 and self.time_2_answered == 0:
            winner = "No one answered, It was a draw"
        if self.time_1_answered < self.time_2_answered:
            if self.is_1_correct:
                winner = "Congratulations to the winner: " + str(self.clients[0][0])
            else:
                winner = "Congratulations to the winner: " + str(self.clients[1][0])
        else:
            if self.is_2_correct:
                winner = "Congratulations to the winner: " + str(self.clients[1][0])
            else:
                winner = "Congratulations to the winner: " + str(self.clients[0][0])
        message += winner
        try:
            self.clients[0][1].send(str.encode(message))
        except:
            print("client is not available")
        try:
            self.clients[1][1].send(str.encode(message))
        except:
            print("client is not available")

        tcp_socket.close()
        print("Game over, sending out offer requests...")
        self.reset()

    def reset(self):
        '''reset the class field after a game over'''
        self.clients.clear()
        self.is_1_correct = False
        self.is_2_correct = False
        self.time_1_answered = 0
        self.time_2_answered = 0


def run_server(server):
    '''driver code for the server'''
    while True:
        server.server_main_func()
        time.sleep(1)

server = Server()
run_server(server)
