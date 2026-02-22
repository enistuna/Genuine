import os, sys, requests, json, warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# - debug -
import os
print(f"DEBUG: GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from langchain_community.document_loaders import TextLoader
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain.document_loaders import TextLoader
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings
    except ImportError:
        TextLoader = None
        Chroma = None
        HuggingFaceEmbeddings = None

from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.prompt_engineering.templates import get_bank_policy_text, get_rag_system_prompt
from src.utils.logger import setup_logger
from src.utils.config import load_config

logger = setup_logger("rag_engine")

class RealRAGEngine:
    def __init__(self):
        try:
            config_path = os.path.join(project_root, 'config', 'model_config.yaml')
            self.config = load_config(config_path)['rag']
        except Exception as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            self.config = {
                "model_name": "gemini-pro",
                "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
                "persist_dir": "./data/chroma",
                "collection_name": "genuine_docs",
                "kb_path": "./data/bank_policies.txt",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }

        self.kb_path = self.config.get('kb_path', './data/bank_policies.txt')
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        
        self.mock_mode = False
        if not (TextLoader and Chroma and HuggingFaceEmbeddings):
            logger.warning("Heavy dependencies missing. Running RAG in MOCK mode.")
            self.mock_mode = True
        elif os.getenv("RAG_MOCK_MODE") == "true":
            self.mock_mode = True
            
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. GenAI will be disabled (or mocked).")
        
        self.model_name = self.config.get("model_name", "gemini-2.0-flash")

        if not self.mock_mode:
            try:
                self.generate_knowledge()
                self.vector_store = self.initialize_vector_store()
            except Exception as e:
                logger.error(f"Failed to init RAG: {e}. Switching to mock mode.")
                self.mock_mode = True

    def generate_knowledge(self):
        """Generates a text file containing bank policies."""
        text = get_bank_policy_text()
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            f.write(text)

    def initialize_vector_store(self):
        """Ingests the synthetic text into ChromaDB."""
        if not os.path.exists(self.kb_path):
            self.generate_knowledge()
            
        loader = TextLoader(self.kb_path, encoding='utf-8')
        docs = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config['chunk_size'], 
            chunk_overlap=self.config['chunk_overlap']
        )
        splits = splitter.split_documents(docs)
        
        embeddings = HuggingFaceEmbeddings(model_name=self.config['embeddings_model'])
        
        return Chroma.from_documents(
            splits, 
            embeddings, 
            persist_directory=self.config['persist_dir']
        )

    def query(self, user_query, user_profile=None):
        """Retrieves context and asks Gemini to generate an answer."""
        
        if self.mock_mode:
            context = "MOCK CONTEXT: Bankamızın faiz oranları %45'tir. Kredi kartı ücreti 500 TL'dir."
        else:
            try:
                docs = self.vector_store.similarity_search(user_query, k=2)
                context = "\n".join([d.page_content for d in docs])
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                context = "Bilgi bankasına erişilemedi."

        tone_instruction = "Resmi ve profesyonel bir dil kullan."
        literacy_note = ""

        if user_profile:
            if user_profile.get("preferred_tone") == "friendly":
                tone_instruction = "Samimi, yardımsever ve günlük bir dil kullan. Emoji kullanabilirsin."
            
            literacy_score = user_profile.get("financial_literacy_score", 50)
            if literacy_score < 30:
                literacy_note = "Kullanıcının finansal bilgisi sınırlı. Terimleri basitçe açıkla."
            elif literacy_score > 80:
                literacy_note = "Kullanıcı finansal konularda uzman. Teknik detaylara girebilirsin."

        system_prompt = get_rag_system_prompt(tone_instruction, literacy_note, context, user_query)
        
        if not self.api_key:
            return f"[MOCK LLM RESPONSE]: (Gemini Key Missing)\n\n{system_prompt}"

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": system_prompt}]
                }]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"Gemini API Error {response.status_code}: {response.text}")
                return "Üzgünüm, şu anda yapay zeka servisine erişemiyorum. (API Error)"

            result = response.json()
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return "Üzgünüm, yanıt oluşturulamadı."

        except Exception as e:
            logger.error(f"Gemini connection failed: {e}")
            return "Üzgünüm, şu anda yapay zeka servisine erişemiyorum. Ancak faiz oranlarımız %45'ten başlamaktadır."

rag_client = RealRAGEngine()
