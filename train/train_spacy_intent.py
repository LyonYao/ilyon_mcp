import spacy
from spacy.util import minibatch, compounding
import random
import os

# 读取训练数据
def load_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            text, label = line.split('\t')
            cats = {l: 1.0 if l == label else 0.0 for l in LABELS}
            data.append((text, {"cats": cats}))
    return data

LABELS = ["create_ec2", "delete_ec2", "create_s3", "delete_s3"]
TRAIN_DATA = load_data(os.path.join(os.path.dirname(__file__), "sample_data.txt"))

# 创建空模型
def train_model(train_data, labels, output_path):
    nlp = spacy.blank("zh")
    textcat = nlp.add_pipe("textcat")
    for label in labels:
        textcat.add_label(label)
    random.shuffle(train_data)
    for epoch in range(15):
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.5))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(texts, annotations, losses=losses)
        print(f"Epoch {epoch+1}, Losses: {losses}")
    nlp.to_disk(output_path)
    print(f"模型已保存到: {output_path}")

if __name__ == "__main__":
    train_model(TRAIN_DATA, LABELS, os.path.join(os.path.dirname(__file__), "spaCy-model.dat"))
