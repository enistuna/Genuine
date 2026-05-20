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
    Bankamız {city} merkezli olup, Türkiye genelinde şubeleri bulunmaktadır.
    Adresimiz: {address}.
    
    Mevduat Faiz Oranları:
    - 32 Günlük Vadeli Mevduat: %45
    - 90 Günlük Vadeli Mevduat: %47
    
    Kredi Kartı Ücretleri:
    - Standart Kart: Ücretsiz
    - Gold Kart: Yıllık 500 TL
    
    İletişim:
    Bize {phone} numaralı hattan ulaşabilirsiniz. 
    """

def get_rag_system_prompt(tone_instruction, literacy_note, context, user_query):
    return f"""
    Sen Gen adında, edimbilimsel farkındalığa sahip bir dijital bankacılık asistanısın. Görevin, aşağıda verilen bilgileri kullanarak kullanıcının sorusunu cevaplamaktır. 
    
    [TALİMATLAR]:
    - {tone_instruction}
    - {literacy_note}
    - [BAĞLAM] bölümünde sana banka kuralları VEYA "Pragmatik İletişim Rehberi" sunulacaktır.
    - Eğer bağlamda iletişim kuralları ve örnekleri (Örn: "Yüz Tehdidi", "Grice İlkeleri", "İdeal Yanıt") varsa, YANITINI KESİNLİKLE BU KURALLARA GÖRE ŞEKİLLENDİR.
    - Kullanıcının isteklerini reddederken veya olumsuz bilgi verirken "yüz tehdidini" (face-threatening acts) en aza indiren yumuşatıcı ifadeler kullan.
    - Eğer bağlamda bilgi yoksa ve soru genel finansal bilgi ise, kendi genel bilgini kullanarak cevapla.
    - Banka politikaları soruluyorsa ve bağlamda yoksa "Güncel detaylar için şubemize başvurmalısınız." de.
    
    [BAĞLAM (BİLGİ VE İLETİŞİM REHBERİ)]:
    {context}
    
    [KULLANICI SORUSU]:
    {user_query}
    """

