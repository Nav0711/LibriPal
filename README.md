# 📚 Library Chatbot System
An AI-powered **chatbot-based library system** designed for students for quick response to library materials.
This project modernizes how students interact with libraries by offering a conversational chatbot, smart notifications, book issue/renewals, and fee tracking.  
---
## ✨ Features
- 🤖 **Chatbot** – Conversational assistant for books, due dates, and policies.  
- 🔔 **Notifications** – Automatic reminders for book returns, renewals, and overdue fees.  
- 📖 **Book Issue & Re-Issue** – Borrow and renew books via chatbot.  
- 💰 **Outstanding Fees** – Track and alert users about pending fees.  
- 📢 **Multi-channel** – Support for email & Telegram notifications.  


## 🚀 Key Highlights
- Conversational chatbot-first approach.
- Real-time book issue & renewal.
- Automated reminders and overdue alerts.
- Transparent outstanding fees tracking.
- Fully documented API at /docs.
---
## ⚙️ Backend Setup
### Prerequisites
- Python **3.10+**  
- [uv](https://github.com/astral-sh/uv) for dependency management  
- PostgreSQL (or SQLite for local development)  
### Steps
```bash
# 1️⃣ Create and activate virtual environment
.venv\Scripts\Activate       # On Windows
# source .venv/bin/activate   # On Mac/Linux
# 2️⃣ Sync dependencies
uv sync
# 3️⃣ Run the backend
python main.py
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

## 📌 Next Steps
- [ ] Add student authentication system.
- [ ] Build an admin dashboard for librarians.
- [ ] Add analytics for book trends & usage statistics.
## 💡 Inspiration
Libraries are often under-utilized because traditional systems feel outdated.
This project makes library access modern, conversational, and engaging through automation and chat-driven services.
