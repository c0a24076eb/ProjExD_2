import os
import sys
import pygame as pg
import random

WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
        yoko, tate = True, True

        if obj_rct.left < 0 or WIDTH < obj_rct.right:
            yoko = False

        if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
            tate = False

        return yoko, tate

def gameover(screen: pg.Surface) -> None:
    
    # ゲームオーバー画面を表示する関数
    # 引数：スクリーンSurface
    # 戻り値：なし

    black = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(black, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))
    black.set_alpha(200)

    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2

    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.0)
    kk_rct_l = kk_img.get_rect()
    kk_rct_l.center = WIDTH // 2 - 250, HEIGHT // 2
    kk_rct_r = kk_img.get_rect()
    kk_rct_r.center = WIDTH // 2 + 250, HEIGHT // 2

    screen.blit(black, [0, 0])
    screen.blit(txt, txt_rct)
    screen.blit(kk_img, kk_rct_l)
    screen.blit(kk_img, kk_rct_r)
    pg.display.update()
    pg.time.wait(5000)

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.center = (
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT)
    )
    vx, vy = +5, +5
    

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0])
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for k, mv in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        kk_rct.move_ip(sum_mv)

        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        
        screen.blit(kk_img, kk_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
