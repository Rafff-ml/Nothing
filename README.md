# OffPad

**A lightweight, offline-first note-taking application with passkey protection.**

OffPad lets you create documents, protect them with a passkey, and edit them with automatic saving — all running locally on your machine.

---

## Features

- **Create & Open** documents with passkey protection
- **Auto-save** every 3 seconds (with visual status indicator)
- **Manual save** via `Ctrl + S`
- **Auto-login** using browser localStorage
- **Word & character count** in real time
- **Last saved timestamp**
- **Logout** button with save-before-exit
- **Responsive** — works on desktop & mobile
- **Fully offline** — runs on localhost with SQLite

---

## Tech Stack

| Layer      | Technology               |
| ---------- | ------------------------ |
| Frontend   | HTML5, CSS3, Vanilla JS  |
| Backend    | FastAPI (Python)         |
| Database   | SQLite                   |
| ORM        | SQLAlchemy               |
| Validation | Pydantic                 |

---

## Project Structure

```
offpad/
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & routes
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── crud.py          # Database operations
├── frontend/
│   ├── index.html       # Home / login page
│   ├── editor.html      # Document editor page
│   ├── style.css        # Global stylesheet
│   └── script.js        # Client-side logic
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone / navigate to the project

```bash
cd offpad
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn backend.main:app --reload
```

### 5. Open in your browser

Navigate to **http://127.0.0.1:8000**

---

## API Endpoints

| Method | Endpoint                    | Description              |
| ------ | --------------------------- | ------------------------ |
| POST   | `/documents/create`         | Create a new document    |
| POST   | `/documents/login`          | Login to a document      |
| GET    | `/documents/{document_name}?passkey=...` | Get document content |
| PUT    | `/documents/{document_name}`| Update document content  |

---

## How It Works

1. **Create** a document by entering a name and passkey on the home page.
2. **Open** an existing document by entering its name and passkey.
3. The **editor** loads your content and auto-saves every 3 seconds.
4. Press **Ctrl + S** to save immediately.
5. **Logout** saves your work and clears the browser session.
6. Reopen the app — if your session is still in localStorage, you'll be auto-logged in.

All data is stored in `offpad.db` (SQLite) which is created automatically on first run.

---

## License

MIT
