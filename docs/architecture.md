# WordPress Analytics Pipeline Architecture

```mermaid
flowchart TB
    A[WordPress REST API] --> B[Python Ingestion]
    B --> C[(Postgres raw schema)]
    C --> D[Airflow DAG]
    D --> E[(Postgres analytics views)]
    E --> F[Dashboard - Metabase]

    C --> C1[wp_posts]
    C --> C2[wp_users]
    C --> C3[wp_comments]
    C --> C4[wp_categories]
    C --> C5[wp_traffic]
```

## Included Data Domains
- Posts
- Users
- Comments
- Traffic
- Categories

## Runtime Components
- Python loader: [etl/load_wordpress_data.py](etl/load_wordpress_data.py)
- Postgres schemas and tables: [sql/init/001_init.sql](sql/init/001_init.sql)
- Airflow orchestration: [airflow/dags/wordpress_pipeline_dag.py](airflow/dags/wordpress_pipeline_dag.py)
- Analytics view builder: [etl/build_analytics_views.py](etl/build_analytics_views.py)
- Dashboard layer: Metabase connected to analytics views
