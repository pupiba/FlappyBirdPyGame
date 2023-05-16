import random
import pygame as pg
import sys


# функция отрисовки и бесконечного движения земли
def ground():
    screen.blit(ground_img, (ground_xpos, 660))             # отрисовка изображения земли на заданных координатах
    screen.blit(ground_img, (ground_xpos + 500, 660))       # отрисовка дополнительного куска земли


# проверка на столкновение с препятствиями
def check_collusion(obst_lst):
    #
    for obst in obst_lst:
        # если коллизия совподает по x или y, то конец игры
        if bird_collusion.colliderect(obst):
            die_sound.play()
            return False

    # если птица долетает до земли или неба, то конец игры
    if bird_collusion.top <= -100 or bird_collusion.bottom >= 660:
        die_sound.play()
        return False
    else:
        return True


# создание объктов коллизий и помещение их в список
def create_obstacle():
    random_obstaclepos = random.choice(obstacle_height)     # задается рандомное значение для высоты коллизий
    top_obstacle = obstacle.get_rect(midbottom=(700, random_obstaclepos-300))   # верхняя коллизия
    bottom_obstacle = obstacle.get_rect(midtop=(700, random_obstaclepos))       # нижняя коллизия
    return bottom_obstacle, top_obstacle


# смещение препятствий влево (работает как и земля)
def move_obstacle(obst_lst):
    # проход по списку объектов (всегда два)
    for obst in obst_lst:
        obst.centerx -= 5
    return obst_lst


# отрисовка препятствий из списка препятствий
def draw_obstacle(obst_lst):
    for obst in obst_lst:
        if obst.bottom >= 700:
            screen.blit(obstacle, obst)
        else:
            flip_obst = pg.transform.flip(obstacle, False, True)    # переворачиваем по вертикали
            screen.blit(flip_obst, obst)


# отрисовка счета (атрибуты: экран, текст, размер шрифта, координаты по x, по y)
def draw_score(wind, text, size, x, y):
    score_text = pg.font.Font('Comic Sans MS Pixel.ttf', size)      # создаем экземпляр текста
    # создаем рендер теста счета со сглаживанем и белым цветом
    score_text = score_text.render(str(text), True, (255, 255, 255))
    wind.blit(score_text, (x, y))   # помещаем текст на экран


pg.init()   # инициализация библиотеки

# переменные
screen_width = 500      # ширина экрана
screen_height = 700   # высота экрана

movement = 0        # переменная движения птицы
gravity = 0.1      # значение гравитации

is_alive = True

score = 0    # значение счета во время игры
best_score = 0    # новый игровой рекорд

anim_score = False    # воспроизведение счета при проигрыше
new_record_sound_play = True    # воспроизведение звука нового рекорда

# переменные PyGame
frame_rate = pg.time.Clock()

screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption('Взбалмошная птица')

bg = pg.image.load('pictures/bg.png').convert()
bg = pg.transform.scale(bg, (screen_width, screen_height))

bird = pg.image.load('pictures/bird.png')
bird = pg.transform.scale(bird, (75, 75))
bird_collusion = bird.get_rect(center=(100, 350))

ground_img = pg.image.load('pictures/ground.png')
ground_img = pg.transform.scale2x(ground_img)
ground_xpos = 0

menu = pg.image.load('pictures/menu.png')
menu = pg.transform.scale(menu, (250, 350))
game_over_collusion = menu.get_rect(center=(250, 350))

# создание переменных препятствий
obstacle = pg.image.load('pictures/tree.png')   # загрузка кртинки
obstacle_height = [350, 400, 600]           # высота препятствий
obstacle_lst = []           # список для их хранения

# пользовательское событие для генерации препятствий
OBSTACLE_EVENT = pg.USEREVENT
pg.time.set_timer(OBSTACLE_EVENT, 1500)

wing_sound = pg.mixer.Sound('sounds/wing.mp3')
die_sound = pg.mixer.Sound('sounds/die.mp3')
score_sound = pg.mixer.Sound('sounds/point.mp3')
new_game = pg.mixer.Sound('sounds/new_game.mp3')
new_record_sound = pg.mixer.Sound('sounds/win.mp3')

# игровой цикл
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and is_alive:
                movement = 0
                movement -= 5
                wing_sound.play()
            if event.key == pg.K_SPACE and (not is_alive):
                score = 0   # обнуление счета при новом запуске
                anim_score = False  # перестаем воспроизводить текст рекордов
                new_game.play()
                bird_collusion.center = (100, 350)
                movement = 0
                obstacle_lst.clear()
                is_alive = True
        if event.type == pg.USEREVENT and is_alive:
            obstacle_lst.extend(create_obstacle())

    screen.blit(bg, (0, 0))     # отрисовка заднего фона на поверхности

    if is_alive:
        new_record_sound_play = True    # пока мы живы, выставлем значение воспроизведения истинным
        movement += gravity         # смещение каждый кадр игры движения птицы
        bird_collusion.centery += movement  # движение птицы по вертикали
        screen.blit(bird, bird_collusion)  # отрисовка птицы на поверхности

        # отрисовка препятствий
        obstacle_lst = move_obstacle(obstacle_lst)
        draw_obstacle(obstacle_lst)
        draw_score(screen, str(score), 56, screen_width / 2, 10)    # функция отрисовки счета (во время игры)

        # добавление одного очка за пролет между препятствиями
        if len(obstacle_lst) == 0:
            pass
        else:
            # если координаты объектов по оси x совпадают, то добавляем поинт
            if bird_collusion.centerx == obstacle_lst[-1].centerx:
                score_sound.play()
                score += 1
        is_alive = check_collusion(obstacle_lst)    # проверка закончилась ли игра
    else:
        # в случае столкновения обновляем рекорд
        if score > best_score:
            best_score = score
            score = 0
            anim_score = True   # вкулючаем анимацию новго рекорда
        screen.blit(menu, game_over_collusion)      # отрисовываем меню
        if anim_score:
            draw_score(screen, 'Новый рекорд!', 56, screen_width / 6 + 10, 10)
            if new_record_sound_play:
                new_record_sound.play()
        else:
            draw_score(screen, 'Прошлый рекорд:', 56, screen_width / 6 - 30, 10)
        draw_score(screen, str(best_score), 56, screen_width / 2, 90)   # цифры счета
        new_record_sound_play = False   # отключаем звук норвго рекорда, если он не был достигнут

    ground_xpos -= 5  # каждую игровую итерацию позиция земли на поверхности смещается по оси x
    ground()  # отрисовка участков земли
    if ground_xpos <= -500:
        ground_xpos = 0

    pg.display.update()     # обновление экрана
    frame_rate.tick(120)    # установка обновления экрана 120 раз за секунду
