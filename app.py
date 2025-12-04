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
# Yeni eklenen kan değerleri için başlangıç değerleri
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
            # st.number_input güncellenmiş değerleri doğrudan session_state'e kaydeder
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
    
    # Kan Tablosu Yüklendiyse/Girildiyse Ek Bilgi Gösterimi
    if st.session_state['uploaded_kan_tablosu'] or 'WBC' in st.session_state:
        st.warning(f"Kan verileri sisteme girildi ({st.session_state.get('WBC', '-')} WBC, {st.session_state.get('BUN', '-')}
