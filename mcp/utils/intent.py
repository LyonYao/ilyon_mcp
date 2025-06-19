import spacy
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../train/spaCy-model.dat')
NLP = spacy.load(MODEL_PATH)

class IntentRecognizer:
    def __init__(self):
        self.nlp = NLP

    def recognize(self, text):
        doc = self.nlp(text)
        intent = max(doc.cats, key=doc.cats.get)
        return intent, doc.cats
