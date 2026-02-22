import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import Dict, Text, Any, List

class TurkishFinancialNER:
    def __init__(self, model_path="dbmdz/bert-base-turkish-cased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path, num_labels=3)
        self.label_map = {0: "O", 1: "B-PARA", 2: "I-PARA"}

    def extract_entities(self, text: Text) -> List[Dict[Text, Any]]:
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        predictions = torch.argmax(logits, dim=2)
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        entities = []
        current_entity = None
        

        for token, pred in zip(tokens, predictions[0].tolist()):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
                
            label = self.label_map.get(pred, "O")
            
            if label == "B-PARA":
                if current_entity:
                    entities.append(current_entity)
                current_entity = {"entity": "amount", "value": token, "confidence": 0.9}
            
            elif label == "I-PARA" and current_entity:
                if token.startswith("##"):
                    current_entity["value"] += token[2:]
                else:
                    current_entity["value"] += " " + token
            
            else:
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
        
        if current_entity:
            entities.append(current_entity)
            
        return entities

# example
if __name__ == "__main__":
    ner = TurkishFinancialNER()
    print(ner.extract_entities("Lütfen hesabıma 500 TL yatır."))
