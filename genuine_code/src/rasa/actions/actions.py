from typing import Any, Text, Dict, List
import os, sys, aiohttp, json
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

load_dotenv(os.path.join(project_root, '.env'))

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet



_rag_client_instance = None
def get_rag_client():
    global _rag_client_instance
    if _rag_client_instance is None:
        from src.llm.rag_client import rag_client
        _rag_client_instance = rag_client
    return _rag_client_instance



BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
TCKN_PLACEHOLDER = "12345678901"

class BaseActionMixin:
    """
    Base class for shared logic like fetching profile and logging.
    """

    async def _get_user_and_profile(self, session, tckn):
        async with session.get(f"{BACKEND_URL}/users/tckn/{tckn}") as resp:
            if resp.status != 200:
                return None, None
            user_data = await resp.json()
            
        user_id = user_data['user_id']
        async with session.get(f"{BACKEND_URL}/users/{user_id}/profile") as resp:
            if resp.status != 200:
                return user_data, None
            profile_data = await resp.json()
            
        return user_data, profile_data

    async def _log_interaction(self, session, user_id, topic):
        payload = {
            "topic": topic,
            "sentiment": "neutral",
            "used_slang": False 
        }
        try:
            await session.post(f"{BACKEND_URL}/users/{user_id}/log_interaction", json=payload)
        except Exception as e:
            print(f"Logging failed (non-fatal): {e}")

    def _get_tone_response(self, profile, formal_text, friendly_text):
        if profile and profile.get("preferred_tone") == "friendly":
            return friendly_text
        return formal_text


class ActionCheckBalance(Action, BaseActionMixin):
    def name(self) -> Text:
        return "action_check_balance"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        
        print(f"DEBUG: ActionCheckBalance STARTED for user: {TCKN_PLACEHOLDER}")
        try:
            async with aiohttp.ClientSession() as session:
                user, profile = await self._get_user_and_profile(session, TCKN_PLACEHOLDER)
                
                if not user:
                    dispatcher.utter_message(text="Kullanıcı bilgilerinize ulaşılamadı.")
                    return []

                balance = user.get("balance", 0)
                formatted_balance = "{:,.2f}".format(balance).replace(",", "X").replace(".", ",").replace("X", ".")
                
                response_text = self._get_tone_response(
                    profile,
                    f"Sayın {user['full_name']}, hesabınızdaki güncel bakiye {formatted_balance} TL'dir.",
                    f"Selam {user['full_name'].split()[0]}! Hesabında şu an {formatted_balance} TL var. 💰"
                )
                
                dispatcher.utter_message(text=response_text)
                
                await self._log_interaction(session, user['user_id'], "balance_check")
                
                acc_no = "Bilinmiyor"
                if user.get("accounts"):
                    acc_no = user["accounts"][0].get("IBAN", "Bilinmiyor")

                print("DEBUG: ActionCheckBalance SUCCESS, returning events")
                return [SlotSet("balance", str(balance)), SlotSet("account_number", acc_no)]
        except Exception as e:
            dispatcher.utter_message(text=f"Bakiye sorgulama sırasında hata: {str(e)}")
            return []


class ActionTransferFunds(Action, BaseActionMixin):
    def name(self) -> Text:
        return "action_transfer_funds"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        
        user_name = tracker.get_slot("user")
        amount_str = tracker.get_slot("money_sum")
        
        try:
            amount = float(''.join(filter(str.isdigit, str(amount_str))))
        except:
            amount = 0

        if not user_name or amount <= 0:
             dispatcher.utter_message(text="Transfer bilgileri eksik. Lütfen kime ve ne kadar göndermek istediğinizi belirtin.")
             return [SlotSet("requested_slot", "user") if not user_name else SlotSet("requested_slot", "money_sum")]

        try:
            async with aiohttp.ClientSession() as session:
                user, profile = await self._get_user_and_profile(session, TCKN_PLACEHOLDER)
                
                if not user:
                    dispatcher.utter_message(text="İşlem gerçekleştirilemedi. Kullanıcı bilgisi bulunamadı.")
                    return []

                payload = {
                    "sender_tckn": TCKN_PLACEHOLDER,
                    "amount": amount,
                    "recipient_tckn": TCKN_PLACEHOLDER
                }
                
                async with session.post(f"{BACKEND_URL}/transfer", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        response_text = self._get_tone_response(
                            profile,
                            f"Transfer işleminiz başarıyla gerçekleşti. {user_name} adlı kişiye {amount} TL gönderildi.",
                            f"Harika! {user_name} hesabına {amount} TL yolladım. İşlem tamam! ✅"
                        )
                        dispatcher.utter_message(text=response_text)
                    else:
                        err = await resp.json()
                        dispatcher.utter_message(text=f"Transfer başarısız: {err.get('detail', 'Bilinmeyen hata')}")

                await self._log_interaction(session, user['user_id'], "transfer")
        except Exception as e:
            dispatcher.utter_message(text=f"İşlem sırasında bir hata oluştu: {str(e)}")
            return []
        
        return []


class ActionListTransactions(Action, BaseActionMixin):
    def name(self) -> Text:
        return "action_list_transactions"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        
        print(f"DEBUG: ActionListTransactions STARTED for user: {TCKN_PLACEHOLDER}")
        try:
            async with aiohttp.ClientSession() as session:
                user, profile = await self._get_user_and_profile(session, TCKN_PLACEHOLDER)
                
                if not user:
                    dispatcher.utter_message(text="Bilgilerinize ulaşılamadı.")
                    return []

                async with session.get(f"{BACKEND_URL}/users/{user['user_id']}/transactions") as resp:
                    data = await resp.json()
                    transactions = data.get("transactions", [])
                    
                    if not transactions:
                        dispatcher.utter_message(text="Son dönemde bir işlem bulunamadı.")
                    else:
                        msg = "Son işlemleriniz:\n"
                        for t in transactions:
                            msg += f"- {t['date']}: {t['description']} ({t['amount']} TL)\n"
                        
                        dispatcher.utter_message(text=msg)

                print("DEBUG: ActionListTransactions SUCCESS")
                await self._log_interaction(session, user['user_id'], "list_transactions")
        except Exception as e:
            dispatcher.utter_message(text=f"İşlem listesi alınırken hata: {str(e)}")
            return []
        
        return []


class ActionAnswerFAQ(Action, BaseActionMixin):
    def name(self) -> Text:
        return "action_answer_faq"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text')
        
        try:
            async with aiohttp.ClientSession() as session:
                user, profile = await self._get_user_and_profile(session, TCKN_PLACEHOLDER)
                
                rag_engine = get_rag_client()
                answer = rag_engine.query(user_message, user_profile=profile)
                
                if answer:
                    response = f"**[Akıllı Gen]:**\n{answer}"
                else:
                    response = "Üzgünüm, bu konuda bankamızda kayıtlı bir bilgi bulamadım."

                dispatcher.utter_message(text=response)
                
                if user:
                    pass

        except Exception as e:
             print(f"FAQ Error: {e}")
             dispatcher.utter_message(text=f"Bir hata oluştu: {str(e)}")
             return []

        return []