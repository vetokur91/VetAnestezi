import streamlit as st

# --- 1. SABİT VERİLER VE PROTOKOL TANIMLARI ---

# İlaç Konsantrasyonları (Varsayılan değerler)
ILAC_KONSLARI = {
    "Butorphanol": 10.0, "Tramadol": 50.0, "Morfin": 15.0, "Hydromorphone": 2.0, "Buprenorfin": 0.3,
    "Acepromazine": 10.0, "Medetomidine": 1.0, "Dexmedetomidine": 0.5, "Diazepam": 5.0, "Midazolam": 5.0,
    "Propofol": 10.0, "Alfaxalone": 10.0, "Ketamin": 100.0,
}

# ASA Risk, Türe ve Uygulama Yoluna Göre Örnek Dozajlar (mg/kg)
PROTOKOL_DOZLAR = {
    'kopek': {
        # Opioid ve Sedatif Dozları (IM/IV/SC/IN farkı gözetilir)
        'Butorphanol': {'IM': {'standart': 0.3, 'düşük': 0.15}, 'IV': {'standart': 0.2, 'düşük': 0.1}, 'SC': {'standart': 0.4, 'düşük': 0.2}, 'IN': {'standart': 0.4, 'düşük': 0.2}},
        'Morfin': {'IM': {'standart': 0.8, 'düşük': 0.4}, 'IV': {'standart': 0.5, 'düşük': 0.2}},
        'Hydromorphone': {'IM': {'standart': 0.15, 'düşük': 0.08}, 'IV': {'standart': 0.1, 'düşük': 0.05}},
        'Buprenorfin': {'IM': {'standart': 0.025, 'düşük': 0.015}, 'IV': {'standart': 0.02, 'düşük': 0.01}, 'SC': {'standart': 0.03, 'düşük': 0.02}},
        'Tramadol': {'IM': {'standart': 3.0, 'düşük': 2.0}, 'IV': {'standart': 2.0, 'düşük': 1.5}},
        
        'Acepromazine': {'IM': {'standart': 0.05, 'düşük': 0.025}, 'IV': {'standart': 0.03, 'düşük': 0.015}},
        'Medetomidine': {'IM': {'standart': 0.015, 'düşük': 0.008}, 'IV': {'standart': 0.01, 'düşük': 0.005}},
        'Dexmedetomidine': {'IM': {'standart': 0.005, 'düşük': 0.0025}, 'IV': {'standart': 0.003, 'düşük': 0.0015}},
        'Midazolam': {'IM': {'standart': 0.3, 'düşük': 0.15}, 'IV': {'standart': 0.2, 'düşük': 0.1}},
        'Diazepam': {'IM': {'standart': 0.4, 'düşük': 0.2}, 'IV': {'standart': 0.3, 'düşük': 0.15}}, # IV yavaş verilmeli
        
        # İndüksiyon Dozları (Varsayılan IV kabul edilir)
        'Propofol': {'IV': {'standart': 5.0, 'düşük': 2.5}},
        'Alfaxalone': {'IV': {'standart': 3.0, 'düşük': 1.5}},
    },
    'kedi': {
        'Butorphanol': {'IM': {'standart': 0.4, 'düşük': 0.2}, 'IV': {'standart': 0.3, 'düşük': 0.15}, 'SC': {'standart': 0.5, 'düşük': 0.25}, 'IN': {'standart': 0.5, 'düşük': 0.25}},
        'Morfin': {'IM': {'standart': 0.3, 'düşük': 0.15}, 'IV': {'standart': 0.1, 'düşük': 0.05}},
        'Hydromorphone': {'IM': {'standart': 0.1, 'düşük': 0.05}, 'IV': {'standart': 0.05, 'düşük': 0.03}},
        'Buprenorfin': {'IM': {'standart': 0.025, 'düşük': 0.015}, 'IV': {'standart': 0.02, 'düşük': 0.01}, 'SC': {'standart': 0.03, 'düşük': 0.02}},
        'Tramadol': {'IM': {'standart': 2.0, 'düşük': 1.0}, 'IV': {'standart': 1.5, 'düşük': 0.75}},

        'Acepromazine': {'IM': {'standart': 0.02, 'düşük': 0.01}, 'IV': {'standart': 0.01, 'düşük': 0.005}},
        'Medetomidine': {'IM': {'standart': 0.01, 'düşük': 0.005}, 'IV': {'standart': 0.007, 'düşük': 0.003}},
        'Dexmedetomidine': {'IM': {'standart': 0.004, 'düşük': 0.002}, 'IV': {'standart': 0.003, 'düşük': 0.0015}},
        'Midazolam': {'IM': {'standart': 0.2, 'düşük': 0.1}, 'IV': {'standart': 0.15, 'düşük': 0.08}},
        'Diazepam': {'IM': {'standart': 0.4, 'düşük': 0.2}, 'IV': {'standart': 0.3, 'düşük': 0.15}},

        'Propofol': {'IV': {'standart': 3.0, 'düşük': 1.5}},
        'Alfaxalone': {'IV': {'standart': 2.5, 'düşük': 1.25}},
    }
}

# --- 2. HESAPLAMA FONKSİYONU (Aynı Kaldı) ---
def doz_hesapla(konsantrasyon_mg_ml, dozaj_mg_kg, va_kg):
    if konsantrasyon_mg_ml <= 0 or dozaj_mg_kg <= 0 or va_kg <= 0: return 0.0, 0.0
    toplam_mg = va_kg * dozaj_mg_kg
    hacim_ml = toplam_mg / konsantrasyon_mg_ml
    return toplam_mg, hacim_ml

# --- 3. OTURUM DURUMU YÖNETİMİ (Aynı Kaldı) ---
if 'page' not in st.session_state: st.session_state['page'] = 1
if 'vucut_agirligi' not in st.session_state: st.session_state['vucut_agirligi'] = 10.0
if 'tur_secimi' not in st.session_state: st.session_state['tur_secimi'] = 'kopek'
if 'asa_sinifi' not in st.session_state: st.session_state['asa_sinifi'] = 'ASA I (Sağlıklı)'
if 'secili_ilaclar' not in st.session_state: st.session_state['secili_ilaclar'] = {}

def go_to_page(page_num):
    st.session_state['page'] = page_num

# --- 4. ARAYÜZ FONKSİYONLARI ---

def render_header():
    LOGO_URL = "https://images.squarespace-cdn.com/content/v1/64b4f89629c6c70b36f31cbb/ec7840bb-fd29-4b5d-8d82-a2c4bfd26a68/logo.png"
    st.set_page_config(page_title="Tuvecca | Anestezi Hesaplayıcı", layout="wide")
    
    st.markdown(f"""
        <style>
        .header-container {{ display: flex; align-items: center; padding-bottom: 20px; }}
        .logo-img {{ width: 80px; height: 80px; margin-right: 25px; border-radius: 10px; object-fit: contain; }}
        .app-title {{ font-size: 3.0em; font-weight: 800; color: #195190; }}
        .app-subtitle {{ font-size: 1.1em; color: #3e5f7d; }}
        </style>
        <div class="header-container">
            <img class="logo-img" src="{LOGO_URL}"> 
            <div>
                <div class="app-title">TUVECCA</div>
                <div class="app-subtitle">Profesyonel Veteriner Anestezi Protokol ve Doz Hesaplayıcı</div>
            </div>
        </div>
        <hr style="border: 0; height: 3px; background-color: #f39c12;">
        """, unsafe_allow_html=True)

def page_1_input_patient_info():
    st.markdown("## 📋 Aşama 1: Temel Hasta Bilgileri ve Risk Değerlendirmesi")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hayvan Türü ve Ağırlığı")
        tur_secimi = st.radio("Hayvan Türü Seçin:", ('Köpek', 'Kedi'), key="p1_tur")
        st.session_state['tur_secimi'] = tur_secimi.lower().replace('ö', 'o').replace('ü', 'u')
        vucut_agirligi = st.number_input("Vücut Ağırlığı (kg):", min_value=0.1, value=st.session_state['vucut_agirligi'], step=0.1, format="%.1f", key="p1_va")
        st.session_state['vucut_agirligi'] = vucut_agirligi

    with col2:
        st.subheader("ASA Risk Sınıfı")
        asa_sinifi = st.selectbox(
            "ASA Fiziksel Durum Sınıfını Seçin:", 
            ('ASA I (Sağlıklı)', 'ASA II (Hafif Hastalık)', 'ASA III (Şiddetli Hastalık)', 'ASA IV (Hayatı Tehdit Eden)'), key="p1_asa"
        )
        st.session_state['asa_sinifi'] = asa_sinifi
        st.info("Risk sınıfına göre tüm ilaç dozları otomatik olarak düşük veya standart protokolden seçilecektir.")
        
    st.markdown("---")
    if st.button("2. AŞAMAYA GEÇ: İlaç Seçimi ve Uygulama Yolu", type="primary"):
        go_to_page(2)

def page_2_select_anesthetics():
    st.markdown("## 🛒 Aşama 2: Elinizdeki İlaçları, Konsantrasyonlarını ve Uygulama Yollarını Seçin")
    st.info(f"Hasta: **{st.session_state['vucut_agirligi']} kg {st.session_state['tur_secimi'].upper()}** | Risk: **{st.session_state['asa_sinifi']}**")
    st.markdown("---")

    col_ilac_1, col_ilac_2, col_ilac_3 = st.columns(3)
    secili_ilaclar_temp = {}
    
    # Tüm İlaç Listeleri ve Yollar
    opioid_listesi = ['Yok', 'Butorphanol', 'Tramadol', 'Morfin', 'Hydromorphone', 'Buprenorfin']
    sedatif_listesi = ['Yok', 'Midazolam', 'Diazepam', 'Medetomidine', 'Dexmedetomidine', 'Acepromazine']
    induksiyon_listesi = ['Propofol', 'Alfaxalone', 'Ketamin (Manuel Doz)']
    
    # Uygulama Yolları (Induksiyon hariç)
    uygulama_yollari_opioid_sedatif = ['IM (Kas İçi)', 'IV (Damar İçi)', 'SC (Deri Altı)', 'IN (İntranazal)']
    uygulama_yolu_iv = ['IV (Damar İçi)'] # Propofol/Alfaxalone için tek seçenek

    # --- A. PREMEDİKASYON (OPİOİD) ---
    with col_ilac_1:
        st.subheader("A. Opioid Analjezik")
        opioid_secim = st.selectbox("1. Opioid Seçimi:", opioid_listesi, key="p2_op_secim")
        
        if opioid_secim != 'Yok':
            # **Opioid Uygulama Yolu Seçimi**
            opioid_yol = st.selectbox("2. Uygulama Yolu:", uygulama_yollari_opioid_sedatif, key="p2_op_yol")
            opioid_kons_varsayilan = ILAC_KONSLARI.get(opioid_secim, 1.0)
            opioid_kons = st.number_input(f"3. Konsantrasyon (mg/mL):", value=opioid_kons_varsayilan, step=0.1, format="%.1f", key="p2_op_kons")
            
            secili_ilaclar_temp['Opioid'] = {'ad': opioid_secim, 'kons': opioid_kons, 'yol': opioid_yol.split(' ')[0]}
            st.caption("Dozlar 3. aşamada uygulama yolu ve riske göre otomatik belirlenecektir.")

    # --- B. PREMEDİKASYON (SEDATİF/TRANQUİLİZAN) ---
    with col_ilac_2:
        st.subheader("B. Sedatif / Tranquilizan")
        sedatif_secim = st.selectbox("1. Sedatif Seçimi:", sedatif_listesi, key="p2_sed_secim")

        if sedatif_secim != 'Yok':
            # **Sedatif Uygulama Yolu Seçimi**
            sedatif_yol = st.selectbox("2. Uygulama Yolu:", uygulama_yollari_opioid_sedatif, key="p2_sed_yol")
            sedatif_kons_varsayilan = ILAC_KONSLARI.get(sedatif_secim, 5.0)
            sedatif_kons = st.number_input(f"3. Konsantrasyon (mg/mL):", value=sedatif_kons_varsayilan, step=0.1, format="%.1f", key="p2_sed_kons")
            
            secili_ilaclar_temp['Sedatif'] = {'ad': sedatif_secim, 'kons': sedatif_kons, 'yol': sedatif_yol.split(' ')[0]}
            st.caption("Dozlar 3. aşamada uygulama yolu ve riske göre otomatik belirlenecektir.")

    # --- C. İNDÜKSİYON AJANI ---
    with col_ilac_3:
        st.subheader("C. İndüksiyon Aj. (IV)")
        induksiyon_secim = st.selectbox("1. İndüksiyon Seçimi:", induksiyon_listesi, key="p2_ind_secim")
        
        if induksiyon_secim != 'Ketamin (Manuel Doz)':
            ind_adi = induksiyon_secim
            
            # Propofol/Alfaxalone için uygulama yolu IV varsayılır (Gerekirse IM de eklenebilir ancak IV yaygındır)
            st.markdown("2. Uygulama Yolu: **IV (Damar İçi) (Varsayılan)**")
            ind_yol = 'IV' 
            
            ind_kons_varsayilan = ILAC_KONSLARI.get(ind_adi, 10.0)
            ind_kons = st.number_input(f"3. Konsantrasyon (mg/mL):", value=ind_kons_varsayilan, step=0.1, format="%.1f", key="p2_ind_kons")
            
            secili_ilaclar_temp['İndüksiyon'] = {'ad': ind_adi, 'kons': ind_kons, 'yol': ind_yol}
            st.caption("Propofol/Alfaxalone dozu 3. aşamada IV protokolüne göre belirlenecektir.")
        else:
            # Ketamin'de manuel doz ve uygulama yolu seçimi
            ketamin_yol_secimi = st.selectbox("2. Uygulama Yolu:", uygulama_yollari_induksiyon, key="p2_ket_yol")
            ketamin_yol = ketamin_yol_secimi.split(' ')[0]
            
            ketamin_kons_varsayilan = ILAC_KONSLARI.get('Ketamin', 100.0)
            ketamin_kons = st.number_input("3. Kons. (mg/mL):", value=ketamin_kons_varsayilan, step=1.0, key="p2_ket_kons")
            ketamin_doz = st.number_input("4. Ketamin Dozu (mg/kg):", value=7.0, step=0.5, key="p2_ket_doz")
            
            secili_ilaclar_temp['İndüksiyon'] = {'ad': 'Ketamin', 'kons': ketamin_kons, 'yol': ketamin_yol, 'manuel_doz_mg_kg': ketamin_doz}
            st.caption("Ketamin dozu manuel girilmiştir.")


    st.markdown("---")
    col_nav_1, col_nav_2 = st.columns(2)
    with col_nav_1:
        if st.button("⬅️ 1. Aşamaya Geri Dön"):
            go_to_page(1)
    with col_nav_2:
        if st.button("3. AŞAMAYA GEÇ: Doz Hesaplama Sonuçları", type="primary"):
            st.session_state['secili_ilaclar'] = secili_ilaclar_temp
            go_to_page(3)


def page_3_show_results():
    st.markdown("## ✅ Aşama 3: Nihai Doz Hesaplama Sonuçları")
    
    va_kg = st.session_state['vucut_agirligi']
    tur_secimi = st.session_state['tur_secimi']
    asa_sinifi = st.session_state['asa_sinifi']
    secili_ilaclar = st.session_state['secili_ilaclar']
    
    doz_ayari = 'standart'
    if 'III' in asa_sinifi or 'IV' in asa_sinifi:
        doz_ayari = 'düşük'
        st.error(f"⚠️ YÜKSEK RİSK ({asa_sinifi}) nedeniyle tüm dozlar otomatik olarak **DÜŞÜK PROTOKOL** ile hesaplanmıştır.", icon="❗")
    else:
        st.success(f"Düşük Risk ({asa_sinifi}) nedeniyle tüm dozlar **STANDART PROTOKOL** ile hesaplanmıştır.")

    st.markdown("---")
    st.subheader(f"1. İlaç Dozajları (Hasta: {va_kg:.1f} kg)")

    cols = st.columns(3)
    ilac_tipleri = ['Opioid', 'Sedatif', 'İndüksiyon']
    
    for i, tip in enumerate(ilac_tipleri):
        if tip in secili_ilaclar:
            ilac = secili_ilaclar[tip]
            ilac_adi = ilac['ad']
            ilac_kons = ilac['kons']
            ilac_yol = ilac['yol']
            
            with cols[i]:
                st.markdown(f"**{tip}: {ilac_adi}**")
                st.caption(f"Uygulama Yolu: **{ilac_yol}**")
                
                if ilac_adi == 'Ketamin':
                    dozaj_mg_kg = ilac['manuel_doz_mg_kg']
                    st.caption(f"Manuel Doz: {dozaj_mg_kg} mg/kg")
                else:
                    # Otomatik dozajı Uygulama Yolu'na göre çek
                    doz_set = PROTOKOL_DOZLAR[tur_secimi].get(ilac_adi, {}).get(ilac_yol, None)
                    
                    if doz_set is None:
                        # Eğer seçilen yol (Örn: Tramadol için IV seçildi ama listede yoksa IM'yi varsay)
                        yol_varsayilan = 'IM' if tip != 'İndüksiyon' else 'IV'
                        
                        # Eğer Propofol/Alfaxalone için yanlışlıkla farklı bir yol seçildiyse IV'yi varsay
                        if tip == 'İndüksiyon' and ilac_yol != 'IV':
                            dozaj_mg_kg = PROTOKOL_DOZLAR[tur_secimi].get(ilac_adi, {}).get('IV', {'standart': 1.0, 'düşük': 0.5})[doz_ayari]
                            st.warning(f"⚠️ {ilac_adi} için sadece IV protokolü uygulanır. IV dozu varsayıldı.")
                        else:
                            dozaj_mg_kg = PROTOKOL_DOZLAR[tur_secimi].get(ilac_adi, {}).get(yol_varsayilan, {'standart': 1.0, 'düşük': 0.5})[doz_ayari]
                            st.warning(f"⚠️ **{ilac_yol}** için kesin protokol bulunamadı. **{yol_varsayilan}** dozu varsayıldı.")
                    else:
                        dozaj_mg_kg = doz_set[doz_ayari]
                    
                    st.caption(f"Otomatik Doz: {dozaj_mg_kg} mg/kg ({doz_ayari.upper()})")

                toplam_mg, hacim_ml = doz_hesapla(ilac_kons, dozaj_mg_kg, va_kg)
                
                st.metric(label="Toplam Doz (mg)", value=f"{toplam_mg:.2f} mg")
                st.metric(label=f"Çekilecek Hacim (mL)", value=f"{hacim_ml:.3f} mL", help=f"Kullanılan Konsantrasyon: {ilac_kons} mg/mL")
        else:
            with cols[i]:
                st.markdown(f"**{tip}**")
                st.info("İlaç Seçilmedi")

    # --- SIVI İDAME HESAPLAMALARI ---
    st.markdown("---")
    st.subheader("2. Sıvı İdame Hesaplamaları")

    sivi_hizi = 10.0
    if 'III' in asa_sinifi or 'IV' in asa_sinifi: sivi_hizi = 5.0 
    st.info(f"Yüksek Risk nedeniyle başlangıç sıvı hızı 5 mL/kg/saat olarak ayarlanmıştır. Hızı elle ayarlayabilirsiniz.")

    sivi_hizi_ayar = st.number_input("İstenen Sıvı Hızı (mL/kg/saat):", value=sivi_hizi, min_value=1.0, step=1.0, key="sivi_ayar")
    set_faktor = st.radio("Damla Seti Kalibrasyonu (Damla/mL):", (60, 15), help="60: Mikro Set, 15: Makro Set", key="set_ayar")

    saatlik_ihtiyac = va_kg * sivi_hizi_ayar
    dakikalik_ihtiyac = saatlik_ihtiyac / 60.0
    damla_hizi = dakikalik_ihtiyac * set_faktor

    col_sivi_1, col_sivi_2 = st.columns(2)
    with col_sivi_1:
        st.metric(label="Saatlik İnfüzyon Hızı (Pompa Ayarı)", value=f"{saatlik_ihtiyac:.2f} mL/saat")
    with col_sivi_2:
        st.metric(label=f"Damla Hızı ({set_faktor} damla/mL)", value=f"{round(damla_hizi)} damla/dakika")

    st.markdown("---")
    if st.button("⬅️ Protokolü Tekrar Düzenle (2. Aşamaya Dön)", type="secondary"):
        go_to_page(2)


# --- 5. ANA UYGULAMA MANTIĞI ---

render_header()

if st.session_state['page'] == 1:
    page_1_input_patient_info()
elif st.session_state['page'] == 2:
    page_2_select_anesthetics()
elif st.session_state['page'] == 3:
    page_3_show_results()

# --- HAZIRLAYICILAR VE SORUMLULUK REDDİ ---
st.markdown("---")
st.subheader("Programı Hazırlayanlar")
st.markdown("""
* **Doç. Dr. Sıtkıcan OKUR**
* **Vet Hek Büşra BAYKAL**
""")

st.caption("🚨 **ÖNEMLİ UYARI:** Bu araç yalnızca eğitim ve hızlı hesaplama amaçlıdır. Verilen dozajlar genel klinik referanslardan alınmıştır ve final kararı her zaman bir **Veteriner Hekim** tarafından verilmelidir.")
