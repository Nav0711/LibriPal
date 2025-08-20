# 📚 Library Chatbot System
An AI-powered **chatbot-based library system** designed for students for quick response to library materials.
This project modernizes how students interact with libraries by offering a conversational chatbot, smart notifications, book issue/renewals, and fee tracking.  
---
## ✨ Features
- 🤖 **Chatbot** – Conversational assistant for books, due dates, and policies, auto prediction for queries .  
- 🔔 **Notifications** – Automatic reminders for book returns, renewals, and overdue fees.  
- 📖 **Book Issue & Re-Issue** – Borrow and renew books via chatbot.  
- 💰 **Outstanding Fees** – Track and alert users about pending fees.  


## 🚀 Key Highlights
- Conversational chatbot-first approach.
- Queries and chat prediction
- Real-time book issue & renewal.
- Automated reminders and overdue alerts.
- Transparent outstanding fees tracking.
---

![hiimg](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/Screenshot%202025-08-20%20205450.png)
![hiimg](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/Screenshot%202025-08-20%20210043.png)
![hiimg](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/image.png)

## ⚙️ Backend Setup
### Prerequisites
- Python **3.10+**  
- [uv](https://github.com/astral-sh/uv) for dependency management  
- PostgreSQL (or SQLite for local development)  
### Steps
```bash
# Sync dependencies
uv sync
# Create and activate virtual environment
.venv\Scripts\Activate       # On Windows
# source .venv/bin/activate   # On Mac/Linux
# Run the backend
python main.py

#add required Gemini Key in the .env file 
GEMINI_API_KEY=(Your Key Here)
```
Backend will be live at:
👉 http://localhost:8000/docs (Swagger UI)
## 🎨 Frontend Setup
### Prerequisites
- Node.js 18+
- npm (or yarn)
### Steps
```bash
# 1️⃣ Navigate to frontend folder
cd frontend
# 2️⃣ Install dependencies
npm install
# 3️⃣ Start frontend
npm run start
```
Frontend will be live at:
👉 http://localhost:3000
## 🖼️ Usage Flow
1. Start the backend → http://localhost:8000/docs
2. Run the frontend → http://localhost:3000
3. Chat with the library chatbot to:
   - Search for and issue books
   - Re-issue books before due date
   - Receive reminders via chat, email, or Telegram
   - View outstanding fees

## 🏗️ Tech Stack
### Frontend:
-React

### Backend:
-Python Fast API


