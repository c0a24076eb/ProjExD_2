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

# Rectが画面内にあるか判定
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True

    if obj_rct.left < 0 or WIDTH < obj_rct.right:
            yoko = False

    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
            tate = False

    return yoko, tate

# ゲームオーバー画面を表示
def gameover(screen: pg.Surface) -> None:
    
    """
    ゲームオーバー画面の表示
    """

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

# 爆弾の拡大,加速
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾のサイズと拡大のリスト作成
    """
    
    bb_imgs = []
    bb_accs = []

    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
        bb_accs.append(r)

    return bb_imgs, bb_accs

# こうかとんの向き
def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動方向に対応したこうかとん画像の設定
    """
    
    kk0 = pg.image.load("fig/3.png")
    kkR = pg.transform.flip(kk0, True, False)

    kk_dict = {
        (0, 0):kk0,
        (5, 0): kkR,
        (5, 5): pg.transform.rotozoom(kkR, 315, 1.0),
        (0, 5): pg.transform.rotozoom(kk0, 90, 1.0),
        (-5, 5): pg.transform.rotozoom(kk0, 45, 1.0),
        (-5, 0): pg.transform.rotozoom(kk0, 0, 1.0),
        (-5, -5): pg.transform.rotozoom(kk0, 315, 1.0),
        (0, -5): pg.transform.rotozoom(kkR, 90, 1.0), 
        (5, -5): pg.transform.rotozoom(kkR, 45, 1.0), 
    }

    return kk_dict

# 追尾型爆弾
def calc_orientation(org: pg.Rect,dst: pg.Rect,current_xy:tuple[float, float]) -> tuple[float, float]:  
    """
    爆弾からこうかとんへの方向ベクトル計算
    """ 

    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery

    norm = (dx**2 + dy**2) ** 0.5

    # 近すぎるときは慣性維持
    if norm < 300:
        return current_xy

    # ノルムを √50 にする
    vx = dx / norm * (50 ** 0.5)
    vy = dy / norm * (50 ** 0.5)

    return vx, vy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
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

        # 爆弾の大きさと速度を時間経過で変更
        idx = min(tmr // 500, 9)
        bb_img = bb_imgs[idx]
        
        # 爆弾がこうかとんを追従する方向を計算
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        # 爆弾画像サイズにRectを合わせる
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 爆弾移動
        bb_rct.move_ip(avx, avy)

        # 壁反射
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        # こうかとん移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]

        for k, mv in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        # こうかとん画像切り替え
        old_center = kk_rct.center
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct = kk_img.get_rect()
        kk_rct.center = old_center
        
        #　こうかとん壁
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # ゲームオーバー
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
