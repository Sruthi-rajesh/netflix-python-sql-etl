import pandas as pd
from pathlib import Path
from config import RAW_DIR, CLEAN_DIR, REJECT_DIR

GENRE_MAP = {
    "SciFi": "Sci-Fi",
    "Sci-Fi": "Sci-Fi",
    "Science Fiction": "Sci-Fi",
    "Docu": "Documentary",
    "Documentary": "Documentary",
    "Drama": "Drama",
    "Comedy": "Comedy",
    "Thriller": "Thriller",
}

RATING_MAP = {
    "PG13": "PG-13",
    "pg-13": "PG-13",
    "PG-13": "PG-13",
    "TVMA": "TV-MA",
    "TV-MA": "TV-MA",
    "G": "G",
    "R": "R",
}

def ensure_dirs():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    REJECT_DIR.mkdir(parents=True, exist_ok=True)

def load_raw():
    users = pd.read_csv(RAW_DIR / "raw_users.csv")
    titles = pd.read_csv(RAW_DIR / "raw_titles.csv")
    views = pd.read_csv(RAW_DIR / "raw_views.csv")
    return users, titles, views

def clean_users(users: pd.DataFrame) -> pd.DataFrame:
    # Keep original schema but normalize types and fill missing
    users["signup_date"] = pd.to_datetime(users["signup_date"], errors="coerce").dt.date.astype(str)
    users["country"] = users["country"].fillna("UNKNOWN")
    users["plan_type"] = users["plan_type"].fillna("UNKNOWN")
    return users

def clean_titles(titles: pd.DataFrame) -> pd.DataFrame:
    titles["genre"] = titles["genre"].map(lambda x: GENRE_MAP.get(str(x).strip(), "Other"))
    titles["maturity_rating"] = titles["maturity_rating"].map(lambda x: RATING_MAP.get(str(x).strip(), "Other"))
    titles["release_year"] = pd.to_numeric(titles["release_year"], errors="coerce").fillna(0).astype(int)
    return titles

def _add_reject_reason(base: pd.Series, mask: pd.Series, reason: str) -> pd.Series:
    """
    Appends a reject reason to a string series, comma-separated.
    """
    out = base.copy()
    out = out.mask(mask & out.eq(""), reason)
    out = out.mask(mask & out.ne(""), out + "," + reason)
    return out

def validate_and_clean_views(views: pd.DataFrame):
    """
    Improvements vs original:
    - Vectorized validation (much faster than iterrows)
    - Safe repairs:
        (1) If end_before_start and both timestamps exist, swap start/end
        (2) If watch_minutes missing/invalid/negative, recompute from timestamps when possible
    - Only reject when still invalid after repairs
    """
    v = views.copy()

    # Parse timestamps + numeric fields
    v["view_start"] = pd.to_datetime(v["view_start"], errors="coerce")
    v["view_end"] = pd.to_datetime(v["view_end"], errors="coerce")
    v["watch_minutes"] = pd.to_numeric(v["watch_minutes"], errors="coerce")

    # ---------------------------
    # 1) REPAIR STEP (safe fixes)
    # ---------------------------

    # (A) Swap timestamps when end < start (common logging glitch)
    swap_mask = v["view_start"].notna() & v["view_end"].notna() & (v["view_end"] < v["view_start"])
    if swap_mask.any():
        v.loc[swap_mask, ["view_start", "view_end"]] = v.loc[swap_mask, ["view_end", "view_start"]].to_numpy()

    # (B) Recompute watch_minutes when possible
    # Recompute if watch_minutes is missing OR negative
    recalc_mask = (
        v["view_start"].notna()
        & v["view_end"].notna()
        & (v["watch_minutes"].isna() | (v["watch_minutes"] < 0))
    )
    if recalc_mask.any():
        computed = ((v.loc[recalc_mask, "view_end"] - v.loc[recalc_mask, "view_start"]).dt.total_seconds() / 60.0)
        v.loc[recalc_mask, "watch_minutes"] = computed.round()

    # If still negative (after recalc), mark missing to trigger reject
    v.loc[v["watch_minutes"].notna() & (v["watch_minutes"] < 0), "watch_minutes"] = pd.NA

    # ---------------------------
    # 2) VALIDATION STEP
    # ---------------------------
    v["reject_reason"] = ""

    bad_ts = v["view_start"].isna() | v["view_end"].isna()
    end_before = v["view_start"].notna() & v["view_end"].notna() & (v["view_end"] < v["view_start"])
    bad_watch = v["watch_minutes"].isna()
    neg_watch = v["watch_minutes"].notna() & (v["watch_minutes"] < 0)

    v["reject_reason"] = _add_reject_reason(v["reject_reason"], bad_ts, "bad_timestamp")
    v["reject_reason"] = _add_reject_reason(v["reject_reason"], end_before, "end_before_start")
    v["reject_reason"] = _add_reject_reason(v["reject_reason"], bad_watch, "bad_watch_minutes")
    v["reject_reason"] = _add_reject_reason(v["reject_reason"], neg_watch, "negative_watch_minutes")

    rejects = v[v["reject_reason"].ne("")].copy()
    cleaned = v[v["reject_reason"].eq("")].copy()

    # ---------------------------
    # 3) FINAL FORMATTING / TYPES
    # ---------------------------
    cleaned["view_start"] = cleaned["view_start"].dt.strftime("%Y-%m-%d %H:%M:%S")
    cleaned["view_end"] = cleaned["view_end"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # watch_minutes should be int
    cleaned["watch_minutes"] = cleaned["watch_minutes"].round().astype(int)

    # completed might be missing -> fill and cast
    if "completed" in cleaned.columns:
        cleaned["completed"] = pd.to_numeric(cleaned["completed"], errors="coerce").fillna(0).astype(int)

    return cleaned.drop(columns=["reject_reason"]), rejects

def main():
    ensure_dirs()
    users, titles, views = load_raw()

    users_clean = clean_users(users)
    titles_clean = clean_titles(titles)
    views_clean, rejects = validate_and_clean_views(views)

    users_clean.to_csv(CLEAN_DIR / "users_clean.csv", index=False)
    titles_clean.to_csv(CLEAN_DIR / "titles_clean.csv", index=False)
    views_clean.to_csv(CLEAN_DIR / "views_clean.csv", index=False)
    rejects.to_csv(REJECT_DIR / "views_rejects.csv", index=False)

    print("Saved cleaned data to:", CLEAN_DIR)
    print("Saved rejects to:", REJECT_DIR)
    print("Rows summary:")
    print(" users:", len(users), "->", len(users_clean))
    print(" titles:", len(titles), "->", len(titles_clean))
    print(" views:", len(views), "->", len(views_clean), "(rejects:", len(rejects), ")")

if __name__ == "__main__":
    main()
