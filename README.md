# 💬 BlogBox

BlogBox is a modern blog platform built with **FastAPI** (backend) and **React.js + Redux Toolkit** (frontend). It supports blogging with images & attachments (uploaded via Cloudinary), a rich comments system, like/unlike interactions, and powerful admin features for managing blogs and users.

---

## 🚀 Features

✅ User authentication & authorization (JWT-based)  
✅ Create, edit (full content), and delete blogs with image and file attachments  
✅ Cloudinary integration for media uploads  
✅ Comments system with superuser moderation (approve/block)  
✅ Like & unlike system with live updates  
✅ Superuser can manage all blogs and user accounts  
✅ Toggle user active status from an admin panel  
✅ Responsive, modern dark-mode UI  

---

## 🖥️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React.js, Redux Toolkit, Tailwind CSS
- **Auth:** JWT-based authentication
- **Storage:** Cloudinary (images & attachments)
- **Deployment:** Render, Vercel, or other cloud providers

---

## ⚙️ Requirements

- Python 3.9+
- Node.js 16+
- PostgreSQL
- Cloudinary account

---

## 💡 Local Setup

### 🌐 Backend (FastAPI)

\`\`\`bash
# Clone the repo
git clone https://github.com/yourusername/BlogBox.git
cd BlogBox/backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
\`\`\`

Edit your \`.env\` file:

\`\`\`
DATABASE_URL=postgresql://user:password@localhost:5432/blogbox_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
CLOUDINARY_CLOUD_NAME=your_cloud_name
\`\`\`

#### 💽 Run migrations

\`\`\`bash
alembic upgrade head
\`\`\`

#### 🚀 Start FastAPI server

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

---

### 💻 Frontend (React)

\`\`\`bash
cd ../frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
\`\`\`

Edit your \`.env\` file:

\`\`\`
VITE_API_URL=http://localhost:8000/api/v1/
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_CLOUDINARY_API_KEY=your_cloudinary_api_key
\`\`\`

#### 🚀 Start frontend

\`\`\`bash
npm run dev
\`\`\`

---

## 🛡️ Superuser

After setup, create a superuser using a script or via API (as documented in your backend).

Superuser privileges:

- Edit entire blog content at once
- Manage comments approval or blocking
- Access the user admin page
- Toggle user active status

---

## 🌍 Deployment

- **Backend:** Render, Fly.io, or any VPS with Docker support
- **Frontend:** Vercel, Netlify, or AWS S3

⚙️ Make sure to update `VITE_API_URL`, database connection, and CORS settings for production.

---

## 🖼️ Screenshots

- ✅ Blog list page
- ✅ Blog detail page with superuser edit
- ✅ Admin user management page (with active toggle)

---

## 🧑‍💻 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 💌 Contact

**Author:** Aswin Narayanan  
**Email:** your-email@example.com  
**GitHub:** [@yourusername](https://github.com/yourusername)

---

⭐ **If you like this project, please consider starring the repo!**