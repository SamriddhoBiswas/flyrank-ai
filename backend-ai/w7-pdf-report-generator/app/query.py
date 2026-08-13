"""SQL aggregation queries for the sales report."""

from __future__ import annotations

import asyncio
from typing import Any

import asyncpg

from app.config import DATABASE_URL


async def _connect() -> asyncpg.Connection:
    return await asyncpg.connect(DATABASE_URL)


async def fetch_report_data() -> dict[str, Any]:
    conn = await _connect()
    try:
        by_category = await conn.fetch(
            """
            SELECT
                p.category,
                COUNT(o.id) AS order_count,
                SUM(o.quantity) AS units_sold,
                ROUND(SUM(o.quantity * p.unit_price)::numeric, 2) AS revenue
            FROM orders o
            JOIN products p ON p.id = o.product_id
            GROUP BY p.category
            ORDER BY revenue DESC
            """
        )

        top_products = await conn.fetch(
            """
            SELECT
                p.name,
                p.category,
                SUM(o.quantity) AS units_sold,
                ROUND(SUM(o.quantity * p.unit_price)::numeric, 2) AS revenue
            FROM orders o
            JOIN products p ON p.id = o.product_id
            GROUP BY p.id, p.name, p.category
            ORDER BY revenue DESC
            LIMIT 5
            """
        )

        totals = await conn.fetchrow(
            """
            SELECT
                COUNT(o.id) AS total_orders,
                COALESCE(SUM(o.quantity), 0) AS total_units,
                ROUND(COALESCE(SUM(o.quantity * p.unit_price), 0)::numeric, 2) AS total_revenue
            FROM orders o
            JOIN products p ON p.id = o.product_id
            """
        )

        return {
            "by_category": [dict(r) for r in by_category],
            "top_products": [dict(r) for r in top_products],
            "totals": dict(totals) if totals else {},
        }
    finally:
        await conn.close()


def fetch_report_data_sync() -> dict[str, Any]:
    return asyncio.run(fetch_report_data())
