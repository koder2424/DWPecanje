import cv2
import pyautogui
import numpy as np
import time
import os

password_file = "reconect/password.txt"
if os.path.exists(password_file):
    with open(password_file, "r", encoding="utf-8") as f:
        sifra = f.read().strip()  # čita sadržaj i uklanja razmake i nove redove
else:
    print(f"[UPOZORENJE] Fajl {password_file} nije pronađen, koristi se podrazumevana šifra.")


def reconect():
    time.sleep(5)
    pyautogui.press('f1')
    time.sleep(5)
    pyautogui.click(555, 225)
    time.sleep(2)

    template_path = "reconect/logo.png"
    if not os.path.exists(template_path):
        print(f"[GREŠKA] Nema slike: {template_path}")
        return

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    t_h, t_w, _ = template.shape

    print("[RECONNECT] Tražim logo...")

    while True:
        # Screenshot ekrana
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Poređenje slike u boji
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val >= 0.7:  # prag za prepoznavanje
            print(f"[RECONNECT] Logo pronađen (score={max_val:.2f}) -> klik na (1066, 576)")
            pyautogui.click(1066, 576)
            time.sleep(1)
            pyautogui.typewrite(sifra, interval=0.1)
            time.sleep(0.5)
            pyautogui.press('enter')
            print("[RECONNECT] Šifra uneta i Enter pritisnut.")
            break
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Logo još nije pronađen (score={max_val:.2f})...")
            time.sleep(2)


    time.sleep(3)
    play_path = "reconect/Igraj.png"
    if not os.path.exists(play_path):
        print(f"[GREŠKA] Nema slike: {play_path}")
        return

    play_btn = cv2.imread(play_path, cv2.IMREAD_COLOR)
    print("[RECONNECT] Tražim dugme 'Igraj'...")

    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(frame, play_btn, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val >= 0.8:
            print(f"[RECONNECT] Dugme 'Igraj' pronađeno (score={max_val:.2f}) -> klik na (1605, 277)")
            pyautogui.click(1605, 277)
            break
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Dugme 'Igraj' još nije pronađeno (score={max_val:.2f})...")
            time.sleep(2)

    zatvori_btn = cv2.imread("reconect/zatvori.png")  # u boji
    while True:
        screenshot = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(frame, zatvori_btn, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val >= 0.8:
            print(f"[RECONNECT] Dugme 'zatvori' pronađeno (score={max_val:.2f}) -> klik na (957, 793)")
            pyautogui.click(957, 793)
            break
        else:
            print(f"[{time.strftime('%H:%M:%S')}] Dugme 'zatvori' još nije pronađeno (score={max_val:.2f})...")
            time.sleep(2)

    