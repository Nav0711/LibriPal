   <div align="center">
        <h1>🏛️ LibriPal - AI Library Assistant</h1>
    </div>


<div align="center">



**An intelligent chatbot-powered library management system designed for modern students**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org)


</div>

---

## 🌟 Overview

LibriPal revolutionizes the traditional library experience by providing an intelligent, conversational interface for all your library needs. Say goodbye to complex library systems and hello to intuitive, chat-based interactions!

Problem statement: AI powered Library and book reminder

### 🎯 Why LibriPal?

- **🤖 Smart Conversations** - Natural language processing for intuitive queries
- **⚡ Instant Responses** - Get information faster than traditional search
- **📱 Modern Interface** - Clean, responsive design for all devices
- **🔔 Proactive Alerts** - Never miss a due date again

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 **Intelligent Chatbot**
- Natural language book search
- Query auto-prediction and suggestions
- Conversational book recommendations
- Library policy assistance

</td>
<td width="50%">

### 📚 **Book Management**
- Easy book issuing and renewals
- Real-time availability checking
- Digital book tracking
- Reading history management

</td>
</tr>
<tr>
<td width="50%">

### 🔔 **Smart Notifications**
- Automated return reminders
- Overdue alerts via multiple channels
- Renewal notifications
- Fee payment reminders

</td>
<td width="50%">

### 💰 **Fee Management**
- Real-time outstanding fee tracking
- Payment history and receipts
- Transparent fee calculations
- Multiple payment options

</td>
</tr>
</table>

---

## 🚀 Quick Start

### 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** - [Download here](https://python.org/downloads)
- **Node.js 18+** - [Download here](https://nodejs.org)
- **uv** - Fast Python package manager
- **PostgreSQL** - For production (SQLite for development)

### ⚙️ Backend Setup

```bash
# 📦 Clone the repository
git clone https://github.com/Nav0711/LibriPal.git
cd LibriPal

# 🔧 Install dependencies with uv
uv sync

# 🚀 Activate virtual environment
# Windows
.venv\Scripts\Activate
# macOS/Linux
# source .venv/bin/activate

# 🔑 Configure environment variables
# Create .env file and add your Gemini API key
echo "GEMINI_API_KEY=your_gemini_key_here" > .env

# 🏃‍♂️ Start the backend server
python main.py
```

> **✅ Success!** Backend running at: http://localhost:8000/docs

### 🎨 Frontend Setup

```bash
# 📁 Navigate to frontend directory
cd frontend

# 📦 Install dependencies
npm install

# 🚀 Start development server
npm run start
```

> **✅ Success!** Frontend running at: http://localhost:3000

---

## 💻 Tech Stack

<div align="center">

### Frontend Technologies
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### Backend Technologies
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)

</div>

---

## 📱 Screenshots

<div align="center">


### 💬 Chat Interface
![Dashboard](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/Screenshot%202025-08-20%20205450.png)

![Chat Interface](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/Screenshot%202025-08-20%20210043.png)

![Analytics](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/image1.png)
### Book Search Feature
![Analytics](https://github.com/Nav0711/LibriPal/blob/main/frontend/media/Screenshot%202025-08-20%20213931.png)


</div>

---

## 🔄 Usage Flow

```mermaid
graph TD
    A[🚀 Start Backend Server] --> B[🎨 Launch Frontend]
    B --> C[💬 Open Chat Interface]
    C --> D{What would you like to do?}
    D -->|Search Books| E[🔍 Book Search & Issue]
    D -->|Renew Books| F[🔄 Book Renewal]
    D -->|Check Fees| G[💰 Fee Management]
    D -->|Get Reminders| H[🔔 Notification Setup]
    E --> I[✅ Task Completed]
    F --> I
    G --> I
    H --> I
```

### 📝 Step-by-Step Guide

1. **🌐 Access the Application**
   - Backend API: http://localhost:8000/docs
   - Frontend Interface: http://localhost:3000

2. **💬 Start Chatting**
   - Type natural language queries
   - Get instant, intelligent responses
   - Follow suggested actions

3. **📚 Library Operations**
   - Search and issue books conversationally
   - Renew books before due dates
   - Track reading progress

4. **🔔 Stay Updated**
   - Receive smart notifications
   - Get reminders via chat, email, or Telegram
   - Monitor outstanding fees

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### 🐛 Found a Bug?
Open an issue on our [GitHub Issues](https://github.com/Nav0711/LibriPal/issues) page.

### 💡 Have a Feature Request?
We'd love to hear your ideas! Create a feature request issue.

---

