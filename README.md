
-----

# Sahibinden İlan Kopyalama Otomasyonu

Bu proje, [sahibinden.com](https://sahibinden.com) üzerindeki eski veya yayında olmayan ilanlarınızı, tüm bilgileri ve fotoğraflarıyla birlikte kopyalayarak sıfırdan yeni bir ilan olarak oluşturan bir Python otomasyon script'idir. Script, ilanları yeniden listelemek ve en üste taşımak için gereken manuel işlemleri otomatize ederek zaman kazandırmak amacıyla geliştirilmiştir.

## ✨ Çalışan Özellikler

Script'in güncel versiyonu aşağıdaki işlemleri tam otomatik olarak gerçekleştirmektedir:

  - **Detaylı Veri Toplama:**

      - Eski ilanın sayfasındaki gizli bir JSON verisinden ilan özelliklerinin (kategori, konum, fiyat, teknik detaylar vb.) büyük bir kısmını hatasız bir şekilde çeker.
      - JSON verisinde bulunmayan ilan başlığını ve formatlı (paragraflı) ilan açıklamasını, doğrudan sayfanın görünür HTML'inden okur.

  - **Yüksek Kaliteli Fotoğraf İşleme:**

      - İlan sayfasındaki ana fotoğrafı ve tüm küçük resimleri (thumbnail) tespit eder.
      - Bulunan küçük resim URL'lerini, en yüksek çözünürlüklü versiyonlarını (`x16_`) işaret edecek şekilde akıllıca günceller.
      - Tüm yüksek kaliteli fotoğrafları proje klasöründeki `temp_images` adlı geçici bir dizine indirir.

  - **Akıllı Form Doldurma:**

      - "Aynı Kategoride Yeni İlan Ver" kısayolunu kullanarak yeni ilan formunu, kategoriler seçilmiş halde yeni bir sekmede açar.
      - Otomatik olarak yeni sekmeye geçiş yapar.
      - Modern web siteleriyle uyumluluk için, form alanlarını (başlık, açıklama, fiyat) doğrudan JavaScript komutları ile doldurur. Bu sayede, sitenin arka planındaki sistemin (AngularJS) yapılan değişiklikleri algılamaması sorunu aşılmıştır.
      - Standart açılır menüleri (`<select>`) ve dinamik olarak güncellenen menüleri (örn: Marka seçilince dolan Seri menüsü) başarılı bir şekilde yönetir.
      - İndirilen tüm yüksek kaliteli fotoğrafları yeni ilan formuna yükler.
      - Sayfayı aşağı kaydırarak gerekli onay kutularını ("İlan Verme Kuralları" ve "Otomatik Yeniden Yayınlama") güvenilir bir şekilde işaretler.

  - **Esnek ve Sürdürülebilir Yapı:**

      - Tüm CSS seçicileri (selector), koddan ayrı bir `selectors.json` dosyasında tutulur. Bu sayede, site tasarımında bir değişiklik olduğunda sadece bu JSON dosyasını güncellemek yeterlidir, ana koda dokunmaya gerek kalmaz.

## ⚙️ Kurulum ve Ön Hazırlık

Bu script'i çalıştırmak için aşağıdaki adımları izlemeniz gerekmektedir.

### Gereksinimler

  - Python 3.8 veya üstü
  - Google Chrome tarayıcısı

### Kurulum Adımları

1.  **Proje Dosyalarını İndirin:**
    Bu projeyi bilgisayarınıza klonlayın veya ZIP olarak indirin. `main.py` ve `selectors.json` dosyalarının aynı klasörde olduğundan emin olun.

2.  **Gerekli Kütüphaneleri Yükleyin:**
    Terminali veya Komut İstemi'ni proje klasöründe açın ve aşağıdaki komutları çalıştırarak gerekli Python kütüphanelerini yükleyin:

    ```bash
    pip install selenium
    pip install requests
    ```

3.  **Chrome'u Uzaktan Kontrol Modunda Başlatın (En Önemli Adım):**
    Script'in çalışabilmesi için Chrome'un özel bir modda başlatılması gerekmektedir.

      - **Önce açık olan tüm Chrome pencerelerini kapatın.**
      - Komut İstemi'ni (cmd) açın ve aşağıdaki komutu yapıştırıp Enter'a basın:

    <!-- end list -->

    ```cmd
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfile"
    ```

      - Bu komut, kontrol edilebilir yeni bir Chrome penceresi açacaktır. **Bu komutu çalıştırdığınız Komut İstemi penceresini, işlem boyunca kapatmayın.**

## 🚀 Kullanım Adımları

1.  Yukarıdaki komutla açılan **yeni ve boş Chrome penceresini** kullanarak:
    a. [sahibinden.com](https://sahibinden.com)'a gidin ve hesabınıza giriş yapın.
    b. Kopyalamak istediğiniz eski/pasif ilanınızın **detay sayfasına** gidin.
    c. Sayfadaki **"İşlemler"** menüsünü fareyle tıklayarak **açık bırakın**.

2.  Her şey hazır olduğunda, projenizin bulunduğu klasörde yeni bir terminal veya Komut İstemi açın ve `main.py` script'ini çalıştırın:

    ```bash
    python main.py
    ```

3.  Script'in ilanı kopyalayıp yeni formu doldurmasını izleyin. İşlem tamamlandığında, script son "Devam Et" butonuna basmadan duracak ve size son kontrol imkanı tanıyacaktır.

## ⚠️ Uyarı ve Sorumluluk Reddi

  - Bu script, eğitim ve kişisel kullanım kolaylığı amacıyla geliştirilmiştir.
  - Otomasyon araçlarının kullanımı, [sahibinden.com](https://sahibinden.com)'un Kullanım Koşulları'nı ihlal edebilir.
  - Bu script'in kullanımından doğabilecek herhangi bir sonuç (hesabın askıya alınması vb.) tamamen kullanıcının kendi sorumluluğundadır. Lütfen dikkatli ve sorumlu bir şekilde kullanın.