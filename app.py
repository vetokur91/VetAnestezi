import streamlit as st

# --- 1. SABİT VERİLER VE PROTOKOL TANIMLARI ---

# İlaç Konsantrasyonları (Varsayılan değerler)
ILAC_KONSLARI = {
    "Butorphanol": 10.0,    # 10 mg/mL
    "Tramadol": 50.0,      # 50 mg/mL
    "Morfin": 15.0,        # 15 mg/mL
    "Acepromazine": 10.0,  # 10 mg/mL
    "Medetomidine": 1.0,   # 1 mg/mL
    "Diazepam": 5.0,       # 5 mg/mL
    "Midazolam": 5.0,      # 5 mg/mL
    "Propofol": 10.0,
    "Alfaxalone": 10.0,
}

# ASA Sınıfına ve Türe Göre Örnek Başlangıç Dozaj Aralığı (mg/kg)
# Bu dozajlar, ASA Risk Yönetimine göre otomatik olarak DÜŞÜK veya STANDART olarak seçilecektir.
PROTOKOL_DOZLAR = {
    'kopek': {
        'Butorphanol': {'standart': 0.2, 'düşük': 0.1},
        'Tramadol': {'standart': 3.0, 'düşük': 2.0},
        'Morfin': {'standart': 0.5, 'düşük': 0.2},
        'Acepromazine': {'standart': 0.03, 'düşük': 0.015}, 
        'Medetomidine': {'standart': 0.01, 'düşük': 0.005}, 
        'Diazepam': {'standart': 0.5, 'düşük': 0.3},
        'Midazolam': {'standart': 0.2, 'düşük': 0.15},
        'Propofol': {'standart': 5.0, 'düşük': 2.5}, 
        'Alfaxalone': {'standart': 3.0, 'düşük': 1.5},
    },
    'kedi': {
        'Butorphanol': {'standart': 0.3, 'düşük': 0.15},
        'Tramadol': {'standart': 2.0, 'düşük': 1.0},
        'Morfin': {'standart': 0.1, 'düşük': 0.05},
        'Acepromazine': {'standart': 0.01, 'düşük': 0.005},
        'Medetomidine': {'standart': 0.007, 'düşük': 0.003},
        'Diazepam': {'standart': 0.5, 'düşük': 0.3},
        'Midazolam': {'standart': 0.15, 'düşük': 0.1},
        'Propofol': {'standart': 3.0, 'düşük': 1.5},
        'Alfaxalone': {'standart': 2.5, 'düşük': 1.25},
    }
}

# --- 2. HESAPLAMA FONKSİYONU ---

def doz_hesapla(konsantrasyon_mg_ml, dozaj_mg_kg, va_kg):
    """Belirtilen ilaç için mg ve mL cinsinden dozu hesaplar."""
    if konsantrasyon_mg_ml <= 0 or dozaj_mg_kg <= 0 or va_kg <= 0:
        return 0.0, 0.0
    
    toplam_mg = va_kg * dozaj_mg_kg
    hacim_ml = toplam_mg / konsantrasyon_mg_ml
    return toplam_mg, hacim_ml

# --- 3. STREAMLIT ARAYÜZ KISMI ---

# !!! BURAYI LOGONUZUN DİREKT İNTERNET ADRESİYLE DEĞİŞTİRİNİZ. !!!
LOGO_URL = "https://i.imgur.com/example_tuvecca_logo.png" # Placeholder Link

st.set_page_config(page_title="Tuvecca | Gelişmiş Veteriner Anestezi Hesaplayıcı", layout="wide")

# HTML ve CSS ile Logoyu Başlığın Üstüne Yerleştirme
st.markdown(f"""
    <style>
    .header-container {{
        display: flex;
        align-items: center;
        padding-bottom: 20px;
    }}
    .logo-img {{
        width: 80px; 
        height: 80px;
        margin-right: 25px;
        border-radius: 50%;
        object-fit: cover;
    }}
    .app-title {{
        font-size: 2.8em;
        font-weight: 700;
        color: #2c3e50;
    }}
    .app-subtitle {{
        font-size: 1.1em;
        color: #7f8c8d; 
    }}
    </style>
    <div class="header-container">
        <img class="logo-img" src="{LOGO_URL}"> 
        <div>
            <div class="app-title">TUVECCA</div>
            <div class="app-subtitle">Gelişmiş Anestezi Protokolü ve Doz Hesaplayıcı</div>
        </div>
    </div>
    <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), #3498db, rgba(0, 0, 0, 0));">
    """, unsafe_allow_html=True)


st.markdown("## 🐾 Sevimli Dostlarımız Güvende! 🐱🐶", unsafe_allow_html=True)
st.markdown("---")

# Yatay Giriş Bölümü
col_giriş_1, col_giriş_2 = st.columns([1, 1])

with col_giriş_1:
    st.header("1. Hasta Bilgileri")
    tur_secimi = st.radio("Hayvan Türü Seçin:", ('Köpek', 'Kedi'), key="tur_secim").lower().replace('ö', 'o').replace('ü', 'u')
    vucut_agirligi = st.number_input("Vücut Ağırlığı (kg):", min_value=0.1, value=10.0, step=0.1, format="%.1f", key="va_giris")
    
with col_giriş_2:
    st.header("2. Risk ve Protokol")
    asa_sinifi = st.selectbox(
        "ASA Fiziksel Durum Sınıfı (Risk Düzeyi):", 
        ('ASA I (Sağlıklı)', 'ASA II (Hafif Hastalık)', 'ASA III (Şiddetli Hastalık)', 'ASA IV (Hayatı Tehdit Eden)'), key="asa_secim"
    )
    
    # ASA sınıfına göre dozaj ayarı otomatik belirlenir.
    doz_ayari = 'standart'
    if 'III' in asa_sinifi or 'IV' in asa_sinifi:
        st.warning("ASA III/IV (Yüksek Risk) hastalar için dozajlar otomatik olarak DÜŞÜK PROTOKOL seçilerek kardiyovasküler stabilite önceliklendirilmiştir.", icon="❗")
        doz_ayari = 'düşük'

st.markdown("---")

# İlaç Seçimi ve Hesaplama Bölümü
st.header("3. 💉 İlaç Seçimi ve Hesaplamalar")

col_ilac_1, col_ilac_2, col_ilac_3 = st.columns(3)

# --- A. PREMEDİKASYON (OPİOİD) ---
with col_ilac_1:
    st.subheader("A. Opioid Analjezik")
    opioid_secim = st.selectbox("Kullanılacak Opioid:", ['Yok', 'Butorphanol', 'Tramadol', 'Morfin'], key="opioid_secim")
    
    if opioid_secim != 'Yok':
        opioid_kons_varsayilan = ILAC_KONSLARI.get(opioid_secim, 1.0)
        # Hekim elindeki konsantrasyonu güncelleyebilir
        opioid_kons = st.number_input(f"{opioid_secim} Konsantrasyon (mg/mL):", value=opioid_kons_varsayilan, step=0.1, format="%.1f", key="op_kons")
        
        # Dozaj ASA ve Türe göre otomatik belirlenir
        opioid_dozaj = PROTOKOL_DOZLAR[tur_secimi].get(opioid_secim, {'standart': 0.1, 'düşük': 0.05})[doz_ayari]
        st.caption(f"**Otomatik Doz:** {opioid_dozaj} mg/kg ({doz_ayari.upper()})")
        
        opioid_mg, opioid_ml = doz_hesapla(opioid_kons, opioid_dozaj, vucut_agirligi)
        
        st.success(f"**Toplam Doz (mg):** {opioid_mg:.2f} mg")
        st.success(f"**Çekilecek Hacim (mL):** {opioid_ml:.3f} mL")


# --- B. PREMEDİKASYON (SEDATİF/BENZO/Alfa-2) ---
with col_ilac_2:
    st.subheader("B. Sedatif / Tranquilizan")
    sedatif_secim = st.selectbox("Kullanılacak Sedatif:", ['Yok', 'Midazolam', 'Diazepam', 'Medetomidine', 'Acepromazine'], key="sedatif_secim")

    if sedatif_secim != 'Yok':
        sedatif_kons_varsayilan = ILAC_KONSLARI.get(sedatif_secim, 5.0)
        sedatif_kons = st.number_input(f"{sedatif_secim} Konsantrasyon (mg/mL):", value=sedatif_kons_varsayilan, step=0.1, format="%.1f", key="sed_kons")

        # Dozaj ASA ve Türe göre otomatik belirlenir
        sedatif_dozaj = PROTOKOL_DOZLAR[tur_secimi].get(sedatif_secim, {'standart': 0.2, 'düşük': 0.15})[doz_ayari]
        st.caption(f"**Otomatik Doz:** {sedatif_dozaj} mg/kg ({doz_ayari.upper()})")

        sedatif_mg, sedatif_ml = doz_hesapla(sedatif_kons, sedatif_dozaj, vucut_agirligi)

        st.success(f"**Toplam Doz (mg):** {sedatif_mg:.2f} mg")
        st.success(f"**Çekilecek Hacim (mL):** {sedatif_ml:.3f} mL")


# --- C. İNDÜKSİYON AJANI ---
with col_ilac_3:
    st.subheader("C. İndüksiyon Aj. (IV)")
    induksiyon_secim = st.selectbox("Kullanılacak İndüksiyon:", ['Propofol', 'Alfaxalone', 'Ketamin (Tek Başına)'], key="induksiyon_secim")

    if induksiyon_secim != 'Ketamin (Tek Başına)':
        ind_kons_varsayilan = ILAC_KONSLARI.get(induksiyon_secim, 10.0)
        ind_kons = st.number_input(f"{induksiyon_secim} Konsantrasyon (mg/mL):", value=ind_kons_varsayilan, step=0.1, format="%.1f", key="ind_kons")

        # Dozaj ASA ve Türe göre otomatik belirlenir
        ind_dozaj = PROTOKOL_DOZLAR[tur_secimi].get(induksiyon_secim, {'standart': 5.0, 'düşük': 2.5})[doz_ayari]
        st.caption(f"**Otomatik Başlangıç Dozu:** {ind_dozaj} mg/kg ({doz_ayari.upper()})")

        ind_mg, ind_ml = doz_hesapla(ind_kons, ind_dozaj, vucut_agirligi)

        st.success(f"**Başl. İnd. Dozu (mg):** {ind_mg:.2f} mg")
        st.success(f"**Çekilecek Hacim (mL):** {ind_ml:.3f} mL (Yavaşça titrate edin!)")
        
    else:
        st.warning("Ketamin tek başına kullanılmamalıdır; midazolam gibi bir benzodiazepin veya diğer sedatiflerle kombinasyon tercih edin.", icon="⚠️")
        ketamin_doz = st.number_input("Ketamin Dozu (mg/kg):", value=7.0, step=0.5, key="ket_doz") # Manuel giriş bırakıldı
        ketamin_kons = st.number_input("Ketamin Kons. (mg/mL):", value=100.0, step=1.0, key="ket_kons")
        ketamin_mg, ketamin_ml = doz_hesapla(ketamin_kons, ketamin_doz, vucut_agirligi)
        st.success(f"**Başl. İnd. Dozu (mg):** {ketamin_mg:.2f} mg")
        st.success(f"**Çekilecek Hacim (mL):** {ketamin_ml:.3f} mL")


st.markdown("---")

# --- D. SIVI İDAME HESAPLAMALARI ---
st.header("4. 💧 Sıvı İdame Hesaplamaları")

sivi_hizi = 10.0
if 'III' in asa_sinifi or 'IV' in asa_sinifi:
    sivi_hizi = 5.0 
    st.info(f"ASA III/IV riski nedeniyle başlangıç sıvı hızı {sivi_hizi} mL/kg/saat olarak ayarlanmıştır. Hızı elle ayarlayabilirsiniz.")

sivi_hizi_ayar = st.number_input("İstenen Sıvı Hızı (mL/kg/saat):", value=sivi_hizi, min_value=1.0, step=1.0, key="sivi_ayar")
set_faktor = st.radio("Damla Seti Kalibrasyonu (Damla/mL):", (60, 15), help="60: Mikro Set, 15: Makro Set", key="set_ayar")

saatlik_ihtiyac = vucut_agirligi * sivi_hizi_ayar
dakikalik_ihtiyac = saatlik_ihtiyac / 60.0
damla_hizi = dakikalik_ihtiyac * set_faktor

col_sivi_1, col_sivi_2 = st.columns(2)
with col_sivi_1:
    st.metric(label="Saatlik İnfüzyon Hızı (Pompa Ayarı)", value=f"{saatlik_ihtiyac:.2f} mL/saat")
with col_sivi_2:
    st.metric(label=f"Damla Hızı ({set_faktor} damla/mL)", value=f"{round(damla_hizi)} damla/dakika")

st.markdown("---")

# --- HAZIRLAYICILAR VE SORUMLULUK REDDİ ---
st.subheader("Hazırlayanlar")
st.markdown("""
* **Doç. Dr. Sıtkıcan OKUR**
* **Vet Hek Büşra BAYKAL**
""")

st.caption("🚨 **UYARI:** Bu araç yalnızca eğitim ve hızlı hesaplama amaçlıdır. Nihai teşhis, doz ayarlamaları ve protokol kararları her zaman bir **Veteriner Hekim** tarafından yapılmalıdır. Lütfen güncel tıbbi referansları kontrol edin.")
