import time
import pygame as p
import protocol
from client import BUFFER, Network

p.init()
WIDTH = HEIGHT = 512
DIMENTION = 8
SQ_SIZE = HEIGHT // DIMENTION  #  The square size
MAX_FPS = 15
IMAGES = {}
PICKLE_BUFF = 4096*8
game_over = False


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        try: #  Linux
            IMAGES[piece] = p.transform.scale(p.image.load(f"img/{piece}.png"), (SQ_SIZE, SQ_SIZE))
        except: #  Windows
            IMAGES[piece] = p.transform.scale(p.image.load(f"img\{piece}.png"), (SQ_SIZE, SQ_SIZE))


def connects():
    global n
    n = Network()
    return n.board
        
    
def main():
    global game_over
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock() #  Takes care of fps
    gs = protocol.recv(n.client) #  The gamestate from the server's dict
    validMoves = protocol.recv(n.client)
    load_images() #  Only done once, before the main loop
    draw_init(screen, gs.board, clock)
    moveMade = False #  Flag variable for when a move is made
    animate = False #  Flag variable for when we should animate a move
    #protocol.client_handshake(n.client, gs)
    running = True
    sqSelected = () #  No squares selected, helps to keep track of the last click of the user
    playerClicks = [] #  keep track of player clicks
    turn = 'w' #  The first to move is always white in chess
    protocol.draw_id(screen, n.currentId)

    #  Main Loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif turn == n.currentId:
                if e.type == p.MOUSEBUTTONDOWN:
                    if not game_over:
                        print('v')
                        location = p.mouse.get_pos()
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if sqSelected == (row, col): #  The user clicked the same square twice
                            sqSelected = () #  Unselect
                            playerClicks = [] #  Clear player clicks
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected) #  Append for both first and second clicks
                        if len(playerClicks) == 2: #  After the 2nd click

                            protocol.send("move", n.client) #  Tell the server you are planning to do a move

                            reply = protocol.ask_move(playerClicks, n.client) #  Send the server the move you want to make
                            
                            if reply == "move made":
                                gs = protocol.recv(n.client)
                                protocol.did_exit(gs, screen)
                                moveMade = True
                                turn = protocol.recv(n.client)
                                protocol.did_exit(turn, screen)
                                validMoves = protocol.recv(n.client)
                                protocol.did_exit(validMoves, screen)
                                reply, is_end = protocol.is_end_client(n.client)
                                if is_end:
                                    game_over = True
                                    running = False
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                                break
                            else:
                                playerClicks = []
                                gs = protocol.recv(n.client)
                                protocol.did_exit(gs, n.client)
                                turn = protocol.recv(n.client)
                                protocol.did_exit(turn, screen)
                                validMoves = protocol.recv(n.client)
                                protocol.did_exit(validMoves, screen)
                                reply, is_end = protocol.is_end_client(n.client)
                                break
            else:
                gs = protocol.recv(n.client)
                protocol.did_exit(gs, screen)
                turn = protocol.recv(n.client)
                protocol.did_exit(turn, screen)
                validMoves = protocol.recv(n.client)
                protocol.did_exit(validMoves, screen)
                reply, is_end = protocol.is_end_client(n.client)
                if is_end:
                    game_over = True
                    running = False
                    break

                if gs != "Not Valid!" and turn == n.currentId:
                    break
                        
            #  Key handlers
            #if e.type == p.KEYDOWN:
            #    if e.key == p.K_z: #  Undo move when 'z' is pressed
            #        gs.undo_move()
            #        moveMade = True
            #        animate = False
            #        print('Undone move!')

        if moveMade:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            moveMade = False
            animate = False

        draw_game_state(screen, gs, validMoves, sqSelected)

        clock.tick(MAX_FPS)
        p.display.flip()

        if game_over:
            drawText(screen, reply)
            clock.tick(MAX_FPS)
            p.display.flip()
            time.sleep(3)
    n.client.close()

'''
    Highlight square selected and moves for selected piece
'''
def highlight_squares(screen, gs, validMoves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #  sq_selected is a piece that can be moved
            #highlight selected squares
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #  Transparency value
            '''s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))'''
            #highlight moves from that square
            s.fill(p.Color('cyan'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))
                    




def draw_init(screen, board, clock):
    draw_board(screen)
    draw_pieces(screen, board)
    clock.tick(MAX_FPS)
    p.display.flip()
'''
    Responsible for all the graphics within the current game state
'''
def draw_game_state(screen, gs, validMoves, sqSelected):
    draw_board(screen) #  Draw the squares on the board
    highlight_squares(screen, gs, validMoves, sqSelected)
    draw_pieces(screen, gs.board) #  Draw pieces on the top of the squares


'''Draw the squares on the board. The top left sqaure is always light.'''
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''Draw pieces on the board using the current <GameState.board>'''
def draw_pieces(screen, board):
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            piece = board[r][c]
            if piece != "--": 
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
    Animating a move
'''
def animate_move(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    fps = 10 #  Frames to move one square
    frame_count = (abs(dR) + abs(dC)) * fps
    for frame in range(frame_count + 1):
        r, c = (move.startRow + dR * frame/frame_count, move.startCol + dC * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #  Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #  Draw captured piece onto rectangle 
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #  Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(144)
    

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Red'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)


if __name__ == "__main__":
    import Menu

    board = connects()
    print(n.currentId)
    try:
        main()
    except Exception as e:
        print(e)
        print("Connection closed")
        n.client.close()

