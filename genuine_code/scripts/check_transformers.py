from transformers import AutoTokenizer, AutoModel

model_name = "dbmdz/bert-base-turkish-cased"

try:
    print(f"Loading tokenizer for {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Tokenizer loaded.")
    
    print(f"Loading model for {model_name}...")
    model = AutoModel.from_pretrained(model_name)
    print("Model loaded successfully.")
except Exception as e:
    print(f"FAILED to load model: {e}")
