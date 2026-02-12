import random
from datetime import datetime, timedelta
import pandas as pd
from config import RAW_DIR

random.seed(42)

COUNTRIES = ["AU", "US", "IN", "UK", "CA", "NZ"]
PLANS = ["Basic", "Standard", "Premium"]
GENRES_RAW = ["SciFi", "Science Fiction", "Sci-Fi", "Drama", "Comedy", "Thriller", "Docu", "Documentary"]
RATINGS_RAW = ["PG13", "PG-13", "pg-13", "TVMA", "TV-MA", "G", "R"]

def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

def make_users(n=300):
    rows = []
    start = datetime(2025, 1, 1)
    for i in range(1, n + 1):
        uid = f"U{i:04d}"
        signup = start + timedelta(days=random.randint(0, 365))
        rows.append({
            "user_id": uid,
            "signup_date": signup.strftime("%Y-%m-%d"),
            "country": random.choice(COUNTRIES),
            "plan_type": random.choice(PLANS),
        })
    return pd.DataFrame(rows)

def make_titles(n=200):
    rows = []
    for i in range(1, n + 1):
        tid = f"T{i:04d}"
        rows.append({
            "title_id": tid,
            "title_name": f"Title {i}",
            "content_type": random.choice(["Movie", "Series"]),
            "genre": random.choice(GENRES_RAW),
            "release_year": random.randint(1985, 2025),
            "maturity_rating": random.choice(RATINGS_RAW),
        })
    return pd.DataFrame(rows)

def make_views(users, titles, n=5000):
    rows = []
    base = datetime(2026, 1, 1)
    for i in range(1, n + 1):
        vid = f"V{i:06d}"
        u = users.sample(1).iloc[0]["user_id"]
        t = titles.sample(1).iloc[0]["title_id"]

        start = base + timedelta(days=random.randint(0, 35), minutes=random.randint(0, 1440))
        watch = random.randint(-10, 180)  # includes bad data on purpose
        end = start + timedelta(minutes=watch)

        # ~3% invalid sessions where end < start
        if random.random() < 0.03:
            end = start - timedelta(minutes=random.randint(1, 60))

        completed = 1 if watch >= 60 and random.random() < 0.6 else 0

        rows.append({
            "view_id": vid,
            "user_id": u,
            "title_id": t,
            "view_start": start.strftime("%Y-%m-%d %H:%M:%S"),
            "view_end": end.strftime("%Y-%m-%d %H:%M:%S"),
            "watch_minutes": watch,
            "completed": completed
        })
    return pd.DataFrame(rows)

def main():
    ensure_dirs()
    users = make_users()
    titles = make_titles()
    views = make_views(users, titles)

    users.to_csv(RAW_DIR / "raw_users.csv", index=False)
    titles.to_csv(RAW_DIR / "raw_titles.csv", index=False)
    views.to_csv(RAW_DIR / "raw_views.csv", index=False)

    print("Saved raw CSVs to:", RAW_DIR)

if __name__ == "__main__":
    main()
