import streamlit as st
from PIL import Image
import os
from datetime import datetime
from config import OPENAI_API_KEY, reports_collection
from ocr_service import extract_text_from_image
from openai_service import get_medical_advice
from auth import authenticate_user, register_user

# 🎨 Stil ve tema ayarı
st.set_page_config(page_title="Mediclear", layout="centered")

# Arka plan rengi ve başlık düzeni (Streamlit'in native CSS özelliğiyle sınırlı)
st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    h1, h2, h3 {
        color: #0a6d91;
    }
    .stButton>button {
        background-color: #0a6d91;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Görsel klasörü
UPLOAD_FOLDER = "uploaded_reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def login_section():
    st.title("🩺 **Mediclear Giriş Paneli**")

    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "🆕 Kayıt Ol"])

    with tab1:
        st.info("Lütfen e-posta ve şifrenizi girin.")
        email = st.text_input("📧 E-posta", key="login_email")
        password = st.text_input("🔒 Şifre", type="password", key="login_password")
        if st.button("Giriş Yap", key="login_button"):
            if authenticate_user(email, password):
                st.session_state["user"] = email
                st.success(f"👋 Hoş geldin **{email}**!")
                st.rerun()
            else:
                st.error("E-posta veya şifre hatalı.")

    with tab2:
        st.subheader("📝 Yeni Hesap Oluştur")
        email_new = st.text_input("📧 E-posta", key="register_email")
        pass1 = st.text_input("🔐 Şifre", type="password", key="register_pass1")
        pass2 = st.text_input("🔐 Şifre Tekrar", type="password", key="register_pass2")

        name = st.text_input("👤 Ad Soyad", key="name")
        age = st.number_input("🎂 Yaş", min_value=0, max_value=120, key="age")
        gender = st.selectbox("🚻 Cinsiyet", ["Kadın", "Erkek", "Diğer"], key="gender")
        weight = st.number_input("⚖️ Kilo (kg)", min_value=0, key="weight")
        medications = st.text_area("💊 Kullandığınız ilaçlar (virgül ile ayırın)", key="medications")
        allergies = st.text_area("🌿 Alerjileriniz (virgül ile ayırın)", key="allergies")
        medical_history = st.text_area("🏥 Geçirdiğiniz hastalık/ameliyatlar", key="history")

        with st.expander("📄 Kullanım Koşullarını Oku"):
            st.markdown("""
            **Mediclear Kullanım Koşulları**
            - Uygulama bilgilendirme amaçlıdır, tıbbi teşhis yerine geçmez.
            - Veriler analiz/geliştirme amaçlı saklanabilir.
            - Gizliliğiniz korunur ve 3. kişilerle paylaşılmaz.
            """)

        agree = st.checkbox("Kullanım koşullarını kabul ediyorum", key="register_checkbox")

        if st.button("Kayıt Ol", key="register_button"):
            if not agree:
                st.warning("Lütfen kullanım koşullarını kabul edin.")
            elif pass1 != pass2:
                st.error("Şifreler uyuşmuyor.")
            else:
                profile = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "weight": weight,
                    "medications": [med.strip() for med in medications.split(",") if med.strip()],
                    "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                    "medical_history": medical_history
                }
                if register_user(email_new, pass1, profile):
                    st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                else:
                    st.error("Bu e-posta zaten kayıtlı.")


def medical_analysis():
    st.title("📋 Sağlık Raporu Analizi")

    st.write("""
    💡 **Mediclear**, yüklediğiniz doktor raporunu analiz eder, sadeleştirir ve size özel sağlık önerileri sunar.
    """)

    uploaded_file = st.file_uploader("📄 Raporunuzu yükleyin (jpg, png, jpeg)", type=["jpg", "png", "jpeg"])
    text_input = st.text_area("✍️ Veya raporu buraya yapıştırın")

    if st.button("🔍 Analizi Başlat"):
        if not text_input and not uploaded_file:
            st.error("Lütfen bir rapor yazın ya da görsel yükleyin.")
            return

        image_filename = None
        if uploaded_file:
            image = Image.open(uploaded_file)
            text = extract_text_from_image(image)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_filename = f"{st.session_state['user']}_{timestamp}.png"
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))
        else:
            text = text_input

        if text.strip() == "":
            st.error("Boş metin algılandı.")
            return

        with st.spinner("🧠 Yapay zekâ analiz ediyor..."):
            output = get_medical_advice(text, OPENAI_API_KEY)

        st.success("✅ İşte analiz sonucu:")
        st.markdown(f"""
        <div style="background-color:#e8f0fe; padding: 15px; border-radius: 10px; border: 1px solid #0a6d91;">
        {output}
        </div>
        """, unsafe_allow_html=True)

        reports_collection.insert_one({
            "user": st.session_state["user"],
            "original_text": text,
            "ai_response": output,
            "uploaded_filename": image_filename,
            "created_at": datetime.utcnow()
        })


def main():
    if "user" not in st.session_state:
        login_section()
    else:
        medical_analysis()

if __name__ == "__main__":
    main()
