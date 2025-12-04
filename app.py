import streamlit as st
import math

# --- 1. KAPSAMLI HESAPLAMA FONKSİYONU ---
def veteriner_anestezi_hesaplayici(vucut_agirligi_kg, tur):
    """
    Veteriner anestezi için ilaç dozu ve sıvı idame hesaplamalarını yapar.
    """
    
    if vucut_agirligi_kg <= 0:
        return {"Hata": "Vücut ağırlığı pozitif bir değer olmalıdır."}

    # İlaç Protokolleri ( mg/kg )
    KETAMIN_DOZAJ = 5.0      
    MIDAZOLAM_DOZAJ = 0.3    
    
    # İlaç Konsantrasyonları ( mg/mL )
    KETAMIN_KONSANTRASYON = 100.0 
    MIDAZOLAM_KONSANTRASYON = 5.0   
    
    SIVI_IDAME_HIZI = 10.0 # mL/kg/saat
    MIKRO_SET_FAKTORU = 60 # damla/mL

    sonuclar = {}
    
    # --- İlaç Dozu Hesaplamaları ---
    ketamin_toplam_doz_mg = vucut_agirligi_kg * KETAMIN_DOZAJ
    ketamin_hacim_ml = ketamin_toplam_doz_mg / KETAMIN_KONSANTRASYON
    
    midazolam_toplam_doz_mg = vucut_agirligi_kg * MIDAZOLAM_DOZAJ
    midazolam_hacim_ml = midazolam_toplam_doz_mg / MIDAZOLAM_KONSANTRASYON
    
    toplam_enjeksiyon_hacmi_ml = ketamin_hacim_ml + midazolam_hacim_ml
    
    sonuclar["İlaç Dozları"] = {
        "Ketamin (mg)": f"{ketamin_toplam_doz_mg:.2f} mg",
        "Ketamin (mL)": f"{ketamin_hacim_ml:.3f} mL",
        "Midazolam (mg)": f"{midazolam_toplam_doz_mg:.2f} mg",
        "Midazolam (mL)": f"{midazolam_hacim_ml:.3f} mL",
        "Toplam Enjeksiyon Hacmi": f"{toplam_enjeksiyon_hacmi_ml:.3f} mL"
    }
    
    # --- Sıvı ve Damla Hızı Hesaplamaları ---
    saatlik_sivi_ihtiyaci_ml_saat = vucut_agirligi_kg * SIVI_IDAME_HIZI
    dakikalik_sivi_ihtiyaci_ml_dakika = saatlik_sivi_ihtiyaci_ml_saat / 60.0
    damla_hizi_mikro_damla_dakika = dakikalik_sivi_ihtiyaci_ml_dakika * MIKRO_SET_FAKTORU
    
    sonuclar["Sıvı İdame"] = {
        "Protokol Hızı": f"{SIVI_IDAME_HIZI} mL/kg/saat",
        "Saatlik İnfüzyon Hızı (Pompada Ayar)": f"{saatlik_sivi_ihtiyaci_ml_saat:.2f} mL/saat",
        "Dakikalık İnfüzyon Hızı": f"{dakikalik_sivi_ihtiyaci_ml_dakika:.2f} mL/dakika",
        "Damla Hızı (Mikro Set)": f"{round(damla_hizi_mikro_damla_dakika):d} damla/dakika"
    }

    return sonuclar

# --- 2. STREAMLIT ARAYÜZ KISMI ---

st.set_page_config(page_title="Veteriner Anestezi Hesaplayıcı", layout="centered")
st.title("🐶🐱 Veteriner Anestezi ve Sıvı Hesaplayıcı")
st.markdown("---")

# Kullanıcı Girişleri
st.header("1. Giriş Bilgileri")
tur_secimi = st.radio("Hayvan Türü Seçin:", ('Köpek', 'Kedi'), help="Dozajlar bu türler için standart kabul edilmiştir.")
vucut_agirligi = st.number_input("Vücut Ağırlığı (kg):", min_value=0.1, value=5.0, step=0.1, format="%.1f", help="Hayvanın tam vücut ağırlığını girin.")

# Hesaplama butonu
if st.button("HESAPLA", type="primary"):
    tur_kodu = tur_secimi.lower().replace('ö', 'o').replace('ü', 'u') 
    sonuclar = veteriner_anestezi_hesaplayici(vucut_agirligi, tur_kodu)

    if "Hata" in sonuclar:
        st.error(f"HATA: {sonuclar['Hata']}")
    else:
        st.success(f"Hesaplamalar {vucut_agirligi} kg'lık bir {tur_secimi} için yapılmıştır.")
        st.markdown("---")

        # İlaç Sonuçları
        st.header("2. 💉 İndüksiyon Dozu (Ketamin/Midazolam)")
        st.info("Kullanılan Protokol: Ketamin 5 mg/kg (100 mg/mL) ve Midazolam 0.3 mg/kg (5 mg/mL).")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Ketamin")
            st.metric(label="Toplam Doz", value=sonuclar["İlaç Dozları"]["Ketamin (mg)"])
            st.metric(label="Çekilecek Hacim", value=sonuclar["İlaç Dozları"]["Ketamin (mL)"], help="100 mg/mL konsantrasyon için")
        
        with col2:
            st.subheader("Midazolam")
            st.metric(label="Toplam Doz", value=sonuclar["İlaç Dozları"]["Midazolam (mg)"])
            st.metric(label="Çekilecek Hacim", value=sonuclar["İlaç Dozları"]["Midazolam (mL)"], help="5 mg/mL konsantrasyon için")
            
        st.markdown("<h3 style='text-align: center; color: green;'>Toplam Enjeksiyon Hacmi:</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; color: green;'>{sonuclar['İlaç Dozları']['Toplam Enjeksiyon Hacmi']}</h1>", unsafe_allow_html=True)


        st.markdown("---")

        # Sıvı İdame Sonuçları
        st.header("3. 💧 Sıvı İdame Hesaplamaları")
        st.info("Kullanılan Protokol: Anestezi idamesi için 10 mL/kg/saat.")
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Saatlik İnfüzyon Hızı", value=sonuclar["Sıvı İdame"]["Saatlik İnfüzyon Hızı (Pompada Ayar)"])
        
        with col4:
            st.metric(label="Damla Hızı (Mikro Set)", value=sonuclar["Sıvı İdame"]["Damla Hızı (Mikro Set)"])


# Sorumluluk Reddi (Etik ve Yasal gereklilik)
st.markdown("---")
st.caption("🚨 **UYARI:** Bu araç yalnızca eğitim ve destek amaçlıdır. Nihai teşhis ve doz ayarlamaları her zaman bir **Veteriner Hekim** tarafından yapılmalıdır. Veriler standart protokollere dayanmaktadır.")