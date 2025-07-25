import streamlit as st
from PIL import Image
import os
from datetime import datetime
from config import reports_collection, users_collection
from ocr_service import extract_text_from_image
from openai_service import get_medical_advice
from auth import authenticate_user, register_user

# Sayfa başlığı ve tema
st.set_page_config(page_title="Mediclear", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    h1, h2, h3 { color: #0a6d91; }
    .stButton>button {
        background-color: #0a6d91; color: white; border-radius: 8px; padding: 10px 20px;
    }
    textarea { background-color: #ffffff !important; border-radius: 6px; color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

UPLOAD_FOLDER = "uploaded_reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Session temizleme
def clear_session():
    keys_to_keep = ["user", "page", "start_new_chat"]
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

# Giriş/kayıt ekranı
def login_section():
    st.title("🩺 Mediclear Giriş Paneli")
    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "🆕 Kayıt Ol"])

    with tab1:
        email = st.text_input("📧 E-posta", key="login_email")
        password = st.text_input("🔒 Şifre", type="password", key="login_password")
        if st.button("Giriş Yap", key="login_btn"):
            if authenticate_user(email, password):
                st.session_state["user"] = email
                st.session_state["page"] = "dashboard"
                st.rerun()
            else:
                st.error("Hatalı giriş.")

    with tab2:
        email_new = st.text_input("📧 E-posta", key="register_email")
        pass1 = st.text_input("🔐 Şifre", type="password", key="pass1")
        pass2 = st.text_input("🔐 Şifre Tekrar", type="password", key="pass2")
        name = st.text_input("👤 Ad Soyad", key="reg_name")
        age = st.number_input("🎂 Yaş", 0, 120, key="reg_age")
        gender = st.selectbox("🚻 Cinsiyet", ["Kadın", "Erkek", "Diğer"], key="reg_gender")
        weight = st.number_input("⚖️ Kilo (kg)", 0, key="reg_weight")
        medications = st.text_area("💊 İlaçlar (virgülle)", key="reg_medications")
        allergies = st.text_area("🌿 Alerjiler (virgülle)", key="reg_allergies")
        history = st.text_area("🏥 Hastalık/Ameliyatlar", key="reg_history")
        agree = st.checkbox("Kullanım koşullarını kabul ediyorum", key="reg_agree")

        if st.button("Kayıt Ol", key="register_btn"):
            if not agree:
                st.warning("Koşulları kabul etmelisiniz.")
            elif pass1 != pass2:
                st.error("Şifreler eşleşmiyor.")
            else:
                profile = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "weight": weight,
                    "medications": [m.strip() for m in medications.split(",") if m.strip()] or ["yok"],
                    "allergies": [a.strip() for a in allergies.split(",") if a.strip()] or ["yok"],
                    "medical_history": history.strip() if history.strip() else "yok"
                }
                if register_user(email_new, pass1, profile):
                    st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                    st.rerun()
                else:
                    st.error("Bu e-posta zaten kayıtlı.")

# Ana sayfa: rapor seçimi ve yükleme
def dashboard():
    st.sidebar.title("📁 Menü")

    if st.sidebar.button("🆕 Yeni Sohbet Başlat", key="new_chat_sidebar"):
        clear_session()
        st.session_state["start_new_chat"] = True
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.title("📋 Sağlık Raporu Analizi")

    # Sidebar: Rapor başlıkları her zaman gösterilsin
    st.sidebar.markdown("### 📜 Önceki Raporlar")

    user_reports = list(reports_collection.find({"user": st.session_state["user"]}).sort("created_at", -1))

    selected_report = None
    if user_reports:
        titles = [
            f"{r.get('report_title', 'Başlıksız Rapor')} ({r['created_at'].strftime('%d.%m.%Y %H:%M')})"
            for r in user_reports
        ]
        selected = st.sidebar.radio("📑 Rapor Seç", titles, key="sidebar_report_selection")

        selected_report = next(
            r for r in user_reports
            if f"{r.get('report_title', 'Başlıksız Rapor')} ({r['created_at'].strftime('%d.%m.%Y %H:%M')})" == selected
        )
    else:
        st.sidebar.info("Herhangi bir rapor bulunamadı.")

    # Eğer yeni sohbet başlatılmadıysa ve bir rapor seçildiyse detaylarını göster
    if not st.session_state.get("start_new_chat", False) and selected_report:
        st.markdown(f"### 📝 Rapor: {selected_report.get('report_title', 'Başlıksız Rapor')}")
        if selected_report.get("uploaded_filename"):
            path = os.path.join(UPLOAD_FOLDER, selected_report["uploaded_filename"])
            if os.path.exists(path):
                st.image(path, caption="🖼️ Yüklenen Rapor", use_container_width=True)
        else:
            st.markdown(f"**Orijinal Metin:**\n\n{selected_report['original_text']}")

        st.markdown(f"**AI Açıklaması:**\n\n{selected_report['ai_response']}")

    # Eğer yeni sohbet başlatıldıysa yeni rapor yükleme alanını göster
    if st.session_state.get("start_new_chat", False):
        st.markdown("### 📤 Yeni Rapor Yükle")
        title = st.text_input("📌 Rapor Başlığı", max_chars=100, key="new_title")
        file = st.file_uploader("📄 Görsel Rapor", type=["jpg", "jpeg", "png"], key="new_file")
        text_input = st.text_area("✍️ Metni yapıştır", key="new_text")

    # Analiz başlatma tuşuna basınca:
    if st.button("🔍 Analizi Başlat", key="analyze_btn"):
        ...
        if not text.strip():
            st.error("Boş içerik algılandı.")
            return

        user_doc = users_collection.find_one({"email": st.session_state["user"]})
        profile = user_doc.get("profile") if user_doc else None

        with st.spinner("🧠 Yapay zekâ analiz ediyor..."):
            result = get_medical_advice(text, user_profile=profile)

            # Boşsa başlık üret
            report_title = title.strip() if title.strip() else get_report_title(text)

        reports_collection.insert_one({
            "user": st.session_state["user"],
            "report_title": report_title,
            "original_text": text,
            "ai_response": result,
            "uploaded_filename": filename,
            "created_at": datetime.utcnow()
        })


        st.session_state["ai_result"] = result
        st.session_state["start_new_chat"] = False
        st.session_state["page"] = "result"
        st.rerun()

# Sonuç sayfası
def result_page():
    st.title("✅ Analiz Sonucu")
    st.markdown(f"""
    <div style="background-color:#e8f0fe; padding: 15px; border-radius: 10px; border: 1px solid #0a6d91;">
    {st.session_state['ai_result']}
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔙 Anasayfaya Dön", key="back_to_dashboard"):
        st.session_state["page"] = "dashboard"
        st.rerun()

# Ana kontrol
def main():
    if "user" not in st.session_state:
        login_section()
    else:
        page = st.session_state.get("page", "dashboard")
        if page == "dashboard":
            dashboard()
        elif page == "result":
            result_page()

if __name__ == "__main__":
    main()
