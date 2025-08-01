import os
from datetime import datetime
from PIL import Image
import streamlit as st
from config import reports_collection, users_collection
from ocr_service import extract_text_from_image
from openai_service import get_medical_advice, get_report_title
from auth import authenticate_user, register_user
from gtts import gTTS
import uuid
import os
import pygame 
# global ses süreci referansı
voice_process = None


st.set_page_config(page_title="Mediclear - Sağlık Asistanı", page_icon="🩺", layout="wide")

st.markdown('<div class="app-header">🩺 Mediclear</div>', unsafe_allow_html=True)

# CSS Güncellemesi
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(to right, #95D5F5FF, #f1f8e9);
    font-family: 'Helvetica Neue', sans-serif;
}

/* Başlık */
.app-header {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    margin-top: 30px;
    color: #0077b6;
    padding: 10px;
    border-bottom: 2px solid #caf0f8;
}

/* Kapsayıcı alan */
.main-container {
    display: flex;
    justify-content: center;
    margin-top: 40px;
    padding: 20px 30px;
}

/* Sadece sol panel */
.left-panel {
    width: 100%;
    max-width: 600px;
}

/* Input ve textarea */
input, textarea {
    font-size: 15px !important;
    padding: 12px !important;
    border-radius: 8px !important;
}

/* Butonlar */
.stButton>button {
    background-color: #0077b6;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 13px 0;
    font-size: 16px;
    font-weight: bold;
    width: 100%;
    margin-top: 20px;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    background-color: #0096c7;
}

/* Sekmeler */
div[data-baseweb="tab"] button {
    color: #888 !important;
    font-weight: 600;
    font-size: 16px;
    background-color: transparent;
    border: none;
}
div[data-baseweb="tab"] button[aria-selected="true"] {
    color: #0077b6 !important;
    border-bottom: 3px solid #0077b6 !important;
}

/* Etiketler */
label {
    color: #222 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
    display: block;
}
</style>
""", unsafe_allow_html=True)

# Yalnızca sol panel render ediliyor (sağ panel kaldırıldı)
st.markdown("""
<div class="main-container">
    <div class="left-panel">
        <!-- Form burada render edilecek -->
    </div>
</div>
""", unsafe_allow_html=True)




UPLOAD_FOLDER = "uploaded_reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# pygame mixer başlatmak için flag
is_audio_initialized = False

def play_ai_voice(text, lang='tr'):
    global voice_process, is_audio_initialized
    try:
        filename = f"voice_{uuid.uuid4()}.mp3"
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)

        # pygame mixer başlat
        if not is_audio_initialized:
            pygame.mixer.init()
            is_audio_initialized = True

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        st.session_state["voice_file"] = filename
        voice_process = True  # sadece oynatılıyor bilgisini tut

    except Exception as e:
        print(f"Sesli okuma başarısız: {e}")

def stop_ai_voice():
    global voice_process
    try:
        # Eğer mixer başlatıldıysa durdurmaya çalış
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.quit()  # mixer'ı tamamen kapat
            print("Ses durduruldu ve mixer kapatıldı.")
        else:
            print("Mixer başlatılmamış ya da ses çalmıyor.")

        voice_process = None

        # Varsa geçici mp3 dosyasını sil
        if "voice_file" in st.session_state:
            try:
                os.remove(st.session_state["voice_file"])
                del st.session_state["voice_file"]
                print("Geçici ses dosyası silindi.")
            except Exception as e:
                print(f"Dosya silme hatası: {e}")

    except Exception as e:
        print(f"Ses durdurulamadı: {e}")


# Session temizleme
def clear_session():
    keys_to_keep = ["user", "page", "start_new_chat"]
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

# Giriş/kayıt ekranı
def login_section():
    col1, col2 = st.columns([1, 1])

    with col1:
        tab1, tab2 = st.tabs(["🔐 Giriş Yap", "🆕 Kayıt Ol"])

        with tab1:
            email = st.text_input("📧 E-posta", key="login_email")
            password = st.text_input("🔒 Şifre", type="password", key="login_password")
            login_btn = st.button("Giriş Yap", key="login_btn")
            if login_btn:
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
            weight = st.number_input("⚖️ Kilo (kg)", 0, 300, key="reg_weight")
            medications = st.text_area("💊 Kullandığınız ilaçlar (virgülle ayırın)", key="reg_medications")
            allergies = st.text_area("🌿 Alerjileriniz (virgülle ayırın)", key="reg_allergies")
            history = st.text_input("📝 Geçmiş hastalıklar", key="reg_history")

            register_btn = st.button("Kayıt Ol", key="register_btn")
            if register_btn:
                if pass1 != pass2:
                    st.error("Şifreler eşleşmiyor.")
                else:
                    user_data = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "weight": weight,
                        "medications": [m.strip() for m in medications.split(",") if m.strip()],
                        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
                        "medical_history": history
                    }
                    if register_user(email_new, pass1, user_data):
                        st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
                        st.rerun()
                    else:
                        st.error("Bu e-posta zaten kayıtlı.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="right-panel">', unsafe_allow_html=True)
        st.image("uploaded/VOTE_mediclear_right.png", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# Ana sayfa: rapor seçimi ve yükleme
def dashboard():
    st.sidebar.title("📁 Menü")

    if st.sidebar.button("🆕 Yeni Sohbet Başlat", key="new_chat_sidebar"):
        clear_session()
        st.session_state["start_new_chat"] = True
        st.session_state["page"] = "dashboard"
        st.rerun()

    st.title("📋 Sağlık Raporu Analizi")
    st.sidebar.markdown("### 📜 Önceki Raporlar")

    user_reports = list(reports_collection.find({"user": st.session_state["user"]}).sort("created_at", -1))
    selected_report = None

    if user_reports:
        # Yeni başlık oluşturmayı sidebar’a da yansıt
        titles = []
        for r in user_reports:
            if not r.get("report_title") or r["report_title"] == "Başlıksız Rapor":
                generated_title = get_report_title(r["original_text"])
                titles.append(f"{generated_title} ({r['created_at'].strftime('%d.%m.%Y %H:%M')})")
                r["report_title"] = generated_title  # title to match during selection
            else:
                titles.append(f"{r['report_title']} ({r['created_at'].strftime('%d.%m.%Y %H:%M')})")

        selected = st.sidebar.radio("📑 Rapor Seç", titles, key="sidebar_report_selection")

        selected_report = next(
            (r for r in user_reports if f"{r['report_title']} ({r['created_at'].strftime('%d.%m.%Y %H:%M')})" == selected),
            None
        )
    else:
        st.sidebar.info("Herhangi bir rapor bulunamadı.")

    if selected_report and st.session_state.get("page") == "dashboard" and not st.session_state.get("start_new_chat", False):
        st.session_state["start_new_chat"] = False # önceki raporu açarken yeni yükleme modu kapansın
        st.session_state["page"] = "dashboard"

        title_to_display = selected_report.get("report_title", "Başlıksız Rapor")
        st.markdown(f"### 📝 Rapor: {title_to_display}")

        if selected_report.get("uploaded_filename"):
            path = os.path.join(UPLOAD_FOLDER, selected_report["uploaded_filename"])
            if os.path.exists(path):
                st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
                st.image(path, caption="🖼️ Yüklenen Rapor", width=350)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Orijinal Metin:**\n\n{selected_report.get('original_text', '')}")

        st.markdown(f"**🧠 AI Açıklaması:**\n\n{selected_report.get('ai_response', 'Yok')}")


        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔊 AI Açıklamasını Sesli Dinle", key="play_voice_btn"):
                play_ai_voice(selected_report.get("ai_response", "Sesli içerik bulunamadı."))
        with col2:
            if st.button("🔈 Sesi Durdur", key="stop_voice_btn"):
                stop_ai_voice()

        # AI'ya soru sor özelliği
        with st.expander("❓ Bu raporla ilgili bir soru sorun"):
            user_q = st.text_input("Sorunuzu yazın", key="user_followup_question")
            if st.button("Yanıt Al", key="ask_followup_btn"):
                with st.spinner("AI yanıtlıyor..."):
                    from openai_service import get_medical_advice  # varsa yukarıya alma
                    user_doc = users_collection.find_one({"email": st.session_state['user']})
                    profile = user_doc.get("profile") if user_doc else None

                    followup_response = get_medical_advice(
                        f"Rapor metni: {selected_report.get('original_text', '')}\n\n"
                        f"Soru: {user_q}",
                        user_profile=profile
                    )
                    st.markdown(f"**🗣️ AI'nin Yanıtı:**\n\n{followup_response}")


    if st.session_state.get("start_new_chat", False):
        st.markdown("### 📤 Yeni Rapor Yükle")
        title = st.text_input("📌 Rapor Başlığı", max_chars=100, key="new_title")
        file = st.file_uploader("📄 Görsel Rapor", type=["jpg", "jpeg", "png"], key="new_file")
        text_input = st.text_area("✍️ Metni yapıştır", key="new_text")

        if st.button("🔍 Analizi Başlat", key="analyze_btn"):
            if not file and not text_input:
                st.error("Lütfen görsel yükleyin veya metin girin.")
                return

            filename = None
            if file:
                image = Image.open(file)
                ext = file.name.split(".")[-1]
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{st.session_state['user']}_{ts}.{ext}"
                image.save(os.path.join(UPLOAD_FOLDER, filename))
                text = extract_text_from_image(image)
            else:
                text = text_input

            if not text.strip():
                st.error("Boş içerik algılandı.")
                return

            report_title = title.strip()
            if not report_title:
                with st.spinner("🧠 Başlık üretiliyor..."):
                    report_title = get_report_title(text)
                if not report_title:
                    report_title = "Başlıksız Rapor"

            user_doc = users_collection.find_one({"email": st.session_state["user"]})
            profile = user_doc.get("profile") if user_doc else None

            with st.spinner("🧠 Yapay zekâ analiz ediyor..."):
                result = get_medical_advice(text, user_profile=profile)

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

