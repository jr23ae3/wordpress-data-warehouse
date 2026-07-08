import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import pandas as pd
import requests
from sqlalchemy import create_engine, text


WP_BASE_URL = os.getenv("WP_BASE_URL", "https://wordpress.org/news")
API_ROOT = f"{WP_BASE_URL.rstrip('/')}/wp-json/wp/v2"
MAX_PAGES = int(os.getenv("WP_MAX_PAGES", "3"))
PER_PAGE = int(os.getenv("WP_PER_PAGE", "50"))

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")


def _fetch_paginated(endpoint: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for page in range(1, MAX_PAGES + 1):
        response = requests.get(
            f"{API_ROOT}/{endpoint}",
            params={"per_page": PER_PAGE, "page": page},
            timeout=30,
        )
        if response.status_code == 400 and "rest_post_invalid_page_number" in response.text:
            break
        response.raise_for_status()
        payload = response.json()
        if not payload:
            break
        rows.extend(payload)
    return rows


def _build_traffic(posts_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    today = datetime.now(timezone.utc).date()

    for _, row in posts_df.iterrows():
        post_id = int(row["id"])
        base_views = max(120, len(row.get("title", "")) * 7)

        for offset in range(0, 7):
            metric_date = today - timedelta(days=offset)
            pageviews = base_views + (post_id % 17) * 9 + offset * 5
            sessions = int(pageviews * 0.68)
            unique_visitors = int(sessions * 0.82)
            rows.append(
                {
                    "metric_date": metric_date,
                    "post_id": post_id,
                    "pageviews": pageviews,
                    "sessions": sessions,
                    "unique_visitors": unique_visitors,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    posts_raw = _fetch_paginated("posts")
    users_raw = _fetch_paginated("users")
    comments_raw = _fetch_paginated("comments")
    categories_raw = _fetch_paginated("categories")

    posts_df = pd.DataFrame(
        [
            {
                "id": p["id"],
                "date_gmt": p.get("date_gmt"),
                "slug": p.get("slug"),
                "status": p.get("status"),
                "link": p.get("link"),
                "author_id": p.get("author"),
                "title": (p.get("title") or {}).get("rendered"),
                "category_ids": ",".join(str(c) for c in p.get("categories", [])),
                "comment_status": p.get("comment_status"),
            }
            for p in posts_raw
        ]
    )

    users_df = pd.DataFrame(
        [
            {
                "id": u["id"],
                "name": u.get("name"),
                "slug": u.get("slug"),
                "link": u.get("link"),
            }
            for u in users_raw
        ]
    )

    comments_df = pd.DataFrame(
        [
            {
                "id": c["id"],
                "post_id": c.get("post"),
                "parent_id": c.get("parent"),
                "author_name": c.get("author_name"),
                "date_gmt": c.get("date_gmt"),
                "status": c.get("status"),
            }
            for c in comments_raw
        ]
    )

    categories_df = pd.DataFrame(
        [
            {
                "id": c["id"],
                "name": c.get("name"),
                "slug": c.get("slug"),
                "description": c.get("description"),
                "count": c.get("count", 0),
            }
            for c in categories_raw
        ]
    )

    traffic_df = _build_traffic(posts_df) if not posts_df.empty else pd.DataFrame()

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    with engine.begin() as conn:
        conn.execute(text("truncate table raw.wp_posts"))
        conn.execute(text("truncate table raw.wp_users"))
        conn.execute(text("truncate table raw.wp_comments"))
        conn.execute(text("truncate table raw.wp_categories"))
        conn.execute(text("truncate table raw.wp_traffic"))

    if not posts_df.empty:
        posts_df.to_sql("wp_posts", con=engine, schema="raw", if_exists="append", index=False)
    if not users_df.empty:
        users_df.to_sql("wp_users", con=engine, schema="raw", if_exists="append", index=False)
    if not comments_df.empty:
        comments_df.to_sql(
            "wp_comments", con=engine, schema="raw", if_exists="append", index=False
        )
    if not categories_df.empty:
        categories_df.to_sql(
            "wp_categories", con=engine, schema="raw", if_exists="append", index=False
        )
    if not traffic_df.empty:
        traffic_df.to_sql("wp_traffic", con=engine, schema="raw", if_exists="append", index=False)

    print(
        "Loaded rows => "
        f"posts={len(posts_df)}, users={len(users_df)}, comments={len(comments_df)}, "
        f"categories={len(categories_df)}, traffic={len(traffic_df)}"
    )


if __name__ == "__main__":
    main()
