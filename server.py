import socket
from _thread import *
from ChessEngine import GameState
import pickle
import protocol
import time
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = '0.0.0.0'
port = 5608

try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server_ip, port))

except socket.error as e:
    s.close()

s.listen()
print("[START] Waiting for a connection")

# Global vars
BUFFER = 1024
connections = 0
currentId = "w"
playerCount = 0
gameIndex = 0
game_ready = [False] #  If the game is ready to begin
can_start = [True] #  If there is no game running at that index it is True
gameClients = [[]] #  [[client1, client2], [client3, client4]]
games = {0:GameState()} #  Games -> {GameState(), GameState()} -- sockets of players
validMovesD = {0:[]} #  Valid moves for each game saved here
lock = threading.Lock()
all_clients = []
turns = []


'''Waits until two clients are connected to a game and starts the client thread so they can play'''
def wait_for_client(conn, gameIndex1, connections):
    global game_ready
    while not game_ready[gameIndex1]:
        pass
    
    conn.sendall(b'Ok') #  Send ok when ready to begin
    
    start_new_thread(threaded_client, (conn, gameIndex1, connections))


def threaded_client(conn, gameIndex, connection):
    global all_clients, lock, validMovesD, games, game_ready, can_start

    if(connection % 2 == 0): #  The second client to connect will always be black
        currentId = "b"
    else:
        currentId = "w"
    
    
    protocol.send(currentId, conn)

    
    gs = games[gameIndex] #  Define the game state
    
    if currentId == 'w':
        validMoves = validMovesD[gameIndex]
        bo = gs.board
    else:
        gs.whiteToMove = False
        validMoves = validMovesD[gameIndex]
        
        bo = gs.board

    time.sleep(0.2)
    protocol.send(bo, conn) #  Sends board to the client
    
    time.sleep(0.2)
    protocol.send(gs, conn) #  Sends the gamestate to the client

    time.sleep(0.1)
    protocol.send(validMoves, conn) #  Send the valid moves to the client
    global connections, playerCount
    try:
        while game_ready[gameIndex]:
            if turns[gameIndex] == currentId:  
                if(turns[gameIndex] == 'b'):
                    games[gameIndex].whiteToMove = False
                else:
                    games[gameIndex].whiteToMove = True

                print(f'listening for client {connection}')
                to_do = protocol.recv(conn)

                if(to_do == "move"):
                    gs, validMoves, flag = protocol.move(conn, games[gameIndex], validMovesD[gameIndex])
                    validMovesD[gameIndex] = validMoves

                    if flag:
                        turns[gameIndex] = protocol.change_turn(turns[gameIndex])

                    if(turns[gameIndex] == 'b'):
                        games[gameIndex].whiteToMove = False
                    else:
                        games[gameIndex].whiteToMove = True

                    games[gameIndex] = gs

                    reply = protocol.is_game_end(gs)

                    with lock:
                        for c in gameClients[gameIndex]:
                            protocol.send(gs, c)
                            time.sleep(0.1)
                            protocol.send(turns[gameIndex], c)
                            time.sleep(0.1)
                            protocol.send(validMoves, c)
                            time.sleep(0.1)
                            protocol.send(reply, c)

                    if reply != "no":
                        game_ready[gameIndex] = False
            else:
                time.sleep(0.3)

    except Exception or EOFError or IndexError:
        print(f"Game {gameIndex} has ended")
        connections -= 1
        playerCount -= 1
        all_clients.remove(conn)
        if protocol.is_game_end(gs) != "no":
            pass
        else:
            with lock:
                for c in gameClients[gameIndex]:
                    if c in all_clients:
                        protocol.send("You won", c)

        try:
            game_ready[gameIndex] = False
            can_start[gameIndex] = True
            turns[gameIndex] = "w"
            gameClients[gameIndex] = []
            print(f'Game {gameIndex} reseted')

        except Exception as e:
            print("There was an error with reseting the game")
            print(e)

        conn.close()       
        exit() #  Exit thread
    
    #  Doing it twice because only one client actually catches the exception
    connections -= 1
    playerCount -= 1
    all_clients.remove(conn)
    conn.close()
    exit()
    




if __name__ == '__main__':
    while True:
        conn, addr = s.accept()
        all_clients.append(conn)
        connections += 1

        playerCount += 1

        gameIndex = 0

        flag = True

        while flag:
            if can_start[gameIndex]:
                if(connections % 2 == 1):
                    games[gameIndex] = GameState()
                    game_ready.append(False)
                    can_start.append(True)
                    try:
                        gameClients[gameIndex] = [conn]
                    except:
                        gameClients.append([conn])
                        
                    flag = False
                else:
                    games[gameIndex].ready = True
                    game_ready[gameIndex] = True
                    can_start[gameIndex] = False
                    validMovesD[gameIndex] = games[gameIndex].get_valid_moves()
                    turns.append("w")
                    gameClients[gameIndex].append(conn)
                    print(f"Game: {gameIndex}, has started!")
                    flag = False
            else:
                gameIndex += 1
                
            


        print(f"Connected to: {addr}")

        #reply_buf = bytes(reply, encoding='ascii')
        
        reply = protocol.server_handshake(game_ready, conn, gameIndex)

        print(f'The game index is {gameIndex}')
        print(gameClients)
        start_new_thread(wait_for_client, (conn, gameIndex, connections))
        
        
