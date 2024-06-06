import os
import sys
import pygame
import Gui

pygame.init()

font = pygame.font.SysFont("arial", 20)

def inputbox(font):
    screen = pygame.display.set_mode((640, 480))
    font = font
    clock = pygame.time.Clock()
    input_box = pygame.Rect(100, 100, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        # Render the current text.
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

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

sel_rect = -1

buttons = Gui.RadioButtonGroup()
buttons.add(Gui.ToggleButton(screen, (300,585), "Rename", font))

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

    mousepos = pygame.mouse.get_pos()
    buttons.update(mousepos, pressed)
    buttons.draw()

    if pressed:
        for i,rect in enumerate(rects):
            if rect.collidepoint(mousepos):
                index = rects.index(rect)
                if texts[index].text == "":
                    break
                else:
                    if sel_rect == -1 or sel_rect != i:
                        sel_rect = i
                    else:
                        if os.path.isfile(os.path.join(path, texts[index].text)):
                            os.startfile(os.path.join(path, texts[index].text))
                        else:
                            path = os.path.join(path, texts[index].text)
                            data, texts = reload(path)
                            rects = []
                            for i in texts:
                                rects.append(i.rects[-1])
                            sel_rect = -1

    if sel_rect != -1:
        pygame.draw.rect(screen, "#A0A0A0", rects[sel_rect])

    for text in texts:
        text.draw()

    active = buttons.get_active()

    if active == 0:
        if sel_rect == -1:
            for member in buttons.members:
                member.pushed = False
        else:
            org_path = os.path.join(path, texts[index].text)
            newtext = inputbox(font)
            os.rename(org_path, os.path.join(path, newtext))
            active = None
            sel_rect = -1
            data, texts = reload(path)
            for member in buttons.members:
                member.pushed = False
            rects = []
            for i in texts:
                rects.append(i.rects[-1])
            print(buttons.members)

    pygame.display.flip()