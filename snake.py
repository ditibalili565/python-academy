import pygame
import random
import sys

# --- Konfigurimi ---
GJERESIA = 600
LARTESIA = 600
MADHESIA_BLLOKUT = 20
FPS = 7
MOLLA_MAX = 5

BARDHE  = (255, 255, 255)
ZI      = (0,   0,   0  )
GJELBER = (0,   200, 0  )
KUQE    = (200, 0,   0  )
HIRI    = (40,  40,  40 )
KALTER  = (56,  189, 248)

# --- Inicializimi ---
pygame.init()
ekrani = pygame.display.set_mode((GJERESIA, LARTESIA))
pygame.display.set_caption("Snake - Python Academy")
orari = pygame.time.Clock()
fonti = pygame.font.SysFont("Courier New", 28, bold=True)
fonti_i_madh = pygame.font.SysFont("Courier New", 48, bold=True)


def gjenero_nje_ushqim(gjarperi, mollat_ekzistuese):
    """Gjeneron 1 molle ne pozicion te lire."""
    while True:
        x = random.randrange(0, GJERESIA, MADHESIA_BLLOKUT)
        y = random.randrange(0, LARTESIA, MADHESIA_BLLOKUT)
        if (x, y) not in gjarperi and (x, y) not in mollat_ekzistuese:
            return (x, y)


def gjenero_mollat(gjarperi, mollat_ekzistuese):
    """Mbush listen e mollave deri ne MOLLA_MAX."""
    mollat = list(mollat_ekzistuese)
    while len(mollat) < MOLLA_MAX:
        mollat.append(gjenero_nje_ushqim(gjarperi, mollat))
    return mollat


def vizato_gjarper(ekrani, gjarperi):
    for i, (x, y) in enumerate(gjarperi):
        ngjyra = KALTER if i == 0 else GJELBER
        pygame.draw.rect(ekrani, ngjyra,
                         (x, y, MADHESIA_BLLOKUT - 2, MADHESIA_BLLOKUT - 2),
                         border_radius=4)


def vizato_mollat(ekrani, mollat):
    for (x, y) in mollat:
        pygame.draw.rect(ekrani, KUQE,
                         (x, y, MADHESIA_BLLOKUT - 2, MADHESIA_BLLOKUT - 2),
                         border_radius=6)


def shfaq_score(ekrani, score):
    teksti = fonti.render(f"Pike: {score}", True, BARDHE)
    ekrani.blit(teksti, (10, 10))


def ekran_fund(ekrani, score):
    ekrani.fill(ZI)
    msg1 = fonti_i_madh.render("LOJA MBAROI!", True, KUQE)
    msg2 = fonti.render(f"Pike: {score}", True, BARDHE)
    msg3 = fonti.render("Shtyp R per te rifilluar", True, HIRI)
    msg4 = fonti.render("Shtyp Q per te dale", True, HIRI)
    ekrani.blit(msg1, (GJERESIA//2 - msg1.get_width()//2, 180))
    ekrani.blit(msg2, (GJERESIA//2 - msg2.get_width()//2, 260))
    ekrani.blit(msg3, (GJERESIA//2 - msg3.get_width()//2, 320))
    ekrani.blit(msg4, (GJERESIA//2 - msg4.get_width()//2, 360))
    pygame.display.flip()


def loja_kryesore():
    gjarperi = [(300, 300), (280, 300), (260, 300)]
    drejtimi = (MADHESIA_BLLOKUT, 0)
    mollat   = gjenero_mollat(gjarperi, [])   # 5 molla fillestare
    score    = 0
    duke_luajtur = True

    while duke_luajtur:

        # --- Ngjarjet ---
        for ngjarje in pygame.event.get():
            if ngjarje.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ngjarje.type == pygame.KEYDOWN:
                if ngjarje.key == pygame.K_UP and drejtimi != (0, MADHESIA_BLLOKUT):
                    drejtimi = (0, -MADHESIA_BLLOKUT)
                elif ngjarje.key == pygame.K_DOWN and drejtimi != (0, -MADHESIA_BLLOKUT):
                    drejtimi = (0, MADHESIA_BLLOKUT)
                elif ngjarje.key == pygame.K_LEFT and drejtimi != (MADHESIA_BLLOKUT, 0):
                    drejtimi = (-MADHESIA_BLLOKUT, 0)
                elif ngjarje.key == pygame.K_RIGHT and drejtimi != (-MADHESIA_BLLOKUT, 0):
                    drejtimi = (MADHESIA_BLLOKUT, 0)

        # --- Levizja ---
        koka_re = (gjarperi[0][0] + drejtimi[0],
                   gjarperi[0][1] + drejtimi[1])

        # --- Kontrolli i goditjes ---
        if (koka_re[0] < 0 or koka_re[0] >= GJERESIA or
                koka_re[1] < 0 or koka_re[1] >= LARTESIA or
                koka_re in gjarperi):
            ekran_fund(ekrani, score)
            duke_pritur = True
            while duke_pritur:
                for ngjarje in pygame.event.get():
                    if ngjarje.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if ngjarje.type == pygame.KEYDOWN:
                        if ngjarje.key == pygame.K_r:
                            loja_kryesore()
                            return
                        if ngjarje.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            return

        gjarperi.insert(0, koka_re)

        # --- Ha mollen? ---
        if koka_re in mollat:
            score += 10
            mollat.remove(koka_re)                     # hiq mollen e ngrene
            mollat = gjenero_mollat(gjarperi, mollat)  # gjenero 1 te re menjehere
        else:
            gjarperi.pop()

        # --- Vizatimi ---
        ekrani.fill(HIRI)

        for x in range(0, GJERESIA, MADHESIA_BLLOKUT):
            pygame.draw.line(ekrani, (50, 50, 50), (x, 0), (x, LARTESIA))
        for y in range(0, LARTESIA, MADHESIA_BLLOKUT):
            pygame.draw.line(ekrani, (50, 50, 50), (0, y), (GJERESIA, y))

        vizato_gjarper(ekrani, gjarperi)
        vizato_mollat(ekrani, mollat)
        shfaq_score(ekrani, score)

        pygame.display.flip()
        orari.tick(FPS)


if __name__ == "__main__":
    loja_kryesore()
    pygame.quit()
