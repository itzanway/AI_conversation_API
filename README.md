# 🤖 AI Conversation API

A production-ready backend API for managing AI-powered conversations with persistent context and database support.  
This service exposes RESTful endpoints to create conversations, send messages to an AI model, and retrieve chat history.

Designed for developers building chatbots, AI assistants, SaaS integrations, and automation tools.

---

## 🚀 Features

- 🧠 Context-aware AI conversations  
- 💬 Persistent conversation history  
- 🗄️ Database integration  
- 🔐 Secure environment-based configuration  
- ⚡ FastAPI-powered high performance backend  
- 📦 Clean and modular project structure  

---

## 🛠 Tech Stack

- **Python**
- **FastAPI**
- **PostgreSQL / SQLite**
- **OpenAI API (or pluggable LLM provider)**
- **Uvicorn**
- **python-dotenv**

---

## 📁 Project Structure

AI_conversation_API/
│
├── database/ # Database models & configuration
├── src/ # Core application source code
│ ├── api/ # Route handlers
│ ├── services/ # AI and conversation logic
│ ├── models/ # Pydantic / ORM models
│ └── main.py # Application entry point
│
├── requirements.txt # Python dependencies
├── .env.example # Sample environment variables
├── .env # Environment config (not committed)
└── README.md


---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Mac/Linux**
```bash
source venv/bin/activate
```

**Windows**
```bash
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Copy example file:

```bash
cp .env.example .env
```

Update `.env`:

```env
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./database.db
HOST=127.0.0.1
PORT=8000
```

---

# ▶️ Running the Server

```bash
uvicorn src.main:app --reload
```

### 🌐 API Base URL
```
http://127.0.0.1:8000
```

### 📄 Interactive API Docs
```
http://127.0.0.1:8000/docs
```

---

# 📡 API Endpoints

## 🗣 Start Conversation

**POST** `/conversations/start`

### Request

```json
{
  "user_id": "123",
  "message": "Hello!"
}
```

### Response

```json
{
  "conversation_id": "uuid",
  "reply": "Hello! How can I help you today?"
}
```

---

## 💬 Send Message

**POST** `/conversations/{conversation_id}/message`

### Request

```json
{
  "message": "Tell me a joke"
}
```

### Response

```json
{
  "reply": "Why don’t programmers like nature? Too many bugs."
}
```

---

## 📜 Get Conversation History

**GET** `/conversations/{conversation_id}`

### Response

```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Hello!"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help you today?"
    }
  ]
}
```

---

# 🧪 Running Tests

```bash
pytest
```

---

# 🔒 Environment Variables

| Variable        | Description                          |
|----------------|--------------------------------------|
| OPENAI_API_KEY | API key for AI provider              |
| DATABASE_URL   | Database connection string           |
| HOST           | Server host                          |
| PORT           | Server port                          |

---

# 📌 Use Cases

- AI Chatbots
- Customer Support Automation
- SaaS AI Assistants
- Internal AI Tools
- Conversational Data Interfaces
