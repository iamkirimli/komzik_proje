https://kozmikfiltreleme.streamlit.app/  -->  DEMO WEBSİTEMİZİN LİNKİ


🚀 Kozmik Ekip: Proje Kurulum ve Çalışma Rehberi

Arkadaşlar selam! Projenin iskeletini kurdum ve klasör yapısını profesyonel standartlara göre güncelledim. Artık hepimiz aynı sistem üzerinden, birbirimizin kodunu bozmadan, tam bir takım ruhuyla çalışabiliriz.

Aşağıda, projeyi bilgisayarınıza nasıl kuracağınızı ve çalışırken hangi kurallara uymanız gerektiğini adım adım anlattım.

🛠️ 1. Adım: Projeyi Bilgisayara Çekme (Clone)

Eğer projeyi daha önce bilgisayarınıza indirmediyseniz, VS Code terminalini açın ve şu komutla çekin:

Bash
git clone https://github.com/iamkirimli/komzik_proje.git

Not: Klasöre girdikten sonra VS Code ile bu klasörü açtığınızdan emin olun (File -> Open Folder).

📦 2. Adım: Kütüphanelerin Kurulumu

Gerekli kütüphaneleri (streamlit, pandas, numpy vb.) tek komutla kurun:

Bash

pip install -r requirements.txt

📂 3. Adım: Klasör Yapımız

Proje 3 ana parçadan oluşuyor:


src/: Ana mutfağımız. app.py (Arayüz) ve processing.py (Algoritmalar) burada.


scripts/: Veri üretme motorumuz (generate_data.py) burada.


data/: Tüm telemetri CSV dosyaları burada toplanacak.


🚀 4. Adım: Çalıştırma Komutları

Arayüzü (Streamlit) Başlatmak İçin: python -m streamlit run src/app.py


Yeni Veri Üretmek İçin: python scripts/generate_data.py

🔄 5. Adım: Çalışma Prensiplerimiz (Altın Kurallar)

Güne Başlarken (Pull): Her sabah mutlaka en güncel kodu çekin: git pull origin main


Sorumluluk Alanı: Size atanan dosya dışında bir yerde değişiklik yapacaksanız gruptan mutlaka haber verin.


Kod Gönderme (Push): İşiniz bitince sırayla: git add ., git commit -m "mesaj", git push origin main.


🎯 Görev Dağılımımız:

Algoritma Grubu: src/processing.py içinde Z-Score ve MAD filtrelerini geliştirip src/app.py entegrasyonuna odaklanın.


Veri ve Analiz Grubu: scripts/generate_data.py ile farklı senaryolar (Güneş patlaması, derin uzay vb.) üretip data/ klasörüne ekleyin.


Arayüz ve Görselleştirme: src/app.py üzerinde grafiklerin şıklığı ve kullanıcı deneyimi (UX) üzerinde çalışın.
