import streamlit as st
import io

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
        'Butorphanol': {'IM': {'standart': 0.3, 'düşük': 0.15}, 'IV': {'standart': 0.2, 'düşük': 0.1}, 'SC': {'standart': 0.4, 'düşük': 0.2}, 'IN': {'standart': 0.4, 'düşük': 0.2}},
        'Morfin': {'IM': {'standart': 0.8, 'düşük': 0.4}, 'IV': {'standart': 0.5, 'düşük': 0.2}},
        'Hydromorphone': {'IM': {'standart': 0.15, 'düşük': 0.08}, 'IV': {'standart': 0.1, 'düşük': 0.05}},
        'Buprenorfin': {'IM': {'standart': 0.025, 'düşük': 0.015}, 'IV': {'standart': 0.02, 'düşük': 0.01}, 'SC': {'standart': 0.03, 'düşük': 0.02}},
        'Tramadol': {'IM': {'standart': 3.0, 'düşük': 2.0}, 'IV': {'standart': 2.0, 'düşük': 1.5}},
        'Acepromazine': {'IM': {'standart': 0.05, 'düşük': 0.025}, 'IV': {'standart': 0.03, 'düşük': 0.015}},
        'Medetomidine': {'IM': {'standart': 0.015, 'düşük': 0.008}, 'IV': {'standart': 0.01, 'düşük': 0.005}},
        'Dexmedetomidine': {'IM': {'standart': 0.005, 'düşük': 0.0025}, 'IV': {'standart': 0.003, 'düşük': 0.0015}},
        'Midazolam': {'IM': {'standart': 0.3, 'düşük': 0.15}, 'IV': {'standart': 0.2, 'düşük': 0.1}},
        'Diazepam': {'IM': {'standart': 0.4, 'düşük': 0.2}, 'IV': {'standart': 0.3, 'düşük': 0.15}},
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

# --- 2. HESAPLAMA FONKSİYONU ---
def doz_hesapla(konsantrasyon_mg_ml, dozaj_mg_kg, va_kg):
    if konsantrasyon_mg_ml <= 0 or dozaj_mg_kg <= 0 or va_kg <= 0: return 0.0, 0.0
    toplam_mg = va_kg * dozaj_mg_kg
    hacim_ml = toplam_mg / konsantrasyon_mg_ml
    return toplam_mg, hacim_ml

# --- 3. OTURUM DURUMU (SESSION STATE) YÖNETİMİ ---
if 'page' not in st.session_state: st.session_state['page'] = 1
if 'vucut_agirligi' not in st.session_state: st.session_state['vucut_agirligi'] = 10.0
if 'tur_secimi' not in st.session_state: st.session_state['tur_secimi'] = 'kopek'
if 'asa_sinifi' not in st.session_state: st.session_state['asa_sinifi'] = 'ASA I (Sağlıklı)'
if 'secili_ilaclar' not in st.session_state: st.session_state['secili_ilaclar'] = {}
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{'role': 'assistant', 'content': "Merhaba! Tuvecca Anestezi Asistanıyım. Uygulama nasıl kullanılır, dozlar nasıl hesaplanır, ASA nedir gibi sorularınızı yanıtlayabilirim."}]
if 'uploaded_kan_tablosu' not in st.session_state: st.session_state['uploaded_kan_tablosu'] = None
# Kan değerleri için başlangıç değerleri
if 'WBC' not in st.session_state: st.session_state['WBC'] = 10.0
if 'HCT' not in st.session_state: st.session_state['HCT'] = 40.0
if 'BUN' not in st.session_state: st.session_state['BUN'] = 20.0
if 'CREA' not in st.session_state: st.session_state['CREA'] = 1.0
if 'ALT' not in st.session_state: st.session_state['ALT'] = 50
if 'GLU' not in st.session_state: st.session_state['GLU'] = 100

def go_to_page(page_num):
    st.session_state['page'] = page_num

# --- 4. CHATBOT MANTIĞI ---
def generate_ai_response(prompt):
    prompt_lower = prompt.lower()
    
    # Uygulama Kullanımı
    if "kullanım" in prompt_lower or "nasıl kullanılır" in prompt_lower:
        return "Uygulama 3 aşamadan oluşur: 1. Hasta bilgisi (ağırlık/tür/ASA) ve kan tablosu verileri girilir. 2. Kullanmak istediğiniz ilaçlar ve uygulama yolları seçilir. 3. Nihai dozaj sonuçları ve model analizi otomatik hesaplanır."
    
    # Hesaplama Mantığı
    elif "doz" in prompt_lower and ("hesap" in prompt_lower or "nasıl" in prompt_lower):
        return "Dozaj (mL) şu formülle hesaplanır: `(Vücut Ağırlığı (kg) * Dozaj (mg/kg)) / Konsantrasyon (mg/mL)`. Dozajlar risk sınıfına ve uygulama yoluna göre otomatik ayarlanır."
    
    # ASA Açıklamaları
    elif "asa" in prompt_lower:
        if "i" in prompt_lower:
             return "ASA I: Sağlıklı hasta. Elektif cerrahi için idealdir."
        elif "ii" in prompt_lower:
             return "ASA II: Hafif sistemik hastalığı olan hasta (Örn: yaşlı, hafif obez). Düşük protokole geçiş düşünülebilir."
        elif "iii" in prompt_lower:
             return "ASA III: Şiddetli sistemik hastalığı olan hasta (Örn: anemi, hafif kalp yetmezliği). Düşük doz protokolü zorunludur."
        elif "iv" in prompt_lower:
             return "ASA IV: Hayati tehlike arz eden, şiddetli sistemik hastalığı olan hasta. Mümkün olan en düşük dozlar ve IV infüzyon tercih edilmelidir."
        else:
             return "ASA, anestezi riskini belirlemek için kullanılan Fiziksel Durum Sınıflandırmasıdır (ASA I - IV)."
             
    # Default Cevap
    else:
        return "Bu konu hakkında uygulama içinde bilgi veremiyorum. Lütfen uygulama kullanımı, doz hesaplama veya ASA risk sınıfları ile ilgili bir soru sorun."

def render_chatbot():
    with st.sidebar:
        st.subheader("💬 Tuvecca Anestezi Asistanı")
        
        for message in st.session_state['messages']:
            with st.chat_message(message['role']):
                st.write(message['content'])

        prompt = st.chat_input("Sorunuzu buraya yazın...")
        
        if prompt:
            st.session_state['messages'].append({'role': 'user', 'content': prompt})
            with st.chat_message('user'):
                st.write(prompt)
            
            with st.chat_message('assistant'):
                with st.spinner("Asistan yanıt üretiyor..."):
                    ai_response = generate_ai_response(prompt)
                    st.write(ai_response)
                    st.session_state['messages'].append({'role': 'assistant', 'content': ai_response})

# --- 5. ARAYÜZ FONKSİYONLARI ---

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
    
    # KAN TABLOSU YÜKLEYİCİ VE MANUEL GİRİŞ
    with st.expander("🔬 Derin Öğrenme Analizi İçin Kan Tablosu Verileri"):
        
        # 1. Dosya Yükleyici
        uploaded_file = st.file_uploader(
            "Kan tablosu dosyanızı yükleyin (Görüntü, PDF veya CSV)", 
            type=["png", "jpg", "jpeg", "pdf", "csv"]
        )
        
        if uploaded_file is not None:
            st.session_state['uploaded_kan_tablosu'] = uploaded_file
            st.success(f"'{uploaded_file.name}' dosyası yüklendi. Verilerin okunması için OCR/Pandas entegrasyonu gereklidir.")
            
            if uploaded_file.name.endswith('.csv'):
                st.caption("CSV formatı model için en kolay okunabilir formattır. İleride Pandas ile bu veriyi işleyebiliriz.")
            else:
                st.caption("⚠️ **Görüntü/PDF** formatları için **Gelişmiş OCR (Görüntü Tanıma) entegrasyonu** gereklidir.")
        else:
            st.session_state['uploaded_kan_tablosu'] = None

        st.markdown("### Veya Temel Kan Değerlerini Elle Girin (Önerilen Hızlı Başlangıç)")
        
        # 2. Manuel Veri Girişi
        col_blood_1, col_blood_2, col_blood_3 = st.columns(3)
        
        with col_blood_1:
            st.session_state['WBC'] = st.number_input("WBC (10^3/uL)", min_value=0.1, value=st.session_state['WBC'], step=0.1, format="%.1f", key="input_wbc")
            st.session_state['HCT'] = st.number_input("HCT (%)", min_value=1.0, value=st.session_state['HCT'], step=0.1, format="%.1f", key="input_hct")
        
        with col_blood_2:
            st.session_state['BUN'] = st.number_input("BUN (mg/dL)", min_value=1.0, value=st.session_state['BUN'], step=1.0, format="%d", key="input_bun")
            st.session_state['CREA'] = st.number_input("Kreatinin (mg/dL)", min_value=0.1, value=st.session_state['CREA'], step=0.1, format="%.1f", key="input_crea")
            
        with col_blood_3:
            st.session_state['ALT'] = st.number_input("ALT (U/L)", min_value=1, value=st.session_state['ALT'], step=1, key="input_alt")
            st.session_state['GLU'] = st.number_input("GLU (mg/dL)", min_value=1, value=st.session_state['GLU'], step=1, key="input_glu")
            
        st.caption("Elle girilen bu veriler, 3. aşamada derin öğrenme modelinizin anestezi risk tahminine girdi olarak sunulacaktır.")
    
    st.markdown("---")
    
    if st.button("2. AŞAMAYA GEÇ: İlaç Seçimi ve Uygulama Yolu", type="primary", key="btn_next_p1"):
        go_to_page(2)

def page_2_select_anesthetics():
    st.markdown("## 🛒 Aşama 2: Elinizdeki İlaçları, Konsantrasyonlarını ve Uygulama Yollarını Seçin")
    st.info(f"Hasta: **{st.session_state['vucut_agirligi']} kg {st.session_state['tur_secimi'].upper()}** | Risk: **{st.session_state['asa_sinifi']}**")
    
    # Kan Tablosu Yüklendiyse/Girildiyse Ek Bilgi Gösterimi (DÜZELTİLMİŞ SATIR)
    if st.session_state['uploaded_kan_tablosu'] or 'WBC' in st.session_state:
        # F-STRING HATASI BU SATIRDA ÇÖZÜLMÜŞTÜR.
        st.warning(f"Kan verileri sisteme girildi ({st.session_state.get('WBC', '-')} WBC, {st.session_state.get('BUN', '-')} BUN vb.). Bu veriler 3. aşamada risk analizi için kullanılacaktır.")

    st.markdown("---")

    col_ilac_1, col_ilac_2, col_ilac_3 = st.columns(3)
    secili_ilaclar_temp = {}
    
    opioid_listesi = ['Yok', 'Butorphanol', 'Tramadol', 'Morfin', 'Hydromorphone', 'Buprenorfin']
    sedatif_listesi = ['Yok', 'Midazolam', 'Diazepam', 'Medetomidine', 'Dexmedetomidine', 'Acepromazine']
    induksiyon_listesi = ['Propofol', 'Alfaxalone', 'Ketamin (Manuel Doz)']
    
    uygulama_yollari_opioid_sedatif = ['IM (Kas İçi)', 'IV (Damar İçi)', 'SC (Deri Altı)', 'IN (İntranazal)']
    uygulama_yollari_ketamin = ['IV (Damar İçi)', 'IM (Kas İçi)']

    # --- A. PREMEDİKASYON (OPİOİD) ---
    with col_ilac_1:
        st.subheader("A. Opioid Analjezik")
        opioid_secim = st.selectbox("1. Opioid Seçimi:", opioid_listesi, key="p2_op_secim")
        
        if opioid_secim != 'Yok':
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
            st.markdown("2. Uygulama Yolu: **IV (Damar İçi)**")
            ind_yol = 'IV' 
            
            ind_kons_varsayilan = ILAC_KONSLARI.get(ind_adi, 10.0)
            ind_kons = st.number_input(f"3. Konsantrasyon (mg/mL):", value=ind_kons_varsayilan, step=0.1, format="%.1f", key="p2_ind_kons")
            
            secili_ilaclar_temp['İndüksiyon'] = {'ad': ind_adi, 'kons': ind_kons, 'yol': ind_yol}
            st.caption("Dozlar IV protokolüne göre belirlenecektir.")
        else:
            ketamin_yol_secimi = st.selectbox("2. Uygulama Yolu:", uygulama_yollari_ketamin, key="p2_ket_yol")
            ketamin_yol = ketamin_yol_secimi.split(' ')[0]
            
            ketamin_kons_varsayilan = ILAC_KONSLARI.get('Ketamin', 100.0)
            ketamin_kons = st.number_input("3. Kons. (mg/mL):", value=ketamin_kons_varsayilan, step=1.0, key="p2_ket_kons")
            ketamin_doz = st.number_input("4. Ketamin Dozu (mg/kg):", value=7.0, step=0.5, key="p2_ket_doz")
            
            secili_ilaclar_temp['İndüksiyon'] = {'ad': 'Ketamin', 'kons': ketamin_kons, 'yol': ketamin_yol, 'manuel_doz_mg_kg': ketamin_doz}
            st.caption("Ketamin dozu manuel girilmiştir.")


    st.markdown("---")
    col_nav_1, col_nav_2 = st.columns(2)
    with col_nav_1:
        if st.button("⬅️ 1. Aşamaya Geri Dön", key="btn_prev_p2"):
            go_to_page(1)
    with col_nav_2:
        if st.button("3. AŞAMAYA GEÇ: Doz Hesaplama Sonuçları", type="primary", key="btn_next_p2"):
            st.session_state['secili_ilaclar'] = secili_ilaclar_temp
            go_to_page(3)


def page_3_show_results():
    st.markdown("## ✅ Aşama 3: Nihai Doz Hesaplama Sonuçları")
    
    va_kg = st.session_state['vucut_agirligi']
    tur_secimi = st.session_state['tur_secimi']
    asa_sinifi = st.session_state['asa_sinifi']
    secili_ilaclar = st.session_state['secili_ilaclar']
    
    # Kan tablosu analizi bölümü (Model sonuçları buraya gelecek)
    st.subheader("🚨 Kan Tablosu Derin Öğrenme Analizi")
    
    kan_verileri = {
        "WBC": st.session_state.get('WBC'), "HCT": st.session_state.get('HCT'), 
        "BUN": st.session_state.get('BUN'), "CREA": st.session_state.get('CREA'),
        "ALT": st.session_state.get('ALT'), "GLU": st.session_state.get('GLU')
    }

    st.markdown(f"""
        **Girdi Verileri:** WBC: `{kan_verileri['WBC']}`, HCT: `{kan_verileri['HCT']}`, BUN: `{kan_verileri['BUN']}`, CREA: `{kan_verileri['CREA']}`, ALT: `{kan_verileri['ALT']}`, GLU: `{kan_verileri['GLU']}`
    """)
    
    st.info("Derin Öğrenme Modeliniz bu verileri kullanarak tahmin yürütebilir. Şu an bu alan model entegrasyonu için ayrılmıştır.")
    st.metric(label="Anestezi Risk Tahmini (Model Sonucu)", value="[Model sonucu gelecek]", delta="[Tavsiye]", delta_color="off")
    
    st.markdown("---")

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
                    doz_set = PROTOKOL_DOZLAR[tur_secimi].get(ilac_adi, {}).get(ilac_yol, None)
                    
                    if doz_set is None:
                        yol_varsayilan = 'IV' if tip == 'İndüksiyon' else 'IM'
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
    if st.button("⬅️ Protokolü Tekrar Düzenle (2. Aşamaya Dön)", type="secondary", key="btn_prev_p3"):
        go_to_page(2)


# --- 6. ANA UYGULAMA MANTIĞI ---

render_header()
render_chatbot()

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
