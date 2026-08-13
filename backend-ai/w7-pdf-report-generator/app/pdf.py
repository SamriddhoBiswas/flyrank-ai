"""Render aggregated data into a PDF artifact on disk (not inline in API responses)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def render_sales_pdf(data: dict, output_path: Path, title: str = "Sales Report") -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(f"Generated: {generated}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    totals = data.get("totals") or {}
    story.append(Paragraph("Summary", styles["Heading2"]))
    summary_rows = [
        ["Total orders", str(totals.get("total_orders", 0))],
        ["Total units sold", str(totals.get("total_units", 0))],
        ["Total revenue", f"${totals.get('total_revenue', 0)}"],
    ]
    summary = Table(summary_rows, colWidths=[8 * cm, 6 * cm])
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F5F5")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(summary)
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Revenue by category (SQL GROUP BY)", styles["Heading2"]))
    cat_rows = [["Category", "Orders", "Units", "Revenue"]]
    for row in data.get("by_category") or []:
        cat_rows.append(
            [
                row["category"],
                str(row["order_count"]),
                str(row["units_sold"]),
                f"${row['revenue']}",
            ]
        )
    cat_table = Table(cat_rows, colWidths=[5 * cm, 3 * cm, 3 * cm, 3 * cm])
    cat_table.setStyle(_table_style())
    story.append(cat_table)
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Top products", styles["Heading2"]))
    prod_rows = [["Product", "Category", "Units", "Revenue"]]
    for row in data.get("top_products") or []:
        prod_rows.append(
            [
                row["name"],
                row["category"],
                str(row["units_sold"]),
                f"${row['revenue']}",
            ]
        )
    prod_table = Table(prod_rows, colWidths=[5 * cm, 4 * cm, 2.5 * cm, 2.5 * cm])
    prod_table.setStyle(_table_style())
    story.append(prod_table)

    story.append(Spacer(1, 1 * cm))
    story.append(
        Paragraph(
            "Artifact stored on disk and linked via download URL — not embedded in the API response.",
            styles["Italic"],
        )
    )

    doc.build(story)
    return output_path


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A5F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ]
    )
