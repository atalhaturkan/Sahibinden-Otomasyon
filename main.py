import json
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


YENI_ILAN_LINK_SELECTORU = "#sellSmilarItem"
ILAN_BASLIK_INPUT_SELECTORU = "input[name='addClassifiedTitle']"
ACIKLAMA_INPUT_SELECTORU = "div[name='Açıklama']"
FIYAT_INPUT_SELECTORU = "#addClassifiedPrice"
FOTO_YUKLEME_INPUT_SELECTORU = 'input[type="file"]'
KURALLAR_CHECKBOX_SELECTORU = "#postRulesCheck"
OTO_YAYIN_CHECKBOX_SELECTORU = "#autoPublishAuction"
DEVAM_ET_BUTTON_SELECTORU = "#postAdBtn"

FOTO_GALERI_SECICISI = "img.stdImg, img.thmbImg"


URUN_DROPDOWN_SELECTORU = "select[an-form-object-name='Ürün']"
ARAC_MARKASI_DROPDOWN_SELECTORU = "select[an-form-object-name='Araç Markası']"
ARAC_SERISI_DROPDOWN_SELECTORU = "select[an-form-object-name='Araç Serisi']"
URUN_MARKASI_DROPDOWN_SELECTORU = "select[an-form-object-name='Ürün Markası']"
CIKMA_PARCA_DROPDOWN_SELECTORU = "select[an-form-object-name='Çıkma Yedek Parça']"
DURUMU_DROPDOWN_SELECTORU = "select[name='condition']"
TAKAS_DROPDOWN_SELECTORU = "select[name='exchange']"
# ------------------------------------------------------------------------------------

TEMP_IMAGE_DIR = "temp_images"
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

try:
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    print("✅ Mevcut Chrome oturumuna başarıyla bağlanıldı.")


    print("\n🕵️ İlan bilgileri toplanıyor...")
    json_data_element = wait.until(EC.presence_of_element_located((By.ID, "gaPageViewTrackingJson")))
    json_string = json_data_element.get_attribute('data-json')
    parsed_data = json.loads(json_string)
    ilan_bilgileri = {item['name']: item['value'].strip() for item in parsed_data.get('customVars', [])}

    baslik_elementi = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.classifiedDetailTitle > h1")))
    ilan_bilgileri['ilan_basligi'] = baslik_elementi.text

    aciklama_elementi = wait.until(EC.presence_of_element_located((By.ID, "classifiedDescription")))
    ilan_bilgileri['ilan_aciklamasi_html'] = aciklama_elementi.get_attribute('innerHTML')
    print("✅ İlan bilgileri başarıyla toplandı.")


    print("\n🖼️ Yüksek kaliteli fotoğraflar indiriliyor...")
    image_elements = driver.find_elements(By.CSS_SELECTOR, FOTO_GALERI_SECICISI)
    downloaded_photo_paths = []
    unique_urls = set()
    for img_element in image_elements:
        image_url = img_element.get_attribute('src')
        if image_url and image_url not in unique_urls:
            unique_urls.add(image_url)


            high_quality_url = image_url.replace("thmb_", "x16_").replace("x5_", "x16_")
            # ---

            try:
                response = requests.get(high_quality_url)
                if 'image' in response.headers.get('Content-Type', ''):
                    file_name = high_quality_url.split('/')[-1]
                    file_path = os.path.join(TEMP_IMAGE_DIR, file_name)
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    downloaded_photo_paths.append(os.path.abspath(file_path))
            except Exception as e:
                print(f"⚠️ Fotoğraf indirilirken hata: {e}")
    print(f"✅ {len(downloaded_photo_paths)} adet yüksek kaliteli fotoğraf 'temp_images' klasörüne indirildi.")


    print("\n🚀 Kısayol kullanılarak yeni ilan verme sürecine başlanıyor...")
    original_window = driver.current_window_handle
    yeni_ilan_linki = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, YENI_ILAN_LINK_SELECTORU)))
    ActionChains(driver).key_down(Keys.CONTROL).click(yeni_ilan_linki).key_up(Keys.CONTROL).perform()
    wait.until(EC.number_of_windows_to_be(2))
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
    print("✅ Yeni sekmeye başarıyla geçildi. Form dolduruluyor...")



    def set_value_with_js(selector, value):
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.execute_script("arguments[0].value = arguments[1];", element, value)


    def set_innerhtml_with_js(selector, html_value):
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.execute_script("arguments[0].innerHTML = arguments[1];", element, html_value)


    set_value_with_js(ILAN_BASLIK_INPUT_SELECTORU, ilan_bilgileri.get("ilan_basligi", ""))
    set_innerhtml_with_js(ACIKLAMA_INPUT_SELECTORU, ilan_bilgileri.get('ilan_aciklamasi_html', ''))
    fiyat = ilan_bilgileri.get('ilan_fiyat', '0').replace('TL', '').replace('.', '').strip()
    set_value_with_js(FIYAT_INPUT_SELECTORU, fiyat)
    print("✅ Başlık, açıklama ve fiyat dolduruldu.")



    def select_dropdown(selector, text_value):
        try:
            if text_value:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                Select(element).select_by_visible_text(text_value)
                print(f"✅ Menüden '{text_value}' seçildi.")
                return True
        except:
            return False


    select_dropdown(URUN_DROPDOWN_SELECTORU, ilan_bilgileri.get("Ürün"))
    if select_dropdown(ARAC_MARKASI_DROPDOWN_SELECTORU, ilan_bilgileri.get("Araç Markası")):
        time.sleep(2)
        select_dropdown(ARAC_SERISI_DROPDOWN_SELECTORU, ilan_bilgileri.get("Araç Serisi"))
    select_dropdown(URUN_MARKASI_DROPDOWN_SELECTORU, ilan_bilgileri.get("Ürün Markası"))
    select_dropdown(CIKMA_PARCA_DROPDOWN_SELECTORU, ilan_bilgileri.get("Çıkma Yedek Parça"))
    select_dropdown(DURUMU_DROPDOWN_SELECTORU, ilan_bilgileri.get("[classified.attribute.productCondition]"))
    select_dropdown(TAKAS_DROPDOWN_SELECTORU, ilan_bilgileri.get("Takas"))

    # Fotoğraf Yükleme
    if downloaded_photo_paths:
        print("⬆️ Fotoğraflar yükleniyor...")
        photo_upload_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, FOTO_YUKLEME_INPUT_SELECTORU)))
        photo_paths_string = "\n".join(downloaded_photo_paths)
        photo_upload_input.send_keys(photo_paths_string)
        print("✅ Fotoğraf yükleme komutu gönderildi.")



    def scroll_and_click(selector):
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
            time.sleep(1)
            wait.until(EC.element_to_be_clickable(element)).click()
            return True
        except:
            return False


    if scroll_and_click(KURALLAR_CHECKBOX_SELECTORU): print("✅ Kurallar kabul edildi.")
    if scroll_and_click(OTO_YAYIN_CHECKBOX_SELECTORU): print("✅ Otomatik yayınlama işaretlendi.")

    print("\n🎉 Form doldurma işlemi tamamlandı! Son kontrol için sayfa size bırakıldı.")

except Exception as e:
    print(f"\n❌ Bir hata oluştu: {e}")
    import traceback

    traceback.print_exc()
finally:
    print("\nScript görevini tamamladı. Sonucu görmek için tarayıcıyı kontrol edebilirsiniz.")