# ⚡ TaskForge – Role Based Project Management

A full-stack, enterprise-grade project management web application featuring a strict **hierarchical Role-Based Access Control (RBAC)** system, **Machine Learning** for smart task prediction, real-time WebSocket updates, activity logs, and a premium dark UI ("Midnight Ocean" theme).

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| **Backend** | FastAPI (Python 3.10+) + SQLAlchemy 2.0 |
| **Database** | SQLite (local dev) / PostgreSQL (production) |
| **Machine Learning** | Scikit-Learn (TF-IDF, Logistic Regression, MultiOutput Classifier) |
| **Auth** | JWT (python-jose) + bcrypt (passlib) |
| **Frontend** | React 18 + Vite + React Router |
| **Data Viz** | Recharts |
| **Real-time** | WebSockets (native FastAPI) |
| **Styling** | Vanilla CSS with Glassmorphism ("Midnight Ocean" design system) |

---

## ✨ Key Features

- **🏢 Enterprise Hierarchical RBAC**: Strict boundaries separating CEO, Department Head, Team Leader, and Employee roles.
- **🤖 Machine Learning Predictions**:
  - **Priority Prediction**: Automatically predicts task priority (`high`, `medium`, `low`) based on context.
  - **Assignment Prediction**: Suggests the optimal `Department` and `Role` to assign a task to using a custom-trained multi-output NLP model.
- **⚡ Real-time Collaboration**: Instant WebSocket communication for messaging and activity feeds.
- **📋 Task & Project Workflows**: Advanced Kanban tracking, assignment delegation, and automated filtering based on your level in the hierarchy.
- **📊 Interactive Dashboard**: Visualizes performance metrics and team productivity.

---

## 🔒 Enterprise Hierarchy & RBAC Rules

1. **CEO**
   - Full organization-wide access.
   - Can view all tasks, departments, and teams.
2. **Department Head (`head`)**
   - Manages a specific Department.
   - Sees tasks assigned to their department or org-wide tasks.
3. **Team Leader (`leader`)**
   - Manages a specific Team within a Department.
   - Sees tasks assigned to their team or org-wide tasks.
4. **Employee (`employee`)**
   - Can only view tasks directly assigned to them, or open tasks within their specific department/team.
   - Cannot create tasks; can only update statuses of their assigned tasks.

---

## 🚀 Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the backend server
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
*Backend runs at: [http://localhost:8000](http://localhost:8000)*  
*Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)*

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
*Frontend runs at: [http://localhost:5173](http://localhost:5173)*

### 3. Machine Learning Models Setup

To use the ML prediction endpoints, you must generate the synthetic datasets and train the models locally:

```bash
cd backend
# 1. Generate datasets
python ml/generate_dataset.py
python ml/generate_assignment_dataset.py

# 2. Train the models
python ml/train.py
python ml/train_assignment.py
```

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=sqlite+aiosqlite:///./taskforge.db
SECRET_KEY=change-this-to-a-random-32-char-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173
```

---

## 🚢 Deployment (Railway)

### Backend Deployment
1. Create a new Railway project and choose **Deploy from GitHub**.
2. Add a **PostgreSQL** database service (auto-injects `DATABASE_URL`).
3. Set the required environment variables (`SECRET_KEY`, `FRONTEND_URL`).
4. Railway will automatically detect the `Dockerfile` and deploy.

### Frontend Deployment
1. Create a **New Service → Static Site** in Railway.
2. Set Root Directory to `frontend/`.
3. Build Command: `npm install && npm run build`
4. Output Directory: `dist`
5. Set `VITE_API_URL` to your backend Railway URL.

---

## 📋 Core API Endpoints

### Authentication & Organization
- `POST /api/auth/register` - Secure user registration/referral flow.
- `POST /api/auth/login` - Authenticate and retrieve JWT token.
- `POST /api/organization` - Manage enterprise organization structure.

### Tasks & Machine Learning
- `GET/POST/PUT/DELETE /api/tasks` - CRUD operations for hierarchical tasks.
- `POST /api/ml/predict-priority` - ML model predicts task priority.
- `POST /api/ml/predict-assignment` - ML model predicts optimal target department and role.

### Collaboration
- `WS /ws/{project_id}` - WebSocket for real-time messaging and events.
