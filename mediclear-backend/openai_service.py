import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def get_report_title(text: str) -> str:
    prompt = f"Aşağıdaki tıbbi rapora uygun kısa ve anlamlı bir başlık öner (örnek: 'Kan Tahlili', 'MR Sonucu', 'D Vitamini Eksikliği'):\n\n{text}\n\nBaşlık:"
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Başlık oluşturulamadı] {e}")
        return "Başlıksız Rapor"

def get_medical_advice(report_text: str, user_profile: dict = None) -> str:
    profile_info = ""
    if user_profile:
        profile_info += "\n👤 Hasta Profili:\n"
        profile_info += f"- Ad Soyad: {user_profile.get('name', 'Bilinmiyor')}\n"
        profile_info += f"- Yaş: {user_profile.get('age', 'Bilinmiyor')}\n"
        profile_info += f"- Cinsiyet: {user_profile.get('gender', 'Bilinmiyor')}\n"
        profile_info += f"- Kilo: {user_profile.get('weight', 'Bilinmiyor')} kg\n"

        medications = user_profile.get("medications", ["belirtilmemiş"])
        allergies = user_profile.get("allergies", ["belirtilmemiş"])
        medical_history = user_profile.get("medical_history", "belirtilmemiş")

        profile_info += f"- Kullandığı ilaçlar: {', '.join(medications) if medications else 'yok'}\n"
        profile_info += f"- Alerjiler: {', '.join(allergies) if allergies else 'yok'}\n"
        profile_info += f"- Geçirdiği hastalık/ameliyatlar: {medical_history if medical_history else 'yok'}\n"

    full_prompt = f"""
🩺 Aşağıda bir hasta raporu var. Lütfen bu metni halkın kolayca anlayabileceği bir şekilde sadeleştir.

🌟 Şu adımları dikkatlice takip et:
1. Raporun hangi tetkike (örneğin MR, ultrason, kan tahlili vb.) ait olduğunu anlamaya çalış. Hangi organ ya da sistemi incelediğini belirt. Rapor tarihine dair bilgi varsa bunu da ekle. 
   Ardından raporun detaylarında neler söylendiğini adım adım ve sade bir şekilde açıkla. Özellikle geçen tıbbi bulguların ne anlama geldiğini halka açık dille anlat. "Bulgu yok" gibi ifadeleri bile detaylıca sadeleştir.
2. Kullanıcının yaş, kilo, cinsiyet, hastalık geçmişi, alerjileri ve ilaç bilgilerine göre 3-5 basit ve uygulanabilir sağlık önerisi ver. 
   ❗ Bu öneriler herkesin günlük yaşamda kolayca uygulayabileceği şeyler olsun. Örneğin:
   - “Omega 3 alın” yerine “haftada 2 kez balık tüketin (örneğin somon, sardalya gibi)”
   - “Antioksidan alın” yerine “her gün 1 avuç ceviz ya da yaban mersini tüketin” gibi öneriler ver.
3. Yukarıdaki bilgilere dayanarak örnek bir günlük beslenme listesi hazırla. Liste pratik ve marketten kolayca temin edilebilecek besinlerden oluşsun.
4. ❗ Verdiğin besin ve sağlık önerilerinde erişilebilirliğe dikkat et. Eğer önerdiğin bir yiyecek pahalıysa ya da bulunması zorsa, onun için alternatif seçenek de sun:
   - Örneğin "somon" öneriyorsan yanına "ton balığı veya uskumru gibi daha uygun fiyatlı alternatifler de olabilir" diye belirt.
   - “Avokado tüketin” yerine “zeytinyağı veya ceviz gibi omega 3 içeren besinlerle de destekleyebilirsiniz” şeklinde açıkla.
   Amaç: Her gelir düzeyine ve alışveriş imkânına uygun, pratik ve anlaşılır öneriler ver.
5. Eğer bazı bilgiler eksikse (örneğin ilaç adı, D vitamini dozu), "Şu bilgi eksik olabilir" gibi kibar bir not düş, ama yine de açıklamayı sürdür.
6. Tıbbi terimleri halk diline çevirerek açıkla. Karmaşık veya korkutucu ifadeler kullanma. Anlatım tarzın sıcak, öğretici ve moral verici olsun.

📄 Hasta Raporu:
{report_text}

{profile_info}

🧠 Cevap:
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen deneyimli bir doktorsun. Karşında medikal geçmişi sınırlı olan bir hasta var. "
                        "Amacın, hastanın sunduğu tıbbi raporu dikkatlice yorumlayarak ona sade, anlaşılır ve moral verici bir şekilde açıklamak. "
                        "Tıbbi terimleri halk diline çevir, karmaşıklığı azalt. Hastanın endişelenmesini engelle, ama aynı zamanda bilinçli olmasını sağla. "
                        "Yorumlarında bir hekimin güven veren ses tonunu koru; gerektiğinde öneriler ver, ama asla korkutma ya da panik yaratma. "
                        "Kısacası; doktor-hasta ilişkisinde güven, açıklık ve anlayış ön planda olsun."
                    )
                },
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Yapay zekâ analizinde bir hata oluştu:\n\n{str(e)}"

def get_followup_advice(question: str, report_text: str = "", user_profile: dict = None) -> str:
    name = user_profile.get("name", "Değerli kullanıcı") if user_profile else "Değerli kullanıcı"

    profile_info = ""
    if user_profile:
        profile_info += f"- Ad: {name}\n"
        profile_info += f"- Yaş: {user_profile.get('age', 'Bilinmiyor')}\n"
        profile_info += f"- Cinsiyet: {user_profile.get('gender', 'Bilinmiyor')}\n"
        profile_info += f"- Kilo: {user_profile.get('weight', 'Bilinmiyor')} kg\n"
        profile_info += f"- Hastalık Geçmişi: {user_profile.get('medical_history', 'belirtilmemiş')}\n"
        profile_info += f"- İlaçlar: {', '.join(user_profile.get('medications', [])) or 'belirtilmemiş'}\n"
        profile_info += f"- Alerjiler: {', '.join(user_profile.get('allergies', [])) or 'belirtilmemiş'}\n"

    prompt = f"""
Kullanıcıdan gelen bir takip sorusu var. Lütfen bu soruya doğrudan ve kişisel bir şekilde yanıt ver.

1. İlk olarak {name} adına bir selamla ve onun yaş, cinsiyet, kilo ve geçmiş sağlık bilgilerine göre kısa bir değerlendirme yap.
2. Soruyu doğrudan ve sade bir dille yanıtla.
3. Eğer uygunsa, kullanıcının bilgilerine uygun olarak günlük bir egzersiz rutini öner. 
   Örneğin:
   - "Sabah: 15 dakika yürüyüş"
   - "Öğle: 5 dakikalık esneme hareketleri"
   - "Akşam: hafif tempolu 20 dakika ev içi egzersiz"
4. Önerilerin erişilebilir, düşük maliyetli ve uygulanabilir olmasına dikkat et.
5. Gerekirse önerdiğin yiyecek/egzersiz için uygun alternatifler sun.

❓ Soru:
{question}

🧾 Rapor özeti (isteğe bağlı):
{report_text[:300] + "..." if report_text else "—"}

👤 Profil bilgileri:
{profile_info}

Yanıtın hem bilgilendirici hem de moral verici olmalı. Samimi bir doktor-hasta iletişimi kurmaya dikkat et.
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen deneyimli bir sağlık danışmanısın. Kullanıcının sorduğu soruya kişisel, sade, ulaşılabilir ve moral verici bir şekilde yanıt ver. "
                        "Eğer uygunsa kısa bir günlük egzersiz planı da öner. Lüks öneriler yerine günlük hayatta herkesin uygulayabileceği alternatifler kullan."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Yanıt alınamadı: {e}"

