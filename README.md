# ReNova Connect — Data Collector

**Collector** is an asynchronous service responsible for fetching and syncing data from **Clinicia**.  
It updates PostgreSQL and invalidates Redis cache when data changes.

---

## 🚀 Features

- Asynchronous Clinicia API connection  
- Data synchronization and normalization  
- PostgreSQL + Redis integration  
- Periodic updates via APScheduler  
- Manual or automatic start (cron compatible)

---

## 🧩 Technologies

| Component | Technology |
|------------|-------------|
| HTTP Client | aiohttp |
| ORM | SQLAlchemy (async) |
| Scheduler | APScheduler |
| Cache | Redis |
| Database | PostgreSQL |
| Deploy | Docker |

---

## ⚙️ Run

```bash
cp .env.example .env
docker-compose up --build
```

---

## 🧠 Architecture

```
Clinicia API → Collector → PostgreSQL → Redis (cache invalidation)
```

---

## 🧰 Environment Variables

| Variable | Description |
|-----------|-------------|
| `CLINICIA_API_URL` | Clinicia base URL |
| `CLINICIA_TOKEN` | API token |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |

---

## 🧾 License
MIT License  
© ReNova Beauty Hub
