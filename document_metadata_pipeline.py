import os
import pytesseract
import fitz  # PyMuPDF
import docx
from pdf2image import convert_from_path
from PIL import Image
import nltk
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import sent_tokenize

# Setup
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust this if needed
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

# ---------- Document Parsing Functions ----------

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file_path):
    text = ""
    pdf = fitz.open(file_path)
    for page in pdf:
        text += page.get_text()
    pdf.close()
    return text

def extract_text_from_scanned_pdf(file_path):
    text = ""
    images = convert_from_path(file_path)
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

def extract_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.pdf':
        text = extract_text_from_pdf(file_path)
        if len(text.strip()) < 100:  # Assume scanned if text is very short
            return extract_text_from_scanned_pdf(file_path)
        return text
    else:
        return "Unsupported file type."

# ---------- Metadata Generation Functions ----------

def extract_title(text):
    lines = text.split("\n")
    for line in lines:
        if line.strip() and len(line.strip().split()) >= 3:
            return line.strip()
    return "Unknown Title"

def extract_summary(text, n_sentences=3):
    sentences = sent_tokenize(text)
    if len(sentences) <= n_sentences:
        return " ".join(sentences)
    sorted_sentences = sorted(sentences, key=lambda x: len(x), reverse=True)
    return " ".join(sorted_sentences[:n_sentences])

def extract_keywords(text, num_keywords=5):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
    X = vectorizer.fit_transform([text])
    keywords = vectorizer.get_feature_names_out()
    return keywords[:num_keywords]

def extract_named_entities(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)
    return entities

def generate_metadata(text):
    return {
        "Title": extract_title(text),
        "Summary": extract_summary(text),
        "Keywords": list(extract_keywords(text)),
        "Named Entities": extract_named_entities(text)
    }

# ---------- Master Function ----------

def process_document(file_path):
    print(f"Processing file: {file_path}")
    text = extract_text(file_path)
    if "Unsupported file type" in text:
        return {"Error": text}
    metadata = generate_metadata(text)
    return metadata

# ---------- Example Run ----------

if __name__ == "__main__":
    filepath = "example.pdf"  # Change this to your actual file
    output = process_document(filepath)
    print("\nGenerated Metadata:\n")
    for key, value in output.items():
        print(f"{key}:\n{value}\n")

