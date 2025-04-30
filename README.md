# NLP Smart Diary Search

A natural language processing system that enables **semantic keyword search** in diary entries  
using **named entity recognition (NER)** and **sentence embeddings**.

---

## Features

- Extracts custom keywords from diary entries:
  - `Event`: What happened (e.g., "missed the meeting")
  - `Action`: What the user did (e.g., "went jogging")
  - `Time`: When it happened (e.g., "yesterday evening")

- Few-shot learning with T5 for flexible keyword extraction

- Embedding-based semantic search (via SentenceTransformers)

---

## Tech Stack

| Layer       | Tool / Model                           |
|-------------|-----------------------------------------|
| Backend NLP | Python, Hugging Face Transformers       |
| Models      | T5, BERT, all-MiniLM sentence embedding |
| Notebook    | Jupyter / Colab                         |
| Data Format | JSON                                    |

---

## 📂 Project Structure

NLP-Smart-Diary-Search/
├── data/                  # Input diary entries & annotations
├── prompts/               # Prompt templates for few-shot T5
├── extract_keywords.py    # Keyword extraction logic
├── sentence_search.py     # Semantic similarity matching
├── README.md              # Project documentation
