import os
import sys
import pygame

pygame.init()

font = pygame.font.SysFont("arial", 20)

def sep_text(text: str, breakpoint = 10):
    spaces = []
    texts = []
    posi = 1
    old_space = 0
    for i,char in enumerate(text):
        if char.isspace():
            spaces.append(i)
    
    for space in spaces:
        if space // breakpoint >= posi:
            posi += 1
            texts.append(text[old_space:space].strip())
            old_space = space
            
    texts.append(text[old_space:])
    return texts

class Text:
    
    def __init__(self, text: str, pos: tuple, scale, color = "#000000", breakpoint = 10, line_spacing = 5):
        
        self.text = text
        last_height = 0
        self.rects = []
        self.surfaces = []
        texts = sep_text(text, breakpoint)
        
        for string in texts:
            surface = font.render(string, False, color)
            surface = pygame.transform.scale_by(surface, scale)
            rect = surface.get_rect()
            rect.x = pos[0]
            rect.y = pos[1] + last_height + line_spacing
            last_height = rect.bottom - pos[1]
            self.surfaces.append(surface)
            self.rects.append(rect)

        
    def draw(self):
        for i in range(len(self.rects)):
            screen.blit(self.surfaces[i], self.rects[i])


def reload(path, folders_first = False):
    data = os.listdir(path)
    files = [f for f in data if os.path.isfile(os.path.join(path, f))]
    folders = [f for f in data if not os.path.isfile(os.path.join(path, f))]
    data = files + [""] + folders if not folders_first else folders + [""] + files
    texts = []
    pos = (0,0)
    for dir in data:
        texts.append(Text(dir, pos, 1, "#FFFFFF", 100000000, 20))
        pos = texts[-1].rects[-1].topleft

    return data, texts 

path = os.path.abspath(os.path.dirname(__file__))
screen = pygame.display.set_mode((600,600))


booting = True
last = 0

while True:
    screen.fill("#000000")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_just_released()
    if keys[pygame.K_ESCAPE] or booting:
        booting = False
        path = os.path.dirname(path)
        data, texts = reload(path)
        rects = []
        for i in texts:
            rects.append(i.rects[-1])

    pressed = False
    if pygame.mouse.get_pressed()[0]:
        last = 1
    else:
        if last == 1:
            last = 0
            pressed = True
        last = 0

    if pressed:
        pos = pygame.mouse.get_pos()
        for rect in rects:
            if rect.collidepoint(pos):
                index = rects.index(rect)
                if texts[index].text == "":
                    break
                else:
                    if os.path.isfile(os.path.join(path, texts[index].text)):
                        os.startfile(os.path.join(path, texts[index].text))
                    else:
                        path = os.path.join(path, texts[index].text)
                        print(path)
                        data, texts = reload(path)
                        rects = []
                        for i in texts:
                            rects.append(i.rects[-1])

    for text in texts:
        text.draw()

    pygame.display.flip()