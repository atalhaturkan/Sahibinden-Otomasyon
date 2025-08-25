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
from selenium.common.exceptions import TimeoutException


def load_selectors():
    """selectors.json dosyasını okur ve içeriğini bir sözlük olarak döndürür."""
    with open('selectors.json', 'r', encoding='utf-8') as f:
        return json.load(f)


TEMP_IMAGE_DIR = "temp_images"
if not os.path.exists(TEMP_IMAGE_DIR):
    os.makedirs(TEMP_IMAGE_DIR)

try:
    selectors = load_selectors()
    print("✅ Selector'lar 'selectors.json' dosyasından başarıyla yüklendi.")

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    print("✅ Mevcut Chrome oturumuna başarıyla bağlanıldı.")

    # BÖLÜM 1: VERİ TOPLAMA
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

    # FOTOĞRAF İNDİRME (GÜNCELLENMİŞ TIKLAMA YÖNTEMİYLE)
    print("\n🖼️ Yüksek kaliteli fotoğraflar tek tek bulunup indiriliyor...")
    thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, selectors['foto_galeri_thumbnail'])
    unique_urls = set()
    downloaded_photo_paths = []
    print(f"🔎 Bulunan küçük resim sayısı: {len(thumbnail_elements)}")
    for i, thumb in enumerate(thumbnail_elements):
        try:
            # Standart click yerine JavaScript click kullanarak engelleri aşıyoruz.
            driver.execute_script("arguments[0].click();", thumb)

            time.sleep(0.5)
            main_image_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['ana_foto_goruntuleyici'])))
            high_quality_url = main_image_element.get_attribute('src')

            if high_quality_url and high_quality_url not in unique_urls:
                unique_urls.add(high_quality_url)
                response = requests.get(high_quality_url)
                if 'image' in response.headers.get('Content-Type', ''):
                    file_name = high_quality_url.split('/')[-1]
                    file_path = os.path.join(TEMP_IMAGE_DIR, file_name)
                    with open(file_path, 'wb') as file: file.write(response.content)
                    downloaded_photo_paths.append(os.path.abspath(file_path))
        except Exception as e:
            print(f"⚠️ {i + 1}. küçük resim işlenirken bir hata oluştu: {e}")
    print(f"✅ {len(downloaded_photo_paths)} adet yüksek kaliteli fotoğraf indirildi.")

    # FOTOĞRAF KONTROLÜ
    if len(downloaded_photo_paths) < len(thumbnail_elements):
        error_message = (f"❌ HATA: Fotoğraf indirme işlemi tamamlanamadı! "
                         f"Bulunan {len(thumbnail_elements)} fotoğraftan sadece {len(downloaded_photo_paths)} tanesi indirilebildi. "
                         f"Script durduruluyor.")
        raise Exception(error_message)
    else:
        print("✅ Tüm fotoğrafların başarıyla indirildiği doğrulandı.")

    # BÖLÜM 2: YENİ İLAN OLUŞTURMA VE DOLDURMA
    print("\n🚀 Kısayol kullanılarak yeni ilan verme sürecine başlanıyor...")
    original_window = driver.current_window_handle
    yeni_ilan_linki = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selectors['yeni_ilan_link'])))
    ActionChains(driver).key_down(Keys.CONTROL).click(yeni_ilan_linki).key_up(Keys.CONTROL).perform()
    wait.until(EC.number_of_windows_to_be(2))
    for window_handle in driver.window_handles:
        if window_handle != original_window: driver.switch_to.window(window_handle)
    print("✅ Yeni sekmeye başarıyla geçildi. Form dolduruluyor...")


    # Form Doldurma Fonksiyonları
    def fill_input_and_trigger_events(selector, value):
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.execute_script("arguments[0].value = arguments[1];", element, value)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)


    def fill_richtext_and_trigger_events(selector, html_value):
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.execute_script("arguments[0].innerHTML = arguments[1];", element, html_value)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)


    fill_input_and_trigger_events(selectors['ilan_baslik_input'], ilan_bilgileri.get("ilan_basligi", ""))
    fill_richtext_and_trigger_events(selectors['aciklama_input'], ilan_bilgileri.get('ilan_aciklamasi_html', ''))
    fiyat = ilan_bilgileri.get('ilan_fiyat', '0').replace('TL', '').replace('.', '').strip()
    fill_input_and_trigger_events(selectors['fiyat_input'], fiyat)
    print("✅ Başlık, açıklama ve fiyat (olaylar tetiklenerek) dolduruldu.")


    # Açılır Menüleri Doldurma
    def select_dropdown(selector, text_value):
        try:
            if text_value:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                Select(element).select_by_visible_text(text_value)
                print(f"✅ Menüden '{text_value}' seçildi.")
                return True
        except Exception:
            print(f"⚠️ Menüden '{text_value}' seçilemedi. Muhtemelen listede böyle bir seçenek yok.")
            return False


    select_dropdown(selectors['urun_dropdown'], ilan_bilgileri.get("Ürün"))
    if select_dropdown(selectors['arac_markasi_dropdown'], ilan_bilgileri.get("Araç Markası")):
        try:
            seri_dropdown_selector = selectors['arac_serisi_dropdown']
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"{seri_dropdown_selector} option:nth-child(2)")))
            print("✅ Araç Serisi menüsü başarıyla doldu.")
            select_dropdown(seri_dropdown_selector, ilan_bilgileri.get("Araç Serisi"))
        except TimeoutException:
            print("⚠️ Araç Serisi menüsü zamanında dolmadı veya hiç seçenek içermiyor. Bu adım atlanıyor.")
    select_dropdown(selectors['urun_markasi_dropdown'], ilan_bilgileri.get("Ürün Markası"))
    select_dropdown(selectors['cikma_parca_dropdown'], ilan_bilgileri.get("Çıkma Yedek Parça"))
    select_dropdown(selectors['durumu_dropdown'], ilan_bilgileri.get("[classified.attribute.productCondition]"))
    select_dropdown(selectors['takas_dropdown'], ilan_bilgileri.get("Takas"))

    # Fotoğraf Yükleme
    if downloaded_photo_paths:
        print("⬆️ Fotoğraflar yükleniyor...")
        photo_upload_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['foto_yukleme_input'])))
        photo_paths_string = "\n".join(downloaded_photo_paths)
        photo_upload_input.send_keys(photo_paths_string)
        print("✅ Fotoğraf yükleme komutu gönderildi.")


    # Onay Kutuları ve İlanı Tamamlama
    def scroll_and_click(selector, label):
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
            time.sleep(1)
            wait.until(EC.element_to_be_clickable(element)).click()
            print(f"✅ '{label}' kutusu/butonu tıklandı.")
            return True
        except TimeoutException:
            print(f"⚠️ HATA: '{label}' ('{selector}') bulunamadı veya tıklanabilir değil.")
            return False
        except Exception as e:
            print(f"⚠️ HATA: '{label}' tıklanırken hata: {e}")
            return False


    if scroll_and_click(selectors['kurallar_checkbox'], "İlan Verme Kuralları"): pass
    if scroll_and_click(selectors['oto_yayin_checkbox'], "Otomatik Yeniden Yayınlama"): pass

    print("\n🎉 Form doldurma işlemi tamamlandı! Sonraki adımlara geçiliyor...")

    if scroll_and_click(selectors['devam_et_1'], "Devam Et (Sayfa 1)"):
        print("✅ Önizleme sayfası yükleniyor...")
        time.sleep(2)

        if scroll_and_click(selectors['devam_et_2'], "Devam Et (Önizleme)"):
            print("✅ Doping sayfası yükleniyor...")
            time.sleep(2)

            if scroll_and_click(selectors['devam_et_3'], "Devam Et (Doping)"):
                print("✅ İlan yayınlandı! Tebrikler sayfası için 10 saniye bekleniyor...")
                time.sleep(10)
            else:
                print("❌ İlan tamamlama başarısız (Doping sayfası). Lütfen tarayıcıyı manuel kontrol edin.")
        else:
            print("❌ İlan tamamlama başarısız (Önizleme sayfası). Lütfen tarayıcıyı manuel kontrol edin.")
    else:
        print("❌ İlk 'Devam Et' butonuna tıklanamadı. İşlem durdu.")

except FileNotFoundError:
    print("❌ HATA: 'selectors.json' dosyası bulunamadı. Lütfen 'main.py' ile aynı dizinde olduğundan emin olun.")
except Exception as e:
    print(f"\n❌ Bir hata oluştu: {e}")
    import traceback

    traceback.print_exc()
finally:
    print("\nScript görevini tamamladı. Sonucu görmek için tarayıcıyı kontrol edebilirsiniz.")