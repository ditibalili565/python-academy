import pygame
import random
import sys
import json
import urllib.request

# --- Konfigurimi ---
GJERESIA         = 600
LARTESIA         = 600
MADHESIA_BLLOKUT = 20
FPS              = 7
MOLLA_MAX        = 1
SERVER           = "http://127.0.0.1:8000"

BARDHE  = (255, 255, 255)
ZI      = (0,   0,   0  )
GJELBER = (0,   200, 0  )
KUQE    = (200, 0,   0  )
HIRI    = (40,  40,  40 )
KALTER  = (56,  189, 248)

pygame.init()
ekrani       = pygame.display.set_mode((GJERESIA, LARTESIA))
pygame.display.set_caption("Snake - Python Academy")
orari        = pygame.time.Clock()
fonti        = pygame.font.SysFont("Courier New", 28, bold=True)
fonti_i_madh = pygame.font.SysFont("Courier New", 48, bold=True)
fonti_vogel  = pygame.font.SysFont("Courier New", 20)


def merr_emrin():
    """Merr emrin nga argumenti ose pyet perdoruesin."""
    if len(sys.argv) > 1:
        return sys.argv[1]

    emri = ""
    duke_shkruar = True
    while duke_shkruar:
        ekrani.fill(ZI)
        t1 = fonti_i_madh.render("Snake", True, KALTER)
        t2 = fonti.render("Shkruaj emrin tend:", True, BARDHE)
        t3 = fonti_vogel.render("(shtyp Enter per te vazhduar)", True, HIRI)
        t_emri = fonti.render(emri + "|", True, KALTER)
        ekrani.blit(t1,    (GJERESIA//2 - t1.get_width()//2,    150))
        ekrani.blit(t2,    (GJERESIA//2 - t2.get_width()//2,    240))
        ekrani.blit(t_emri,(GJERESIA//2 - t_emri.get_width()//2,280))
        ekrani.blit(t3,    (GJERESIA//2 - t3.get_width()//2,    340))
        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and emri.strip():
                    duke_shkruar = False
                elif ev.key == pygame.K_BACKSPACE:
                    emri = emri[:-1]
                elif len(emri) < 20:
                    emri += ev.unicode
        orari.tick(30)

    return emri.strip() or "Mysafir"


def ruaj_pike(emri, pike):
    """Dergo piket tek serveri lokal."""
    try:
        payload = json.dumps({"emri": emri, "pike": pike}).encode()
        req = urllib.request.Request(
            f"{SERVER}/ruaj-snake",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass  # nese serveri nuk eshte i disponueshem, vazhdo


def gjenero_nje_ushqim(gjarperi, mollat_ekzistuese):
    while True:
        x = random.randrange(0, GJERESIA, MADHESIA_BLLOKUT)
        y = random.randrange(0, LARTESIA, MADHESIA_BLLOKUT)
        if (x, y) not in gjarperi and (x, y) not in mollat_ekzistuese:
            return (x, y)


def gjenero_mollat(gjarperi, mollat_ekzistuese):
    mollat = list(mollat_ekzistuese)
    while len(mollat) < MOLLA_MAX:
        mollat.append(gjenero_nje_ushqim(gjarperi, mollat))
    return mollat


def vizato_gjarper(ekrani, gjarperi):
    for i, (x, y) in enumerate(gjarperi):
        ngjyra = KALTER if i == 0 else GJELBER
        pygame.draw.rect(ekrani, ngjyra,
                         (x, y, MADHESIA_BLLOKUT-2, MADHESIA_BLLOKUT-2),
                         border_radius=4)


def vizato_mollat(ekrani, mollat):
    for (x, y) in mollat:
        pygame.draw.rect(ekrani, KUQE,
                         (x, y, MADHESIA_BLLOKUT-2, MADHESIA_BLLOKUT-2),
                         border_radius=6)


def shfaq_score(ekrani, score, emri):
    t = fonti.render(f"Pike: {score}  |  {emri}", True, BARDHE)
    ekrani.blit(t, (10, 10))


def ekran_fund(ekrani, score, emri):
    ekrani.fill(ZI)
    msg1 = fonti_i_madh.render("LOJA MBAROI!", True, KUQE)
    msg2 = fonti.render(f"Pike: {score}", True, BARDHE)
    msg3 = fonti_vogel.render(f"Perdoruesi: {emri}", True, KALTER)
    msg4 = fonti.render("Shtyp R per te rifilluar", True, HIRI)
    msg5 = fonti.render("Shtyp Q per te dale", True, HIRI)
    ekrani.blit(msg1, (GJERESIA//2 - msg1.get_width()//2, 160))
    ekrani.blit(msg2, (GJERESIA//2 - msg2.get_width()//2, 230))
    ekrani.blit(msg3, (GJERESIA//2 - msg3.get_width()//2, 270))
    ekrani.blit(msg4, (GJERESIA//2 - msg4.get_width()//2, 330))
    ekrani.blit(msg5, (GJERESIA//2 - msg5.get_width()//2, 370))
    pygame.display.flip()


def loja_kryesore(emri):
    gjarperi     = [(300, 300), (280, 300), (260, 300)]
    drejtimi     = (MADHESIA_BLLOKUT, 0)
    mollat       = gjenero_mollat(gjarperi, [])
    score        = 0

    while True:
        for ngjarje in pygame.event.get():
            if ngjarje.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ngjarje.type == pygame.KEYDOWN:
                if ngjarje.key in (pygame.K_UP, pygame.K_w) and drejtimi != (0, MADHESIA_BLLOKUT):
                    drejtimi = (0, -MADHESIA_BLLOKUT)
                elif ngjarje.key in (pygame.K_DOWN, pygame.K_s) and drejtimi != (0, -MADHESIA_BLLOKUT):
                    drejtimi = (0, MADHESIA_BLLOKUT)
                elif ngjarje.key in (pygame.K_LEFT, pygame.K_a) and drejtimi != (MADHESIA_BLLOKUT, 0):
                    drejtimi = (-MADHESIA_BLLOKUT, 0)
                elif ngjarje.key in (pygame.K_RIGHT, pygame.K_d) and drejtimi != (-MADHESIA_BLLOKUT, 0):
                    drejtimi = (MADHESIA_BLLOKUT, 0)

        koka_re = (gjarperi[0][0] + drejtimi[0],
                   gjarperi[0][1] + drejtimi[1])

        if (koka_re[0] < 0 or koka_re[0] >= GJERESIA or
                koka_re[1] < 0 or koka_re[1] >= LARTESIA or
                koka_re in gjarperi):

            ruaj_pike(emri, score)  # ← ruaj piket para se te dale
            ekran_fund(ekrani, score, emri)

            duke_pritur = True
            while duke_pritur:
                for ngjarje in pygame.event.get():
                    if ngjarje.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if ngjarje.type == pygame.KEYDOWN:
                        if ngjarje.key == pygame.K_r:
                            loja_kryesore(emri); return
                        if ngjarje.key == pygame.K_q:
                            pygame.quit(); sys.exit()
            return

        gjarperi.insert(0, koka_re)
        if koka_re in mollat:
            score += 10
            mollat.remove(koka_re)
            mollat = gjenero_mollat(gjarperi, mollat)
        else:
            gjarperi.pop()

        ekrani.fill(HIRI)
        for x in range(0, GJERESIA, MADHESIA_BLLOKUT):
            pygame.draw.line(ekrani, (50, 50, 50), (x, 0), (x, LARTESIA))
        for y in range(0, LARTESIA, MADHESIA_BLLOKUT):
            pygame.draw.line(ekrani, (50, 50, 50), (0, y), (GJERESIA, y))
        vizato_gjarper(ekrani, gjarperi)
        vizato_mollat(ekrani, mollat)
        shfaq_score(ekrani, score, emri)
        pygame.display.flip()
        orari.tick(FPS)


if __name__ == "__main__":
    emri = merr_emrin()
    loja_kryesore(emri)
    pygame.quit()