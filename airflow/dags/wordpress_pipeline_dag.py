from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "data-eng",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="wordpress_analytics_pipeline",
    default_args=default_args,
    description="Load WordPress data to Postgres and build analytics views",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["wordpress", "analytics"],
) as dag:
    ingest_wordpress = BashOperator(
        task_id="ingest_wordpress_api_to_postgres",
        bash_command="python /opt/pipeline/etl/load_wordpress_data.py",
    )

    build_views = BashOperator(
        task_id="build_analytics_views",
        bash_command="python /opt/pipeline/etl/build_analytics_views.py",
    )

    ingest_wordpress >> build_views
