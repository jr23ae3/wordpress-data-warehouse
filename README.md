# WordPress Analytics Pipeline

End-to-end data pipeline:

WordPress REST API -> Python -> Postgres -> Airflow -> Dashboard

## Included Domains
- Posts
- Users
- Comments
- Traffic
- Categories

## Stack
- Source: WordPress REST API (`/wp-json/wp/v2`)
- Ingestion: Python (`requests`, `pandas`, `SQLAlchemy`)
- Storage: Postgres 16
- Orchestration: Airflow 2.10
- Dashboard: Metabase

## Repository Layout
```text
.
├── airflow/
│   ├── Dockerfile
│   ├── .env
│   └── dags/wordpress_pipeline_dag.py
├── data/sample/
│   ├── posts.csv
│   ├── users.csv
│   ├── comments.csv
│   ├── categories.csv
│   └── traffic.csv
├── docker-compose.yml
├── docs/architecture.md
├── etl/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── load_wordpress_data.py
│   └── build_analytics_views.py
└── sql/init/001_init.sql
```

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/jr23ae3/wordpress-data-warehouse.git
   cd wordpress-data-warehouse
   ```

2. Start services:
   ```bash
   docker compose up -d postgres adminer metabase airflow
   ```

3. Run on-demand ETL once (optional manual trigger):
   ```bash
   docker compose run --rm python-etl
   python etl/build_analytics_views.py
   ```

4. Airflow DAG:
- UI: http://localhost:8081
- DAG name: `wordpress_analytics_pipeline`
- Default credentials: `admin` / `admin`

5. Dashboard tools:
- Adminer: http://localhost:8080
- Metabase: http://localhost:3001

## Raw Tables
- `raw.wp_posts`
- `raw.wp_users`
- `raw.wp_comments`
- `raw.wp_categories`
- `raw.wp_traffic`

## Analytics Views
- `analytics.pipeline_kpis`
- `analytics.top_posts_by_traffic`
- `analytics.comment_activity`
- `analytics.posts_per_category`

## Notes
- `WP_BASE_URL` defaults to `https://wordpress.org/news` and can be overridden in compose env.
- Traffic is generated in Python as synthetic per-post daily metrics to make dashboards immediately usable.
