import os, sys, requests, json, warnings
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["ANONYMIZED_TELEMETRY"] = "False"
print(f"DEBUG: GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader, Docx2txtLoader
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader, Docx2txtLoader
        from langchain.vectorstores import Chroma
        from langchain.embeddings import HuggingFaceEmbeddings
    except ImportError:
        TextLoader = None
        DirectoryLoader = None
        PyPDFLoader = None
        Docx2txtLoader = None
        Chroma = None
        HuggingFaceEmbeddings = None

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from src.prompt_engineering.templates import get_bank_policy_text, get_rag_system_prompt, get_grammar_guardrails
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
                "model_name": "gemini-2.5-flash",
                "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
                "persist_dir": "./data/chroma",
                "collection_name": "genuine_docs",
                "kb_dir": "./data/knowledge_base",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }

        self.kb_dir = self.config.get('kb_dir', './data/knowledge_base')
        os.makedirs(self.kb_dir, exist_ok=True)
        
        self.mock_mode = False
        if not (TextLoader and Chroma and HuggingFaceEmbeddings):
            logger.warning("Heavy dependencies missing. Running RAG in MOCK mode.")
            self.mock_mode = True
        elif os.getenv("RAG_MOCK_MODE") == "true":
            self.mock_mode = True
            
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. GenAI will be disabled (or mocked).")
        
        self.model_name = self.config.get("model_name", "gemini-2.5-flash")

        if not self.mock_mode:
            try:
                self.vector_store = self.initialize_vector_store()
                self.implicature_store = self.initialize_implicature_store()
            except Exception as e:
                logger.error(f"Failed to init RAG: {e}. Switching to mock mode.")
                self.mock_mode = True

    def initialize_vector_store(self):
        """Ingests documents from the knowledge_base directory into ChromaDB."""
        
        embeddings = HuggingFaceEmbeddings(model_name=self.config['embeddings_model'])
        store = Chroma(persist_directory=self.config['persist_dir'], embedding_function=embeddings, collection_name=self.config['collection_name'])
        
        if store._collection.count() > 0:
            logger.info("Found existing genuine_docs ChromaDB collection. Skipping re-ingestion.")
            return store
            
        logger.info("Ingesting Knowledge Base documents into ChromaDB...")
        docs = []
        for file in os.listdir(self.kb_dir):
            file_path = os.path.join(self.kb_dir, file)
            if file.endswith('.txt') or file.endswith('.md'):
                loader = TextLoader(file_path, encoding='utf-8')
                docs.extend(loader.load())
            elif file.endswith('.pdf') and PyPDFLoader:
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
            elif file.endswith('.docx') and Docx2txtLoader:
                loader = Docx2txtLoader(file_path)
                docs.extend(loader.load())
        
        if not docs:
            fallback_path = os.path.join(self.kb_dir, "bank_policies.txt")
            text = get_bank_policy_text()
            with open(fallback_path, 'w', encoding='utf-8') as f:
                f.write(text)
            loader = TextLoader(fallback_path, encoding='utf-8')
            docs.extend(loader.load())
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config['chunk_size'], 
            chunk_overlap=self.config['chunk_overlap']
        )
        splits = splitter.split_documents(docs)
        
        store.add_documents(splits)
        return store

    def initialize_implicature_store(self):
        """Ingests implicature data into a separate ChromaDB collection."""
        embeddings = HuggingFaceEmbeddings(model_name=self.config['embeddings_model'])
        implicature_persist_dir = os.path.join(self.config['persist_dir'], "implicature")
        
        store = Chroma(persist_directory=implicature_persist_dir, embedding_function=embeddings, collection_name="implicature_examples")
        
        if store._collection.count() > 0:
            return store
            
        dataset_path = os.path.join(project_root, 'data', 'datasets', 'grice_implicature_data.jsonl')
        if not os.path.exists(dataset_path):
            return store
            
        logger.info("Ingesting Grice Implicature dataset. This may take a moment...")
        docs = []
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i >= 500:
                        break
                    data = json.loads(line)
                    if 'dialog' in data:
                        for turn in data['dialog']:
                            q = turn.get('question', '')
                            a = turn.get('answer', '')
                            ea = turn.get('explict_answer', '')
                            content = f"Context Question: {q}\nIndirect Answer: {a}\nExplicit Meaning (Implicature): {ea}"
                            docs.append(Document(page_content=content))
        except Exception as e:
            logger.error(f"Failed to read Grice data: {e}")
            
        if docs:
            store.add_documents(docs)
            
        return store

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

        implicature_context = ""
        if not self.mock_mode and hasattr(self, 'implicature_store') and self.implicature_store:
            try:
                imp_docs = self.implicature_store.similarity_search(user_query, k=2)
                implicature_context = "\n\n".join([d.page_content for d in imp_docs])
            except Exception as e:
                logger.error(f"Implicature retrieval failed: {e}")
                
        grammar_guardrails = get_grammar_guardrails()

        system_prompt = get_rag_system_prompt(
            tone_instruction, 
            literacy_note, 
            context, 
            user_query,
            implicature_context=implicature_context,
            grammar_guardrails=grammar_guardrails
        )
        
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
                return "Üzgünüm, şu anda yapay zeka servisine erişemiyorum."

            result = response.json()
            try:
                return result['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return "Üzgünüm, yanıt oluşturulamadı."

        except Exception as e:
            logger.error(f"Gemini connection failed: {e}")
            return "Üzgünüm, şu anda yapay zeka servisine erişemiyorum. Ancak faiz oranlarımız %45'ten başlamaktadır."

rag_client = RealRAGEngine()
