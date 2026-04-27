from langchain_core.tools import tool
from google.cloud import bigquery
from app.core.bigquery_client import run_query
import json


@tool
def get_traffic_volume_by_source(
    traffic_source: str, start_date: str, end_date: str
) -> str:
    """
    Retorna o volume de usuários de um canal de tráfego específico em um período.
    Use quando o usuário perguntar sobre um canal específico como Search, Facebook, etc.

    Args:
        traffic_source: Canal de mídia (Search, Organic, Facebook, Email, Display)
        start_date: Data início no formato YYYY-MM-DD
        end_date: Data fim no formato YYYY-MM-DD
    """
    sql = """
        SELECT
            DATE(created_at) AS date,
            traffic_source,
            COUNT(DISTINCT id) AS total_users
        FROM `bigquery-public-data.thelook_ecommerce.users`
        WHERE traffic_source = @traffic_source
          AND DATE(created_at) BETWEEN @start_date AND @end_date
        GROUP BY 1, 2
        ORDER BY 1
    """
    params = [
        bigquery.ScalarQueryParameter("traffic_source", "STRING", traffic_source),
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
    ]
    rows = run_query(sql, params)
    total = sum(r["total_users"] for r in rows)
    return json.dumps(
        {"traffic_source": traffic_source, "total_users": total, "daily_breakdown": rows},
        default=str,
    )


@tool
def get_all_channels_performance(start_date: str, end_date: str) -> str:
    """
    Retorna performance comparativa de todos os canais: usuários, pedidos,
    receita e taxa de conversão. Use quando o usuário quiser comparar canais
    ou perguntar qual é o melhor.

    Args:
        start_date: Data início no formato YYYY-MM-DD
        end_date: Data fim no formato YYYY-MM-DD
    """
    sql = """
        WITH user_orders AS (
            SELECT
                u.traffic_source,
                COUNT(DISTINCT u.id)            AS total_users,
                COUNT(DISTINCT o.order_id)      AS total_orders,
                ROUND(SUM(oi.sale_price), 2)    AS total_revenue,
                ROUND(AVG(oi.sale_price), 2)    AS avg_order_value
            FROM `bigquery-public-data.thelook_ecommerce.users` u
            LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` o
                ON u.id = o.user_id
                AND o.status NOT IN ('Cancelled', 'Returned')
                AND DATE(o.created_at) BETWEEN @start_date AND @end_date
            LEFT JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
                ON o.order_id = oi.order_id
            WHERE DATE(u.created_at) BETWEEN @start_date AND @end_date
            GROUP BY 1
        )
        SELECT
            traffic_source,
            total_users,
            total_orders,
            total_revenue,
            avg_order_value,
            ROUND(SAFE_DIVIDE(total_orders, total_users) * 100, 2) AS conversion_rate_pct
        FROM user_orders
        ORDER BY total_revenue DESC
    """
    params = [
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
    ]
    rows = run_query(sql, params)
    return json.dumps(
        {"period": f"{start_date} to {end_date}", "channels": rows},
        default=str,
    )


@tool
def get_top_converting_channels(start_date: str, end_date: str, limit: int = 3) -> str:
    """
    Retorna os canais com maior taxa de conversão (pedidos / usuários).
    Use quando o usuário perguntar sobre conversão ou ROI.

    Args:
        start_date: Data início no formato YYYY-MM-DD
        end_date: Data fim no formato YYYY-MM-DD
        limit: Número de canais a retornar
    """
    sql = """
        SELECT
            u.traffic_source,
            COUNT(DISTINCT u.id)                                        AS total_users,
            COUNT(DISTINCT o.order_id)                                  AS total_orders,
            ROUND(SAFE_DIVIDE(COUNT(DISTINCT o.order_id),
                              COUNT(DISTINCT u.id)) * 100, 2)           AS conversion_rate_pct,
            ROUND(SUM(oi.sale_price), 2)                                AS total_revenue
        FROM `bigquery-public-data.thelook_ecommerce.users` u
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` o
            ON u.id = o.user_id
            AND o.status NOT IN ('Cancelled', 'Returned')
            AND DATE(o.created_at) BETWEEN @start_date AND @end_date
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
            ON o.order_id = oi.order_id
        WHERE DATE(u.created_at) BETWEEN @start_date AND @end_date
        GROUP BY 1
        ORDER BY conversion_rate_pct DESC
        LIMIT @limit
    """
    params = [
        bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
        bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
        bigquery.ScalarQueryParameter("limit", "INT64", limit),
    ]
    rows = run_query(sql, params)
    return json.dumps({"top_converting_channels": rows}, default=str)


ALL_TOOLS = [
    get_traffic_volume_by_source,
    get_all_channels_performance,
    get_top_converting_channels,
]