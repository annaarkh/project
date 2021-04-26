import math
import os
import pygame
import requests
import sys
import json
from pgu import gui
from flask import Flask


app = Flask(__name__)


dt = json.dumps({})


@app.route('/')
def index():
    global data
    return data


lat_step, lon_step = 0.008, 0.02
coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
width = 600
height = 450


def load_image(pth, name, colorkey=None):
    fullname = os.path.join("C:/Users/1/Desktop/project/" + pth, name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class MapParams(object):
    def __init__(self):
        self.x = 60.597465
        self.y = 56.838011
        self.zoom = 16
        self.type = "map"

    def update1(self, event):
        my_step = 0.0005
        c = my_step * math.pow(2, 15 - self.zoom)
        if event.key == pygame.K_1:
            self.type = "map"
        elif event.key == pygame.K_2:
            self.type = "sat"
        elif event.key == pygame.K_3:
            self.type = "sat,skl"
        elif event.key == pygame.K_LEFT and self.x - c > 45:  # LEFT_ARROW
            self.x -= c
        elif event.key == pygame.K_RIGHT and self.x + c < 75:  # RIGHT_ARROW
            self.x += c
        elif event.key == pygame.K_UP and self.y + c < 71:  # UP_ARROW
            self.y += c
        elif event.key == pygame.K_DOWN and self.y - c > 41:  # DOWN_ARROW
            self.y -= c

    def update2(self, event):
        if event.button == 4 and self.zoom < 20:  # Page_UP
            self.zoom += 1
        elif event.button == 5 and self.zoom > 14:  # Page_DOWN
            self.zoom -= 1

    def ll(self):
        return str(self.x) + "," + str(self.y)


class Search(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("/pics", "magnifying-glass.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() // 15,
                                                         self.image.get_height() // 15))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (width - 20, 20)


def load_map(mp):
    map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={type}".format(ll=mp.ll(), z=mp.zoom, type=mp.type)
    mresponse = requests.get(map_request)
    if not mresponse:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", mresponse.status_code, "(", mresponse.reason, ")")
        sys.exit(1)

    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(mresponse.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)
    return map_file


def check(pos):
    if sch.rect.collidepoint(pos):
        return True
    return False


class SimpleDialog(gui.Dialog):
    def __init__(self, title):
        self.title = gui.Label(title)
        t = gui.Table()
        t.tr()
        self.line = gui.Input(size=49)
        self.line.connect(gui.KEYDOWN, self.lkey)
        t.td(self.line)
        main = gui.Container(width=20, height=20)
        # passing the 'height' parameter resulting in a typerror when paint was called
        gui.Dialog.__init__(self, self.title, t)

    def open(self,w=None,x=None,y=None):
        global d_opened
        d_opened = True
        super().open()


    def lkey(self, _event):
        e = _event
        if e.key == pygame.K_RETURN:
            global resp
            global lg
            resp = self.line.value
            lg = True
            self.close()
            self.line.value = ""

    def close(self, *args, **kwargs):
        print("closing")
        global d_opened
        d_opened = False
        return super(SimpleDialog, self).close(*args, **kwargs)


def screen_to_geo(pos):
    dy = 225 - pos[1]
    dx = pos[0] - 300
    lx = mp.x + dx * coord_to_geo_x * 2 ** (15 - mp.zoom)
    ly = mp.y + dy * coord_to_geo_y * math.cos(math.radians(mp.y)) * 2 ** (15 - mp.zoom)
    return str(lx) + " " + str(ly)


if __name__ == "__main__":
    #app.run(host='localhost', port=5000)

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((width, height))
    mp = MapParams()
    map_file = load_map(mp)

    all_sprites = pygame.sprite.Group()
    sch = Search()
    all_sprites.add(sch)

    app = gui.App()

    dialog1 = SimpleDialog("Search")
    dialog2 = SimpleDialog("Type")

    empty = gui.Container(width=width, height=height)
    app.init(empty)

    app.paint(screen)
    pygame.display.flip()
    resp = ""
    ps = ""
    d_opened = False
    lg = False
    lg1 = False
    with open('coords.json', 'w') as outfile:
        json.dump({}, outfile)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os.remove(map_file)
                sys.exit()
            if lg and lg1:
                lg = False
                lg1 = False
                with open('coords.json') as f:
                    data = json.load(f)
                    print(data)
                    if resp not in data.keys():
                        data.update({resp: [ps]})
                    elif ps not in data[resp]:
                        data[resp].append(ps)
                    with open('coords.json', 'w') as outfile:
                        json.dump(data, outfile)
            elif lg:
                response = requests.get(
                    "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={}&format=json".format(resp))
                lg = False
                if response:
                    json_response = response.json()
                    print(json_response)
                    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                    toponym_coodrinates = toponym["Point"]["pos"].split()
                    mp.x = float(toponym_coodrinates[0])
                    mp.y = float(toponym_coodrinates[1])
                    map_file = load_map(mp)
                    screen.blit(pygame.image.load(map_file), (0, 0))
                    all_sprites.draw(screen)
            elif not d_opened:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    # print("opening")
                    dialog1.open()
                    app.event(event)
                    # print(d_opened)
                elif event.type == pygame.KEYDOWN:
                    mp.update1(event)
                elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                    mp.update2(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if check(event.pos):
                        dialog1.open()
                    else:
                        dialog2.open()
                        lg1 = True
                        # print(event.pos)
                        ps = screen_to_geo(event.pos)
                    app.event(event)
                map_file = load_map(mp)
                screen.blit(pygame.image.load(map_file), (0, 0))
                all_sprites.draw(screen)
            else:
                app.event(event)
        # print(mp.zoom, mp.x, mp.y, d_opened, resp)
        app.paint(screen)
        pygame.display.flip()
        clock.tick(30)