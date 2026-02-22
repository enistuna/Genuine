import chainlit as cl
import requests
import os

RASA_URL = os.getenv("RASA_URL", "http://localhost:5005")

@cl.on_chat_start
async def start():
    welcome_message = """
    ## Genuine'a Hoşgeldiniz 🚀
    """
    await cl.Message(content=welcome_message).send()

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
            await cl.Message(content="Üzgünüm, şu an yanıt veremiyorum.").send()
        else:
            for response in rasa_responses:
                if "text" in response:
                    await cl.Message(content=response["text"]).send()
                if "image" in response:
                    image = cl.Image(url=response["image"], name="image", display="inline")
                    await cl.Message(content="", elements=[image]).send()
    
    except requests.exceptions.RequestException as e:
        print(f"Rasa connection error: {e}")
        await cl.Message(content="Rasa sunucusuna ulaşılamıyor. Lütfen sistem yöneticinizle iletişime geçin.").send()