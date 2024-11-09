import re
from transformers import LlamaTokenizer

def preprocess_text(text):
    # Normalisasi
    text = text.lower()
    
    # Pembersihan
    text = re.sub(r'[^\w\s]', '', text)
    
    # Hapus whitespace berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize_text(text, tokenizer):
    # Tokenisasi
    tokens = tokenizer.tokenize(text)
    
    # Konversi token ke ID
    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    
    return input_ids

# Inisialisasi tokenizer
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Sampel kalimat
sentences = [
    "Fasilitas apa saja yang ada di Sindang Kemadu?",
    "Dapatkah Anda memberikan detail tentang Lembah Rembulan?",
    "Sejarah Sawah Batu bagaimana?"
]

print("Before and After Preprocessing:")
for sentence in sentences:
    print("\nOriginal:", sentence)
    
    # Preprocessing
    preprocessed = preprocess_text(sentence)
    print("Preprocessed:", preprocessed)
    
    # Tokenisasi
    tokenized = tokenize_text(preprocessed, tokenizer)
    print("Tokenized:", tokenized)
    
    # Decoding kembali untuk menunjukkan hasil
    decoded = tokenizer.decode(tokenized)
    print("Decoded:", decoded)