import cv2
import numpy as np
import pyautogui
import time
import glob
import os
from threading import Thread
from queue import Queue
from ocr_reader import check_button
from reconect import reconect


# ------- Podesi ovde -------
TEMPLATE_FOLDER = "ribe"
THRESHOLD = 0.88
SCREEN_REGION = None
SCAN_INTERVAL = 0.35
MULTISCALE = True
SCALE_RANGE = (0.8, 1.2)
SCALE_STEPS = 6
COOLDOWN = 0.9
pyautogui.FAILSAFE = False
# ----------------------------

# učitaj template fajlove
template_paths = glob.glob(os.path.join(TEMPLATE_FOLDER, "*.png"))
templates = []
for p in template_paths:
    img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        templates.append((os.path.basename(p), img))

if not templates:
    raise SystemExit("Nema template fajlova u folderu: " + TEMPLATE_FOLDER)

print(f"Učitao {len(templates)} template-a.")
time.sleep(3)

def take_screenshot(region=None):
    if region:
        left, top, w, h = region
        img = pyautogui.screenshot(region=(left, top, w, h))
    else:
        img = pyautogui.screenshot()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

# funkcija za thread: traži template i stavlja rezultat u queue
def thread_search(name, templ, frame, queue):
    found = []
    if MULTISCALE:
        for s in np.linspace(SCALE_RANGE[0], SCALE_RANGE[1], SCALE_STEPS):
            new_w = int(templ.shape[1] * s)
            new_h = int(templ.shape[0] * s)
            if new_w < 8 or new_h < 8:
                continue
            templ_resized = cv2.resize(templ, (new_w, new_h), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(frame, templ_resized, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= THRESHOLD)
            for pt in zip(*loc[::-1]):
                x, y = pt
                found.append((name, x, y, new_w, new_h, res[y, x]))
    else:
        res = cv2.matchTemplate(frame, templ, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= THRESHOLD)
        for pt in zip(*loc[::-1]):
            x, y = pt
            found.append((name, x, y, templ.shape[1], templ.shape[0], res[y, x]))

    if found:
        # uzimamo samo najbolje podudaranje po score
        best = max(found, key=lambda h: h[5])
        queue.put(best)


def odbijam():
    """Traži odbijam.png na ekranu i klikne na njega ako se pronađe."""
    template_path = "odbijam.png"
    templ = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if templ is None:
        print(f"Ne mogu da učitam {template_path}")
        return

    frame = take_screenshot(SCREEN_REGION)
    res = cv2.matchTemplate(frame, templ, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= THRESHOLD)

    if len(loc[0]) > 0:
        # uzimamo prvo podudaranje
        y, x = loc[0][0], loc[1][0]
        click_x = x + templ.shape[1] // 2
        click_y = y + templ.shape[0] // 2

        if SCREEN_REGION:
            left, top, _, _ = SCREEN_REGION
            click_x += left
            click_y += top

        pyautogui.click(click_x, click_y)
        print(f"Klik na odbijam.png -> {click_x},{click_y}")
    else:
        # ništa nije pronađeno
        print("odbijam.png nije pronađen")


#Traži hranu i vodu i koristi ih pritiskom na 'use'.
def nahrani_se():
    print("Proces hranjenja")

    folder = "Hrana"
    items = ["hrana.png", "voda.png", "use.png"]

    # učitaj slike
    templates = {}
    for item in items:
        path = os.path.join(folder, item)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Ne mogu da učitam {path}")
        else:
            templates[item] = img

    if not templates:
        print("Nema učitanih template-a za hranjenje.")
        return

    # ---- Prvo hrana ----
    print("Otvaram inventory za hranu")
    pyautogui.press('i')
    time.sleep(5)

    # klik na hrana.png
    food_img = templates.get("hrana.png")
    use_img = templates.get("use.png")
    if food_img is not None:
        frame = take_screenshot(SCREEN_REGION)
        res = cv2.matchTemplate(frame, food_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= THRESHOLD)
        if len(loc[0]) > 0:
            y, x = loc[0][0], loc[1][0]
            click_x = x + food_img.shape[1] // 2
            click_y = y + food_img.shape[0] // 2
            if SCREEN_REGION:
                left, top, _, _ = SCREEN_REGION
                click_x += left
                click_y += top
            pyautogui.click(click_x, click_y)
            print("Klik na hranu")
            time.sleep(1)

            # klik na use.png
            if use_img is not None:
                frame_use = take_screenshot(SCREEN_REGION)
                res_use = cv2.matchTemplate(frame_use, use_img, cv2.TM_CCOEFF_NORMED)
                loc_use = np.where(res_use >= THRESHOLD)
                if len(loc_use[0]) > 0:
                    uy, ux = loc_use[0][0], loc_use[1][0]
                    click_x_use = ux + use_img.shape[1] // 2
                    click_y_use = uy + use_img.shape[0] // 2
                    if SCREEN_REGION:
                        click_x_use += left
                        click_y_use += top
                    pyautogui.click(click_x_use, click_y_use)
                    print("Pritisnut use za hranu")
                    time.sleep(17)
        else:
            print("Nije pronađena hrana")

    # ---- Sada voda ----
    print("Otvaram inventory za vodu")
    pyautogui.press('i')
    time.sleep(5)

    water_img = templates.get("voda.png")
    if water_img is not None:
        frame = take_screenshot(SCREEN_REGION)
        res = cv2.matchTemplate(frame, water_img, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= THRESHOLD)
        if len(loc[0]) > 0:
            y, x = loc[0][0], loc[1][0]
            click_x = x + water_img.shape[1] // 2
            click_y = y + water_img.shape[0] // 2
            if SCREEN_REGION:
                left, top, _, _ = SCREEN_REGION
                click_x += left
                click_y += top
            pyautogui.click(click_x, click_y)
            print("Klik na vodu")
            time.sleep(1)

            # klik na use.png
            if use_img is not None:
                frame_use = take_screenshot(SCREEN_REGION)
                res_use = cv2.matchTemplate(frame_use, use_img, cv2.TM_CCOEFF_NORMED)
                loc_use = np.where(res_use >= THRESHOLD)
                if len(loc_use[0]) > 0:
                    uy, ux = loc_use[0][0], loc_use[1][0]
                    click_x_use = ux + use_img.shape[1] // 2
                    click_y_use = uy + use_img.shape[0] // 2
                    if SCREEN_REGION:
                        click_x_use += left
                        click_y_use += top
                    pyautogui.click(click_x_use, click_y_use)
                    print("Pritisnut use za vodu")
                    time.sleep(17)
        else:
            print("Nije pronađena voda")


last_click_time = 0
start_time = time.time()  # timer za hranjenje
TIMER_MINUTES = 30       # hrana
ITERATION_TIMEOUT = 40   # maksimalno trajanje iteracije u sekundama
zadnji_lov = time.time()
reconect_timer = 5 * 60

def pecaj():
    """Traži ribu i vraća najbolje podudaranje ili None"""
    frame = take_screenshot(SCREEN_REGION)
    queue = Queue()
    threads = []

    for name, templ in templates:
        t = Thread(target=thread_search, args=(name, templ, frame, queue))
        t.start()
        threads.append(t)

    # čekaj sve threadove
    for t in threads:
        t.join()

    if not queue.empty():
        results = []
        while not queue.empty():
            results.append(queue.get())
        best = max(results, key=lambda h: h[5])
        name, x, y, w, h, score = best

        if SCREEN_REGION:
            left, top, _, _ = SCREEN_REGION
            click_x = left + x + w // 2
            click_y = top + y + h // 2
        else:
            click_x = x + w // 2
            click_y = y + h // 2

        return name, score, click_x, click_y

    return None, None, None, None

# ------------------ Glavna petlja ------------------
while True:
    iteration_start = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Nova iteracija počinje...")
    
    odbijam()
    check_button()
    pyautogui.press('e')
    print("E1 je kliknuto")
    time.sleep(1)

    # Provera da li je vreme za hranjenje
    elapsed_seconds = int(time.time() - start_time)
    need_food = elapsed_seconds >= TIMER_MINUTES * 60

    if time.time() - zadnji_lov > reconect_timer:  # NOVO: reconect ako 5 minuta nije ulovljena riba
        print(f"[{time.strftime('%H:%M:%S')}] Nije ulovljena nijedna riba 5 minuta, pokrećem reconect()...")
        reconect()
        zadnji_lov = time.time()  # NOVO: reset posle reconecta

    # Ako je vreme za hranu, pokušaj da prvo nadješ ribu
    if need_food:
        print(f"[{time.strftime('%H:%M:%S')}] Vreme za hranu! Pokušavam da nadjem ribu pre hranjenja...")
        name, score, click_x, click_y = None, None, None, None
        start_pecaj = time.time()
        while time.time() - start_pecaj < ITERATION_TIMEOUT:
            n, s, cx, cy = pecaj()
            if n is not None:
                name, score, click_x, click_y = n, s, cx, cy
                zadnji_lov = time.time()
                break
            time.sleep(0.1)

        # Ako riba postoji, klikni
        if name is not None:
            print(f"[{time.strftime('%H:%M:%S')}] Pronađena riba pre hranjenja: {name} (score {score:.2f})")
            pyautogui.click(click_x, click_y)
            time.sleep(1)

        # Sada jedi
        print(f"[{time.strftime('%H:%M:%S')}] Jedem...")
        nahrani_se()
        start_time = time.time()  # reset timer za hranu
        last_click_time = time.time()  # reset cooldown posle hranjenja

    else:
        # Normalno pecanje
        name, score, click_x, click_y = None, None, None, None
        start_pecaj = time.time()
        while time.time() - start_pecaj < ITERATION_TIMEOUT:
            n, s, cx, cy = pecaj()
            if n is not None:
                name, score, click_x, click_y = n, s, cx, cy
                zadnji_lov = time.time()
                break
            time.sleep(0.1)

        # Ako riba postoji i cooldown je prošao
        if name is not None and (time.time() - last_click_time > COOLDOWN):
            print(f"[{time.strftime('%H:%M:%S')}] Pronađena riba: {name} (score {score:.2f}) -> klik {click_x},{click_y}")
            pyautogui.click(click_x, click_y)
            time.sleep(1)
            check_button()
            time.sleep(1)
            pyautogui.press('e')
            print("E2 je kliknuto")
            last_click_time = time.time()

    # Pauza između iteracija
    elapsed = time.time() - iteration_start
    print(f"[INFO] Iteracija završena za {elapsed:.1f}s\n")
    time.sleep(SCAN_INTERVAL)
