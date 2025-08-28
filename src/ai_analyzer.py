import requests
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import logging

logger = logging.getLogger("Skynet")

def predict_threat(domain, config):
    """Prediksi ancaman dengan lightweight transformer model."""
    try:
        tokenizer = BertTokenizer.from_pretrained(config.get("bert_model_path", "/app/data/bert_model"))
        model = BertForSequenceClassification.from_pretrained(config.get("bert_model_path", "/app/data/bert_model"))
        model.eval()
        
        # Ambil metadata domain
        whois_data = requests.get(f"https://api.whois.com/v1/{domain}", headers={"Authorization": f"Bearer {config['whois_api_key']}"}).json()
        content = requests.get(f"http://{domain}", timeout=5).text if requests.get(f"http://{domain}", timeout=5).status_code == 200 else ""
        
        # Tokenisasi input
        inputs = tokenizer(f"{domain} {whois_data.get('registrar', '')} {content[:1000]}", return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
            score = torch.softmax(outputs.logits, dim=1)[0][1].item() * 100  # Probabilitas ancaman (0-100)
        
        logger.info(f"Threat score for {domain}: {score:.2f}")
        return score
    except Exception as e:
        logger.error(f"Threat prediction error for {domain}: {e}")
        return 0.0