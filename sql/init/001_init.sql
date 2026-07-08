create schema if not exists raw;
create schema if not exists analytics;

create table if not exists raw.wp_posts (
    id bigint primary key,
    date_gmt timestamptz,
    slug text,
    status text,
    link text,
    author_id bigint,
    title text,
    category_ids text,
    comment_status text,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.wp_users (
    id bigint primary key,
    name text,
    slug text,
    link text,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.wp_comments (
    id bigint primary key,
    post_id bigint,
    parent_id bigint,
    author_name text,
    date_gmt timestamptz,
    status text,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.wp_categories (
    id bigint primary key,
    name text,
    slug text,
    description text,
    count integer,
    loaded_at timestamptz not null default now()
);

create table if not exists raw.wp_traffic (
    metric_date date not null,
    post_id bigint not null,
    pageviews integer not null,
    sessions integer not null,
    unique_visitors integer not null,
    loaded_at timestamptz not null default now(),
    primary key (metric_date, post_id)
);
