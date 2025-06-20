import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
import random
import os

LABELS = ["create_ec2", "delete_ec2", "create_s3", "delete_s3"]

def load_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                text, label = line.split('//', 1)
            except ValueError:
                print(f"跳过无效行: {line}")
                continue
            label = label.strip()
            if label not in LABELS:
                print(f"标签 {label} 不在 LABELS 列表中，跳过: {line}")
                continue
            cats = {l: 1.0 if l == label else 0.0 for l in LABELS}
            data.append((text.strip(), {"cats": cats}))
    if not data:
        raise ValueError("训练数据为空！")
    return data

TRAIN_DATA = load_data(os.path.join(os.path.dirname(__file__), "sample_data.txt"))

def train_model(train_data, labels, output_path):
    nlp = spacy.blank("zh")
    textcat = nlp.add_pipe("textcat", last=True, config={"exclusive_classes": True, "multilabel": False})
    for label in labels:
        textcat.add_label(label)
    random.shuffle(train_data)
    for epoch in range(15):
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.5))
        for batch in batches:
            examples = []
            for text, annotation in batch:
                doc = nlp.make_doc(text)
                examples.append(Example.from_dict(doc, annotation))
            nlp.update(examples, losses=losses)
        print(f"Epoch {epoch+1}, Losses: {losses}")
    nlp.to_disk(output_path)
    print(f"模型已保存到: {output_path}")

if __name__ == "__main__":
    print("训练样本数:", len(TRAIN_DATA))
    from collections import Counter
    all_labels = []
    for _, ann in TRAIN_DATA:
        for k, v in ann["cats"].items():
            if v == 1.0:
                all_labels.append(k)
    print("各标签样本数:", Counter(all_labels))
    train_model(TRAIN_DATA, LABELS, os.path.join(os.path.dirname(__file__), "spaCy-model.dat"))