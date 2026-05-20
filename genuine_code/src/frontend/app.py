import chainlit as cl
import requests
import os

RASA_URL = os.getenv("RASA_URL", "http://localhost:5005")
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8001")


@cl.on_chat_start
async def start():
    welcome_text = """## Genuine'a Hoşgeldiniz

Benim ismim **Gen**, açık, empatik ve etkili finansal destek sağlamak için tasarlanmış edimbilimsel farkındalığa sahip dijital bankacılık asistanınızım.

Bana şu konularda danışabilirsiniz:
- Başka bir hesaba **para transferi** yapmak.
- *Güncel bakiyenizi* ve hesap detaylarınızı kontrol etmek.
- *Son işlemlerinizi* incelemek.
- Genel bankacılık sorularınıza yanıt bulmak.

**Geri bildiriminiz bizim için çok değerli!** Yanıtlarımdan sonra, iletişimimin **nazik** ve *öz* olup olmadığını belirtmek için butonları kullanabilirsiniz."""
    await cl.Message(content=welcome_text).send()

@cl.on_message
async def main(message: cl.Message):
    try:
        response = requests.post(
            f"{RASA_URL}/webhooks/rest/webhook",
            json={"sender": cl.user_session.get("id"), "message": message.content}
        )
        response.raise_for_status()
        rasa_responses = response.json()

        if not rasa_responses:
            await cl.Message(content="Üzgünüm, şu an sistemsel bir hatadan dolayıyanıt veremiyorum.").send()
        else:
            for response in rasa_responses:
                elements = []
                if "image" in response:
                    elements.append(cl.Image(url=response["image"], name="image", display="inline"))
                
                content = response.get("text", "")
                
                trunc_msg = content[:200].replace("|", " ")
                actions = [
                    cl.Action(name="toggle_feedback", payload={"value": trunc_msg}, label="💬 Geri Bildirim")
                ]
                
                await cl.Message(content=content, elements=elements, actions=actions).send()
    
    except requests.exceptions.RequestException as e:
        print(f"Rasa connection error: {e}")
        await cl.Message(content="Rasa sunucusuna ulaşılamıyor. Lütfen sistem yöneticinizle iletişime geçin.").send()

@cl.action_callback("toggle_feedback")
async def on_toggle_feedback(action):
    trunc_msg = action.payload.get("value", "")
    actions = [
        cl.Action(name="feedback_polite", payload={"value": f"1|{trunc_msg}"}, label="👍 Nazik & Yardımcı"),
        cl.Action(name="feedback_impolite", payload={"value": f"-1|{trunc_msg}"}, label="👎 Kaba / Doğrudan"),
        cl.Action(name="feedback_concise", payload={"value": f"1|{trunc_msg}"}, label="📏 Tam Kararında"),
        cl.Action(name="feedback_wordy", payload={"value": f"-1|{trunc_msg}"}, label="🗣️ Çok Uzun")
    ]
    await action.remove()
    await cl.Message(content="Lütfen bu yanıt için değerlendirmenizi seçin:", actions=actions).send()

@cl.action_callback("feedback_polite")
async def on_action_polite(action):
    await log_feedback(action, "Politeness")

@cl.action_callback("feedback_impolite")
async def on_action_impolite(action):
    await log_feedback(action, "Politeness")

@cl.action_callback("feedback_concise")
async def on_action_concise(action):
    await log_feedback(action, "Quantity")

@cl.action_callback("feedback_wordy")
async def on_action_wordy(action):
    await log_feedback(action, "Quantity")

async def log_feedback(action, category):
    try:
        score_str, bot_message = action.payload.get("value", "0|").split("|", 1)
        score = int(score_str)
        
        requests.post(
            f"{FASTAPI_URL}/log_feedback",
            json={
                "user_id": cl.user_session.get("id", "anonymous"),
                "bot_message": bot_message,
                "category": category,
                "value": score
            }
        )
        await cl.Message(content=f"Geri bildiriminiz için teşekkürler! ({action.label})").send()
        
    except Exception as e:
        print(f"Error logging feedback: {e}")