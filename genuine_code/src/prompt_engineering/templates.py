from faker import Faker
import os
import json

_grammar_guardrails = ""

def get_grammar_guardrails():
    global _grammar_guardrails
    if _grammar_guardrails:
        return _grammar_guardrails
        
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    trcola_path = os.path.join(project_root, 'data', 'datasets', 'trcola_data.jsonl')
    
    if not os.path.exists(trcola_path):
        return ""
        
    correct = []
    incorrect = []
    
    try:
        with open(trcola_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i > 500:
                    break
                data = json.loads(line)
                if data.get('label') == 1 and len(correct) < 2:
                    correct.append(data.get('orig'))
                elif data.get('label') == 0 and len(incorrect) < 2:
                    incorrect.append(f"{data.get('variation')} ({data.get('var_type')})")
                    
        guardrails = ""
        for c in correct:
            guardrails += f"- Doğru (Kabul Edilebilir): {c}\n"
        for inc in incorrect:
            guardrails += f"- Yanlış (Kabul Edilemez): {inc}\n"
            
        _grammar_guardrails = guardrails
        return _grammar_guardrails
    except Exception as e:
        print(f"Error loading TrCOLA: {e}")
        return ""

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
    Gənuine Bankacılık Hizmetleri
    
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

def get_rag_system_prompt(tone_instruction, literacy_note, context, user_query, implicature_context="", grammar_guardrails=""):
    prompt = f"""
    Sen "Gən" adında, edimbilimsel farkındalığa sahip bir dijital bankacılık asistanısın. Görevin, aşağıda verilen bilgileri kullanarak kullanıcının sorusunu cevaplamaktır. 
    
    [TALİMATLAR]:
    - {tone_instruction}
    - {literacy_note}
    - [BAĞLAM] bölümünde sana banka kuralları VEYA teorik bilgiler sunulacaktır.
    - Kullanıcının isteklerini reddederken veya olumsuz bilgi verirken "yüz tehdidini" (face-threatening acts) en aza indiren yumuşatıcı ifadeler kullan.
    - Eğer bağlamda bilgi yoksa ve soru genel finansal bilgi ise, kendi genel bilgini kullanarak cevapla.
    """
    
    if implicature_context:
        prompt += f"""
    [PRAGMATİK ÖRNEKLERİ (Örtük Anlam / Implicature)]:
    Aşağıdaki örnekler, insanların söylemedikleri şeyleri nasıl kastettiklerini gösterir. Yanıtlarında bu mantığı kullanarak kullanıcının asıl niyetini anla:
    {implicature_context}
    """

    if grammar_guardrails:
        prompt += f"""
    [DİL BİLGİSİ KURALLARI (Linguistic Acceptability)]:
    Aşağıdaki örnekler doğru ve yanlış Türkçe kullanımlarını göstermektedir. Kesinlikle "Yanlış (Kabul Edilemez)" olarak işaretlenmiş yapıdaki gibi dilbilgisi, morfolojik veya sözdizimsel hatalar yapma. Her zaman "Doğru" olan yapıya benzer, dilbilgisi kurallarına uyan cümleler kur:
    {grammar_guardrails}
    """

    prompt += f"""
    [BAĞLAM (BİLGİ VE TEORİK REHBER)]:
    {context}
    
    [KULLANICI SORUSU]:
    {user_query}
    """
    return prompt

