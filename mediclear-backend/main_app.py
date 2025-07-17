import streamlit as st
from PIL import Image
import io

from config import OPENAI_API_KEY
from ocr_service import extract_text_from_image
from openai_service import get_medical_advice

def main():
    st.title("🩺 Mediclear")

    st.write("Mediclear, kişisel sağlık asistanınız olarak, doktor raporlarınızı ve tahlil sonuçlarınızı sizin için inceler. " \
    "Sağlık bilgilerinizi basit ve anlaşılır bir dile çevirerek, her bilginin ne anlama geldiğini kolayca kavramanıza yardımcı olur. " \
    "Ayrıca, tahlil veya doktor raporunuza göre kişiye özel sağlık tavsiyelerinde ve beslenme programı önerilerinde bulunur.")

    uploaded_file = st.file_uploader("📄 Rapor veya tahlil sonucu fotoğrafı yükleyin (jpg, png, jpeg)", type=["jpg", "png", "jpeg"])
    text_input = st.text_area("✍️ Ya da raporunuzu buraya yazın")

    if st.button("🩺 Mediclear"):
        if not text_input and not uploaded_file:
            st.error("Lütfen metin girin ya da fotoğraf yükleyin.")
        else:
            text = ""
            if uploaded_file:
                image = Image.open(uploaded_file)
                text = extract_text_from_image(image)
            else:
                text = text_input

            if text:
                with st.spinner("Rapor çözümleniyor..."):
                    output = get_medical_advice(text, OPENAI_API_KEY)
                st.success("✅ İşte sonuç:")
                st.write(output)
            else:
                st.error("Görüntüden metin çıkarılamadı veya boş metin girildi.")

if __name__ == "__main__":
    main()