import struct
import pickle
import sys
import pygame
import os
import ChessEngine
import ChessMain
import time

BUFFER = 1024


#Lets the user enter an input, if nothing is entred he gets to try again
def EnterInput(msg):
    data = input(f"{msg}")
    if(len(data) == 0):
        while len(data) == 0:
            data = input("You typed nothing, try again... \n")
    return data


#User sends message
#def send_board(board, sock):
#    msg = str(board)
#    length = len(msg)
#    length_to_send = struct.pack("l", length)
#    sock.send(length_to_send)
#    to_send = sock.send(msg.encode())
#
#
##Recieves packed msg and returns unpacked data
def recv_unpack_length(sock):
    Unpacked = sock.recv(4)
    Unpacked = struct.unpack("i", Unpacked)
    Unpacked = Unpacked[0]
    return Unpacked


##Recieves and decodes the unpacked data
#def recv_board(sock):
#    length = recv_unpack_length(sock)
#    data = sock.recv(length)
#    data = data.decode()
#    board = ast.literal_eval(data)
#    print(board)
#    return board


def send(data, sock):
    data_string = pickle.dumps(data)
    sock.send(data_string)


def recv(sock):
    data = sock.recv(4096*8)
    return pickle.loads(data)


def waiting_client_screen() -> None:
    from ChessMain import WIDTH, HEIGHT
    display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Waiting for client')
    chessbg = pygame.image.load(os.path.join("img", "load-sc.jpg"))
    display_surface.fill((255,255,255))
    display_surface.blit(chessbg, (0, 0))
    pygame.display.update()

def server_handshake(game_ready, conn, gameIndex) -> str:
    if game_ready[gameIndex]:
        send("ready", conn)
        
    else:
        send("show", conn)
        print(f"{gameIndex} Waiting for second client")
        return 'wait'

    reply = recv(conn)
    print(reply)
    print(f'Game {gameIndex} is starting!')
    return reply
    


def client_handshake(sock):
    to_show = recv(sock)

    if to_show == "show":
        waiting_client_screen()

    else:
        send('Ok', sock) #  When the game is ready the client will tell the server that it connected
    
    r = sock.recv(BUFFER).decode()
    print(r)


def ask_move(playerClicks, sock):
    print(playerClicks)
    time.sleep(0.2)
    send(playerClicks, sock) #  Send the clicks of the player
    reply = recv(sock)

    return reply


def move(sock, gs, validMoves):
    playerClicks = recv(sock)
    print(playerClicks)
    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
    flag = False

    for i in range(len(validMoves)):
        if move == validMoves[i]:
            gs.make_move(validMoves[i])
            send("move made", sock)
            print("Move made")
            flag = True
            break
        else:
            flag = False

    if not flag:
        print('Invalid')
        send("Not Valid!", sock)

    validMoves = gs.get_valid_moves()
    return gs, validMoves, flag


def change_turn(turn) -> str:
    if turn == 'w':
        return 'b'
    else:
        return 'w'


def is_game_end(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return "Black wins by checkmate"
        else:
            return "White wins by checkmate"

    elif gs.stalemate:
        return "stalemate"

    else:
        return "no"

def is_end_client(sock) -> bool:
    reply = recv(sock)

    if reply != "no":
        return reply, True
    
    else:
        return reply, False


def did_exit(data, screen):
    if data == "You won":
        print('ys')
        ChessMain.drawText(screen, data)
        pygame.display.flip()
        time.sleep(2)
        sys.exit() #  Terminate the program
    
    else:
        pass


def draw_id(screen, id):
    if id == 'w':
        ChessMain.drawText(screen, "You are white")
    else:
        ChessMain.drawText(screen, "You are black")
    
    pygame.display.flip()
    time.sleep(1.5)

