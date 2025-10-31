import cv2
import pytesseract
from PIL import Image
import numpy as np
import pyautogui
import time
import os
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def take_screenshot(region=None):
    """Pravi screenshot celog ekrana ili određenog regiona u boji"""
    if region:
        left, top, w, h = region
        img = pyautogui.screenshot(region=(left, top, w, h))
    else:
        img = pyautogui.screenshot()
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # BGR za OpenCV


def check_button(template_path="Kod/dugme.png", threshold=0.7):
    """
    Traži dugme na ekranu u boji i snima region gde je pronađeno.
    
    :param template_path: putanja do slike dugmeta
    :param threshold: prag podudaranja (0-1)
    :return: koordinate centra dugmeta ako je pronađeno, inače None
    """
    # Screenshot celog ekrana u boji
    screenshot = take_screenshot()
    
    # Učitavanje template slike dugmeta u boji
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"[ERROR] Template {template_path} nije pronađen")
        return None
    
    w, h = template.shape[1], template.shape[0]  # širina i visina

    # Template matching u boji
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center = (top_left[0] + w // 2, top_left[1] + h // 2)

        # Crop i snimi deo ekrana gde je dugme
        cropped = screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        save_path = "pronaseno_dugme.png"
        cv2.imwrite(save_path, cropped)
        print(f"[BUTTON] Dugme pronađeno! Snimljeno kao {save_path} na koordinatama {center}. MaxVal: {max_val}")

        solve_captcha()
        return center
    else:
        print(f"[BUTTON] Dugme nije pronađeno. MaxVal: {max_val}")
        return None


def solve_captcha():
    # 1️⃣ Screenshot samo regiona gde se nalazi captcha
    region = (825, 427, 1105 - 825, 501 - 427)  # (left, top, width, height)
    captcha_region = take_screenshot(region=region)
    cv2.imwrite("captcha_region.png", captcha_region)  # čisto radi provere

    # 2️⃣ OCR prepoznavanje samo unutar tog regiona
    captcha_text = pytesseract.image_to_string(captcha_region)
    captcha_text = captcha_text.strip()
    print(f"[CAPTCHA] Prepoznat tekst: {captcha_text}")

    # 3️⃣ Klik na F3
    pyautogui.press('f3')
    time.sleep(0.2)

    # 4️⃣ Traži input polje (Kod/input.png)
    screenshot = take_screenshot()
    input_coords = None
    input_template_path = "Kod/input.png"
    template = cv2.imread(input_template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"[ERROR] Template {input_template_path} nije pronađen")
        return

    w, h = template.shape[1], template.shape[0]
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= 0.3:
        top_left = max_loc
        bottom_right = (top_left[0]+w, top_left[1]+h)
        input_coords = (top_left[0]+w//2, top_left[1]+h//2)
        cropped = screenshot[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        cv2.imwrite("pronaseno_input.png", cropped)
        print(f"[INPUT] Input pronađen i snimljen. Koordinate: {input_coords}")

        # Klik na input
        pyautogui.click(input_coords)
        time.sleep(0.2)

        # 5️⃣ Unos captche
        pyautogui.typewrite(captcha_text, interval=0.05)
        time.sleep(0.2)
    else:
        print(f"[INPUT] Input polje nije pronađeno. MaxVal: {max_val}")
        return

    time.sleep(0.4)
    # 6️⃣ Klik direktno na već poznato dugme (ponovo pronađi ali BEZ solve_captcha)
    template_path = "Kod/dugme.png"
    screenshot = take_screenshot()
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is not None:
        w, h = template.shape[1], template.shape[0]
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.5:
            top_left = max_loc
            center = (top_left[0] + w//2, top_left[1] + h//2)
            pyautogui.click(center)
            print("[BUTTON] Dugme kliknuto.")
        else:
            print("[BUTTON] Dugme nije pronađeno pri završnom kliku.")
    else:
        print(f"[ERROR] Template {template_path} nije pronađen za završni klik.")

    # 3️⃣ Klik na F3
    time.sleep(0.2)
    pyautogui.press('f3')
    time.sleep(0.2)




