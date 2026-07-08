import os

from sqlalchemy import create_engine, text


DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "warehouse")
DB_USER = os.getenv("POSTGRES_USER", "etl")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "etl")


def main() -> None:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    sql = """
    create schema if not exists analytics;

    drop view if exists analytics.posts_per_category;
    create view analytics.posts_per_category as
    select
        c.id as category_id,
        c.name as category_name,
        c.count as category_post_count
    from raw.wp_categories c;

    drop view if exists analytics.comment_activity;
    create view analytics.comment_activity as
    select
        coalesce(date_trunc('day', date_gmt), now())::date as activity_date,
        count(*) as comments_count
    from raw.wp_comments
    group by 1
    order by 1;

    drop view if exists analytics.top_posts_by_traffic;
    create view analytics.top_posts_by_traffic as
    select
        p.id as post_id,
        p.title,
        p.slug,
        sum(t.pageviews) as pageviews,
        sum(t.sessions) as sessions,
        sum(t.unique_visitors) as unique_visitors
    from raw.wp_posts p
    join raw.wp_traffic t on t.post_id = p.id
    group by p.id, p.title, p.slug
    order by pageviews desc;

    drop view if exists analytics.pipeline_kpis;
    create view analytics.pipeline_kpis as
    select 'posts'::text as metric, count(*)::bigint as value from raw.wp_posts
    union all
    select 'users'::text as metric, count(*)::bigint as value from raw.wp_users
    union all
    select 'comments'::text as metric, count(*)::bigint as value from raw.wp_comments
    union all
    select 'traffic_rows'::text as metric, count(*)::bigint as value from raw.wp_traffic
    union all
    select 'categories'::text as metric, count(*)::bigint as value from raw.wp_categories;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("Created analytics views in schema analytics")


if __name__ == "__main__":
    main()
