# openai_service.py
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_medical_advice(report_text: str, user_profile: dict = None) -> str:
    """
    Verilen rapor metni ve varsa kullanıcı profiline göre tıbbi öneriler döner.

    Args:
        report_text (str): Doktor raporu veya tahlil sonucu metni.
        user_profile (dict, optional): Kullanıcının yaşı, kilosu, hastalık geçmişi gibi bilgiler.

    Returns:
        str: OpenAI'dan gelen sadeleştirilmiş rapor, sağlık tavsiyeleri ve beslenme önerisi.
    """
    profile_info = ""
    if user_profile:
        profile_info = "\n\nKullanıcı Profili:\n"
        for key, value in user_profile.items():
            profile_info += f"- {key.capitalize()}: {value}\n"

    prompt = f"""
    Aşağıdaki doktor raporunu herkesin anlayabileceği şekilde sadeleştir.
    Ayrıca sağlık tavsiyelerini (3-5 madde) açıkla ve kullanıcıya uygun bir günlük beslenme planı sun.
    Beslenme planının amacını birkaç cümleyle belirt.

    Rapor:
    {report_text}
    {profile_info}

    Cevap:
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen kişisel sağlık danışmanı olarak görev yapıyorsun."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Hata: {str(e)}"
