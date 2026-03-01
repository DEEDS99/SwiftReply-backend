# SWIFTREPLY SaaS

SWIFTREPLY is a **WhatsApp automation SaaS** that allows businesses to automatically respond to customer messages, detect keywords, save leads, and handle payments through Stripe, Flutterwave, and Mobile Money. Built with **FastAPI** and a React dashboard, it supports global WhatsApp users and is production-ready.

---

## Features

- Automatic WhatsApp replies based on keyword detection
- Lead saving to Postgres (or any SQL database)
- JWT authentication for secure login
- Stripe, Flutterwave, and Mobile Money payment integration
- Multi-business support
- Revenue analytics and dashboards
- Async task handling for messaging and payments
- CORS enabled for frontend-backend communication
- OpenAI integration for AI-powered responses

---

## Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy, AsyncPG, Alembic, Celery, Redis
- **Frontend**: React (Static site deployment on Render)
- **Payments**: Stripe, Flutterwave, Mobile Money
- **Auth & Security**: JWT, Passlib (bcrypt), Python-JOSE
- **Async HTTP**: HTTPX, Requests
- **Monitoring & Logging**: Loguru, Sentry, Prometheus FastAPI Instrumentator
- **Environment Management**: python-dotenv
- **Testing & Formatting**: Pytest, Pytest-asyncio, Black, Isort

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DEEDS99/SwiftReply-backend.git
cd SwiftReply-backend
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables (`.env` file recommended):
```
STRIPE_SECRET=your_stripe_secret
FLUTTERWAVE_SECRET=your_flutterwave_secret
MOBILE_MONEY_API_KEY=your_mobile_money_key
BACKEND_URL=https://your-backend-url
```

5. Run the backend:
```bash
uvicorn main:app --reload
```

6. Deploy frontend on Render (Static Site) and update `BACKEND_URL` in the frontend code.

---

## Usage

- Access the React dashboard via the deployed frontend URL
- Add your business WhatsApp numbers and configure webhook endpoints
- Test automated replies and payment processing in sandbox mode
- Monitor revenue and leads in the dashboard

---

## Contributing

- Fork the repo
- Create a new branch
- Commit changes
- Submit a pull request

---

## License

MIT License
