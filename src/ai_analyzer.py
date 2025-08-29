from sklearn.linear_model import LogisticRegression
import joblib
import hashlib
import logging
import os

logger = logging.getLogger("Skynet")

class ThreatAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model = joblib.load(self.config["model_path"]) if os.path.exists(self.config["model_path"]) else LogisticRegression()

    def predict_threat(self, domain):
        try:
            domain_hash = int(hashlib.sha256(domain.encode()).hexdigest(), 16) % 10**8
            score = self.model.predict_proba([[domain_hash]])[0][1] * 100
            logger.info(f"Threat score for {domain}: {score:.2f}")
            return score
        except Exception as e:
            logger.error(f"Threat prediction error: {e}")
            return 0.0