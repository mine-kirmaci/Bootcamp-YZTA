from openai import OpenAI

def get_medical_advice(report_text: str, api_key: str) -> str:
    """
    Verilen rapor metnini kullanarak OpenAI'dan tıbbi tavsiye ve beslenme programı alır.

    Args:
        report_text (str): Doktor raporu veya tahlil sonucu metni.
        api_key (str): OpenAI API anahtarı.

    Returns:
        str: OpenAI'dan gelen sadeleştirilmiş rapor, sağlık tavsiyeleri ve beslenme programı.
    """
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Her tavsiyende lütfen satırbaşı yaparak metin oluştur.
    Aşağıdaki doktor raporunu halkın kolayca anlayacağı şekilde sadeleştir.
    Ayrıca sağlık tavsiyelerini 3 ile 5 arasında olmak üzere maddeler halinde ver.
    Kullanıcıya sağlık sorununu gidermek için örnek bir beslenme listesi de oluşturmalısın.
    Ayrıca beslenme listesini neden oluşturduğunu, ne işe yaradığını birkaç cümle ile açıklamalısın.

    Rapor:
    {report_text}

    Cevap:
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen bir kişisel sağlık asistanısın."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
