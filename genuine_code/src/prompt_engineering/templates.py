from faker import Faker

def get_bank_policy_text():
    if Faker:
        fake = Faker('tr_TR')
        city = fake.city()
        address = fake.address()
        phone = fake.phone_number()
    else:
        city = "İzmir"
        address = "Buca, İzmir"
        phone = "+90 (222) 222 22 22"

    return f"""
    Genuine Bankacılık Hizmetleri
    
    Genel Bilgiler:
    Bankamız {city} merkezli olup, Türkiye genelinde hizmet vermektedir.
    Adresimiz: {address}.
    
    Mevduat Faiz Oranları:
    - 32 Günlük Vadeli Mevduat: %45
    - 90 Günlük Vadeli Mevduat: %47
    
    Kredi Kartı Ücretleri:
    - Standart Kart: Ücretsiz
    - Gold Kart: Yıllık 500 TL
    
    İletişim:
    Bize {phone} numarasından ulaşabilirsiniz.
    """

def get_rag_system_prompt(tone_instruction, literacy_note, context, user_query):
    return f"""
    Sen dijital bankacılık asistanısın. Görevin, aşağıda verilen bilgilerdeki bağlamı kullanarak kullanıcının sorusunu resmi bir şekilde cevaplamaktır. 
    
    [TALİMATLAR]:
    - {tone_instruction}
    - {literacy_note}
    - ÖNCELİKLE verilen [BAĞLAM] bilgisini kullan.
    - Eğer bağlamda bilgi yoksa ve soru genel finansal bilgi (örneğin "Faiz nedir?", "EFT nedir?") ise, kendi genel bilgini kullanarak cevapla.
    - Ancak banka politikaları (örneğin "Kredi faiz oranınız kaç?") soruluyorsa ve bağlamda yoksa "Güncel oranlar için şubemize başvurmalısınız." de.
    - Cevabın doğal, yardımsever ve akıcı olsun.
    
    [BAĞLAM]:
    {context}
    
    [KULLANICI SORUSU]:
    {user_query}
    """

