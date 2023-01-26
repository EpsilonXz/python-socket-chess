import pygame as p
from ChessMain import WIDTH, HEIGHT

p.init()

black = (0,0,0)
white = (255,255,255)

screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption('Chess project - The game')
clock = p.time.Clock()

try: #  Works for linux
    img = p.image.load('img/ChessBoardPic.jpg')

    start_img = p.image.load('img/start_btn.png').convert_alpha()
    exit_img = p.image.load('img/exit_btn.png').convert_alpha()
except: #  Works for windows
    img = p.image.load('img\ChessBoardPic.jpg')

    start_img = p.image.load('img\start_btn.png').convert_alpha()
    exit_img = p.image.load('img\exit_btn.png').convert_alpha()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self):
        action = False

        # draw button on screen
        screen.blit(self.image, (self.rect.x, self.rect.y))

        # Get mouse position
        pos = p.mouse.get_pos()

        #Check mouseover and clicked condition
        if self.rect.collidepoint(pos):
            if p.mouse.get_pressed()[0] == 1 and self.clicked == False:
                print('clicked')
                self.clicked = True
                action = True
        
        if p.mouse.get_pressed()[0] == 0:
            self.clicked = False
        
        return action


# Create button instances
start_button = Button(100, 200, start_img)
exit_button = Button(300, 200, exit_img)


def game_intro():

    intro = True

    while intro:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                quit()

        screen.fill(white)
        screen.blit(img, (0, 0))

        if start_button.draw(): 
            print('STARTING...')
            intro = False
        elif exit_button.draw(): 
            print('QUITTING...')
            exit()
        
        
        p.display.flip()



game_intro()
        
