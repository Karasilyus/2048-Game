import pygame
import random
import os  # Dosya işlemleri için gerekli

# --- BAŞLANGIÇ AYARLARI ---
pygame.init()

# Ekran Boyutları
GENISLIK = 400
YUKSEKLIK = 550  # Üst kısma High Score sığsın diye uzattık
EKRAN = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("2048 - High Score")

# Renkler
ARKAPLAN_RENGI = (187, 173, 160)
BOS_HUCRE_RENGI = (205, 193, 180)
YAZI_RENGI = (119, 110, 101)
SKOR_TABLOSU_RENGI = (143, 122, 102)

HUCRE_RENKLERI = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121),
    16: (245, 149, 99), 32: (246, 124, 95), 64: (246, 94, 59),
    128: (237, 207, 114), 256: (237, 204, 97), 512: (237, 200, 80),
    1024: (237, 197, 63), 2048: (237, 194, 46)
}

# Yazı Tipleri
FONT = pygame.font.SysFont("arial", 40, bold=True)
SKOR_BASLIK_FONT = pygame.font.SysFont("arial", 15, bold=True)
SKOR_FONT = pygame.font.SysFont("arial", 25, bold=True)
GAMEOVER_FONT = pygame.font.SysFont("arial", 35, bold=True)

# Oyun Değişkenleri
fps = 60
timer = pygame.time.Clock()
skor = 0
en_yuksek_skor = 0
oyun_bitti = False

tahta = [[0 for _ in range(4)] for _ in range(4)]


# --- DOSYA İŞLEMLERİ (HIGH SCORE) ---

def en_yuksek_skoru_yukle():
    """Dosyadan en yüksek skoru okur."""
    if os.path.exists("en_yuksek_skor.txt"):
        with open("en_yuksek_skor.txt", "r") as dosya:
            try:
                return int(dosya.read())
            except:
                return 0
    return 0


def en_yuksek_skoru_kaydet(yeni_skor):
    """Eğer rekor kırıldıysa dosyaya kaydeder."""
    global en_yuksek_skor
    if yeni_skor > en_yuksek_skor:
        en_yuksek_skor = yeni_skor
        with open("en_yuksek_skor.txt", "w") as dosya:
            dosya.write(str(en_yuksek_skor))


# Başlangıçta skoru yükle
en_yuksek_skor = en_yuksek_skoru_yukle()


# --- YARDIMCI FONKSİYONLAR ---

def oyunu_sifirla():
    global tahta, skor, oyun_bitti
    tahta = [[0 for _ in range(4)] for _ in range(4)]
    skor = 0
    oyun_bitti = False
    yeni_sayi_ekle(tahta)
    yeni_sayi_ekle(tahta)


def yeni_sayi_ekle(tahta):
    bos_yerler = [(i, j) for i in range(4) for j in range(4) if tahta[i][j] == 0]
    if bos_yerler:
        satir, sutun = random.choice(bos_yerler)
        tahta[satir][sutun] = 2 if random.random() < 0.9 else 4


def hareket_kaldi_mi(tahta):
    for i in range(4):
        for j in range(4):
            if tahta[i][j] == 0: return True
            if j < 3 and tahta[i][j] == tahta[i][j + 1]: return True
            if i < 3 and tahta[i][j] == tahta[i + 1][j]: return True
    return False


# --- ÇİZİM FONKSİYONLARI ---

def skor_kutusu_ciz(baslik, deger, x, y):
    """Skor tabelalarını çizmek için yardımcı fonksiyon"""
    rect = pygame.Rect(x, y, 100, 50)
    pygame.draw.rect(EKRAN, SKOR_TABLOSU_RENGI, rect, border_radius=5)

    baslik_yazi = SKOR_BASLIK_FONT.render(baslik, True, (230, 220, 210))
    deger_yazi = SKOR_FONT.render(str(deger), True, (255, 255, 255))

    EKRAN.blit(baslik_yazi, (rect.centerx - baslik_yazi.get_width() // 2, y + 5))
    EKRAN.blit(deger_yazi, (rect.centerx - deger_yazi.get_width() // 2, y + 22))


def tahtayi_ciz(tahta, skor, high_score):
    EKRAN.fill(ARKAPLAN_RENGI)

    # Başlık
    title = pygame.font.SysFont("arial", 50, bold=True).render("2048", True, (119, 110, 101))
    EKRAN.blit(title, (20, 20))

    # Skor Kutuları
    skor_kutusu_ciz("SKOR", skor, GENISLIK - 220, 25)
    skor_kutusu_ciz("EN İYİ", high_score, GENISLIK - 110, 25)

    for i in range(4):
        for j in range(4):
            deger = tahta[i][j]
            renk = HUCRE_RENKLERI.get(deger, (60, 58, 50)) if deger > 0 else BOS_HUCRE_RENGI

            rect_x = j * 90 + 20
            rect_y = i * 90 + 100
            pygame.draw.rect(EKRAN, renk, (rect_x, rect_y, 80, 80), border_radius=5)

            if deger > 0:
                yazi_renk = YAZI_RENGI if deger < 8 else (255, 255, 255)
                # Yazı boyutu sayı büyüdükçe küçülsün (sığması için)
                font_boyutu = 40 if deger < 100 else (30 if deger < 1000 else 25)
                dinamik_font = pygame.font.SysFont("arial", font_boyutu, bold=True)

                sayi_yazisi = dinamik_font.render(str(deger), True, yazi_renk)
                yazi_rect = sayi_yazisi.get_rect(center=(rect_x + 40, rect_y + 40))
                EKRAN.blit(sayi_yazisi, yazi_rect)


def game_over_ekrani_ciz():
    # Şeffaf bir katman oluşturalım (Surface)
    s = pygame.Surface((GENISLIK, YUKSEKLIK))
    s.set_alpha(150)  # Şeffaflık seviyesi (0-255)
    s.fill((255, 230, 200))  # Hafif sarımsı bir ton
    EKRAN.blit(s, (0, 0))

    msg1 = GAMEOVER_FONT.render("OYUN BİTTİ!", True, YAZI_RENGI)
    msg2 = SKOR_FONT.render("Tekrar oynamak için ENTER", True, YAZI_RENGI)

    EKRAN.blit(msg1, (GENISLIK / 2 - msg1.get_width() / 2, YUKSEKLIK / 2 - 50))
    EKRAN.blit(msg2, (GENISLIK / 2 - msg2.get_width() / 2, YUKSEKLIK / 2 + 10))


# --- HAREKET MANTIĞI ---

def sıkıstır(satir):
    yeni_satir = [i for i in satir if i != 0]
    yeni_satir += [0] * (4 - len(yeni_satir))
    return yeni_satir


def birlestir(satir):
    global skor
    for i in range(3):
        if satir[i] != 0 and satir[i] == satir[i + 1]:
            satir[i] *= 2
            skor += satir[i]
            satir[i + 1] = 0
    return satir


def sola_hareket(tahta):
    yeni_tahta = []
    degisim_oldu = False
    for satir in tahta:
        sıkısmıs = sıkıstır(satir)
        birlestirilmis = birlestir(sıkısmıs)
        son_hali = sıkıstır(birlestirilmis)
        yeni_tahta.append(son_hali)
        if satir != son_hali: degisim_oldu = True
    return yeni_tahta, degisim_oldu


def ters_cevir(tahta): return [satir[::-1] for satir in tahta]


def transpoze(tahta): return [[tahta[j][i] for j in range(4)] for i in range(4)]


def hareket_yonet(yon):
    global tahta, oyun_bitti
    if oyun_bitti: return

    degisim = False
    temp_tahta = tahta

    if yon == 'SOL':
        temp_tahta, degisim = sola_hareket(temp_tahta)
    elif yon == 'SAG':
        temp_tahta = ters_cevir(temp_tahta)
        temp_tahta, degisim = sola_hareket(temp_tahta)
        temp_tahta = ters_cevir(temp_tahta)
    elif yon == 'YUKARI':
        temp_tahta = transpoze(temp_tahta)
        temp_tahta, degisim = sola_hareket(temp_tahta)
        temp_tahta = transpoze(temp_tahta)
    elif yon == 'ASAGI':
        temp_tahta = transpoze(temp_tahta)
        temp_tahta = ters_cevir(temp_tahta)
        temp_tahta, degisim = sola_hareket(temp_tahta)
        temp_tahta = ters_cevir(temp_tahta)
        temp_tahta = transpoze(temp_tahta)

    if degisim:
        tahta = temp_tahta
        yeni_sayi_ekle(tahta)
        # Her hareketten sonra rekoru kontrol et
        en_yuksek_skoru_kaydet(skor)
        if not hareket_kaldi_mi(tahta):
            oyun_bitti = True


# --- OYUN DÖNGÜSÜ ---
oyunu_sifirla()

calisiyor = True
while calisiyor:
    timer.tick(fps)
    # Çizim fonksiyonuna artık hem skoru hem rekoru gönderiyoruz
    tahtayi_ciz(tahta, skor, en_yuksek_skor)

    if oyun_bitti:
        game_over_ekrani_ciz()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            calisiyor = False

        if event.type == pygame.KEYDOWN:
            if oyun_bitti:
                if event.key == pygame.K_RETURN:
                    oyunu_sifirla()
            else:
                if event.key == pygame.K_LEFT:
                    hareket_yonet('SOL')
                elif event.key == pygame.K_RIGHT:
                    hareket_yonet('SAG')
                elif event.key == pygame.K_UP:
                    hareket_yonet('YUKARI')
                elif event.key == pygame.K_DOWN:
                    hareket_yonet('ASAGI')

            if event.key == pygame.K_r:
                oyunu_sifirla()

    pygame.display.flip()

pygame.quit()