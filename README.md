# 🧠 Complaint Chatbot with RAG + MongoDB + Hugging Face

A smart chatbot to handle complaint registration, status tracking, and general question-answering using Retrieval-Augmented Generation (RAG). Built with:

- ⚡ FastAPI (backend)
- 📦 MongoDB for complaint storage
- 🧠 FAISS + SentenceTransformer for document retrieval
- 🤖 Hugging Face LLM (via API)
- 💬 React frontend (separate repo) with persistent device-based user tracking

---

## 🚀 Features

- 📝 File a complaint through chat
- 📌 Track the **status** or **details** using a complaint ID
- 🔐 Complaint data is private — only the user who submitted can view it
- 💡 Handles general user questions using a document-backed chatbot (RAG)
- 💻 React frontend stores a unique user ID in `localStorage`

---

## 📦 Tech Stack

| Layer     | Technology                             |
|-----------|----------------------------------------|
| Backend   | FastAPI, MongoDB (Motor), Pydantic     |
| Embedding | `all-MiniLM-L6-v2` via SentenceTransformer |
| Vector DB | FAISS                                  |
| LLM       | Hugging Face Inference API (`zephyr-7b-beta`) |
| Frontend  | React + TypeScript + HeroUI + Iconify  |

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/shubhamkatyaan/RAG_CHAT_BOT_EXAMPLE.git
cd RAG_CHAT_BOT_EXAMPLE
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `.env` file in the root:

```env
HF_API_TOKEN=your_huggingface_token
MONGODB_URL=mongodb://localhost:27017
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

Visit the API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📚 Knowledge Base: Add Your Own Documents

The chatbot uses a vector-based RAG system.

### ➕ Add a new PDF/text file

```bash
cp myfile.pdf knowledge_base/docs/
```

### 🔄 Rebuild the Index

```bash
python build_index.py
```

This will:

- Extract and chunk the document
- Embed with SentenceTransformer
- Store vectors in `faiss_index.bin` and `metadatas.pkl`

---

## 🔐 User Identity and Authorization

- On the frontend, each user is assigned a persistent `user_id` (stored in `localStorage`)
- On complaint creation, this `user_id` is saved in the database
- For status/detail queries:
  - ✅ If the same user: details are shown
  - ❌ If different: returns `403 Forbidden`

Every request includes:
- Header: `user-id`
- Body: `{ user_id, text }`

---

## 🧾 API Endpoints

| Method | Endpoint             | Description                            |
|--------|----------------------|----------------------------------------|
| POST   | `/chat`              | Main chat interaction (RAG, complaint logic) |
| POST   | `/complaints`        | Create a new complaint                 |
| GET    | `/complaints/{id}`   | Fetch complaint (user-matched only)    |

---

## 🧠 Example Chat Queries

- `"I want to file a complaint"` → Starts registration flow
- `"Track complaint 1234..."` → Shows status (if user is owner)
- `"Show me details of complaint 1234..."` → Returns full data (if allowed)
- `"What are your services?"` → Answered via knowledge base (RAG)

---

## 📁 Project Structure

```bash
├── app/
│   ├── chat/
│   │   ├── router.py        # Chatbot controller
│   │   └── manager.py       # Complaint session logic
│   ├── rag/
│   │   ├── retriever.py     # FAISS retrieval
│   │   └── llm.py           # Hugging Face query
│   ├── models/
│   │   └── schemas.py       # Pydantic schemas
│   ├── db/
│   │   └── mongo.py         # MongoDB setup
│   └── main.py              # FastAPI app entry
├── knowledge_base/
│   ├── docs/                # Upload raw PDFs/texts here
│   └── index/               # FAISS + metadata outputs
├── build_index.py           # Script to build KB
├── requirements.txt
└── README.md
```

---

## 🔗 Frontend Repo

👉 [Frontend GitHub Repository](https://github.com/shubhamkatyaan/RAG_CHAT_BOT_FRONT_END)

---

## ⚙️ CORS Setup (Already Included)

Ensure your `app/main.py` includes:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🌐 Deployment

You can deploy this backend to:

- Render / Railway / Deta / Heroku
- Any cloud VM with Python support
- Self-host with Nginx + Uvicorn + Supervisor

---

## 🪪 License

MIT — Free to use, improve, fork, and deploy.

---

## 🙌 Credits

- Hugging Face Transformers
- Sentence Transformers
- FAISS
- FastAPI
- Uvicorn
