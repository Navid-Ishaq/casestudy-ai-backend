"""
---------------------------------------------------------
CaseStudy AI Backend
Deterministic Intent and Tool Registry
---------------------------------------------------------

Purpose:
    Classify user intent and map Business KPI questions to MCP tools.

This module contains no OpenAI calls and no MCP network calls.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class Intent(StrEnum):
    BUSINESS_KPI = "BUSINESS_KPI"
    TOOL_DISCOVERY = "TOOL_DISCOVERY"
    DATASET_INFORMATION = "DATASET_INFORMATION"
    TECHNOLOGY = "TECHNOLOGY"
    KNOWLEDGE = "KNOWLEDGE"
    CASE_STUDY = "CASE_STUDY"
    GENERAL = "GENERAL"


@dataclass(frozen=True)
class ToolRoute:
    tool_name: str
    category: str
    keywords: tuple[str, ...]
    arguments: dict | None = None


def normalize_question(question: str) -> str:

    return " ".join(
        question.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace("?", " ")
        .replace(".", " ")
        .replace(",", " ")
        .split()
    )


def contains_any(text: str, keywords: Iterable[str]) -> bool:

    tokens = set(text.split())

    for keyword in keywords:
        if " " in keyword:
            if keyword in text:
                return True
        elif keyword in tokens:
            return True

    return False


TOOL_DISCOVERY_KEYWORDS = (
    "what tools do you have",
    "list available tools",
    "list available mcp tools",
    "list mcp tools",
    "available business intelligence tools",
    "available bi tools",
    "what can you analyze",
    "what analytics can you do",
    "what kpis can you answer",
    "show tools",
    "show available tools",
)


DATASET_INFORMATION_KEYWORDS = (
    "which dataset",
    "what dataset",
    "dataset are you using",
    "configured dataset",
    "analytics dataset",
    "data source",
    "which data source",
    "bigquery dataset",
    "project id",
    "server status",
    "mcp server status",
    "analytics server status",
)


TECHNOLOGY_KEYWORDS = (
    "architecture",
    "openai",
    "mcp",
    "model context protocol",
    "bigquery",
    "fastapi",
    "fastmcp",
    "python",
    "sql",
    "google cloud",
    "data engineering",
    "etl",
    "elt",
    "pipeline",
    "api",
    "how does it work",
    "technical",
    "technology",
)


TECHNOLOGY_QUESTION_MARKERS = (
    "what is",
    "what are",
    "explain",
    "how does",
    "how do",
    "architecture",
    "technical",
    "technology",
)


CASE_STUDY_KEYWORDS = (
    "case study",
    "case studies",
    "casestudy",
    "portfolio",
    "project example",
)


KNOWLEDGE_KEYWORDS = (
    "detleng",
    "services",
    "service",
    "contact",
    "email",
    "website",
    "mission",
    "about",
    "company",
    "who are you",
    "what do you do",
)


BUSINESS_KPI_TERMS = (
    "revenue",
    "sales",
    "orders",
    "customers",
    "customer",
    "products",
    "product",
    "categories",
    "category",
    "sellers",
    "seller",
    "payments",
    "payment",
    "reviews",
    "review",
    "rating",
    "delivery",
    "kpi",
    "analytics",
    "metric",
    "dashboard",
    "top",
    "bottom",
    "best selling",
    "worst selling",
    "average",
    "count",
    "total",
    "growth",
    "profit",
    "margin",
    "cost",
    "refund",
    "inventory",
    "stock",
    "conversion",
    "retention",
    "churn",
)


TOOL_ROUTES: tuple[ToolRoute, ...] = (
    ToolRoute(
        "executive_dashboard",
        "Executive KPIs",
        (
            "executive dashboard",
            "business dashboard",
            "overall dashboard",
            "kpi dashboard",
        ),
    ),
    ToolRoute(
        "business_summary",
        "Executive KPIs",
        (
            "business summary",
            "overall business summary",
            "company summary",
            "business overview",
        ),
    ),
    ToolRoute(
        "sales_summary",
        "Executive KPIs",
        (
            "sales summary",
            "sales overview",
            "revenue summary",
        ),
    ),
    ToolRoute(
        "customer_summary",
        "Executive KPIs",
        (
            "customer summary",
            "customer overview",
        ),
    ),
    ToolRoute(
        "delivery_summary",
        "Executive KPIs",
        (
            "delivery summary",
            "delivery overview",
        ),
    ),
    ToolRoute(
        "payment_summary",
        "Executive KPIs",
        (
            "payment summary",
            "payment overview",
        ),
    ),
    ToolRoute(
        "review_summary",
        "Executive KPIs",
        (
            "review summary",
            "review overview",
        ),
    ),
    ToolRoute(
        "monthly_revenue_growth",
        "Revenue Analytics",
        (
            "monthly revenue growth",
            "revenue growth by month",
        ),
    ),
    ToolRoute(
        "quarterly_revenue_growth",
        "Revenue Analytics",
        (
            "quarterly revenue growth",
            "revenue growth by quarter",
        ),
    ),
    ToolRoute(
        "yearly_revenue_growth",
        "Revenue Analytics",
        (
            "yearly revenue growth",
            "revenue growth by year",
        ),
    ),
    ToolRoute(
        "revenue_by_month",
        "Revenue Analytics",
        (
            "revenue by month",
            "sales by month",
            "month wise revenue",
        ),
    ),
    ToolRoute(
        "revenue_by_year",
        "Revenue Analytics",
        (
            "revenue by year",
            "sales by year",
            "year wise revenue",
        ),
    ),
    ToolRoute(
        "top_revenue_month",
        "Revenue Analytics",
        (
            "top revenue month",
            "highest revenue month",
            "best revenue month",
        ),
    ),
    ToolRoute(
        "lowest_revenue_month",
        "Revenue Analytics",
        (
            "lowest revenue month",
            "worst revenue month",
            "least revenue month",
        ),
    ),
    ToolRoute(
        "new_customers",
        "Customer Analytics",
        (
            "new customers",
            "first time customers",
            "new customer count",
        ),
    ),
    ToolRoute(
        "repeat_customers",
        "Customer Analytics",
        (
            "repeat customers",
            "returning customers",
            "customers with multiple orders",
        ),
    ),
    ToolRoute(
        "customer_growth",
        "Customer Analytics",
        (
            "customer growth",
            "customer growth by month",
            "new customer growth",
        ),
    ),
    ToolRoute(
        "customers_by_month",
        "Customer Analytics",
        (
            "customers by month",
            "monthly customers",
            "customer count by month",
        ),
    ),
    ToolRoute(
        "customers_by_year",
        "Customer Analytics",
        (
            "customers by year",
            "yearly customers",
            "customer count by year",
        ),
    ),
    ToolRoute(
        "highest_priced_products",
        "Product Analytics",
        (
            "highest priced products",
            "most expensive products",
            "highest price products",
        ),
    ),
    ToolRoute(
        "lowest_priced_products",
        "Product Analytics",
        (
            "lowest priced products",
            "cheapest products",
            "lowest price products",
        ),
    ),
    ToolRoute(
        "largest_categories",
        "Product Analytics",
        (
            "largest categories",
            "categories with most products",
            "biggest categories",
        ),
    ),
    ToolRoute(
        "smallest_categories",
        "Product Analytics",
        (
            "smallest categories",
            "categories with fewest products",
            "smallest product categories",
        ),
    ),
    ToolRoute(
        "products_per_category",
        "Product Analytics",
        (
            "products per category",
            "product count per category",
        ),
    ),
    ToolRoute(
        "bottom_sellers",
        "Seller Analytics",
        (
            "bottom sellers",
            "lowest sellers",
            "worst sellers",
            "lowest revenue sellers",
        ),
    ),
    ToolRoute(
        "seller_growth",
        "Seller Analytics",
        (
            "seller growth",
            "new sellers by month",
            "seller growth by month",
        ),
    ),
    ToolRoute(
        "average_seller_revenue",
        "Seller Analytics",
        (
            "average seller revenue",
            "avg seller revenue",
            "revenue per seller",
        ),
    ),
    ToolRoute(
        "cancelled_orders",
        "Order Analytics",
        (
            "cancelled orders",
            "canceled orders",
            "cancelled order count",
            "canceled order count",
        ),
    ),
    ToolRoute(
        "delivered_orders",
        "Order Analytics",
        (
            "delivered orders",
            "delivered order count",
        ),
    ),
    ToolRoute(
        "pending_orders",
        "Order Analytics",
        (
            "pending orders",
            "pending order count",
        ),
    ),
    ToolRoute(
        "processing_orders",
        "Order Analytics",
        (
            "processing orders",
            "processing order count",
        ),
    ),
    ToolRoute(
        "shipped_orders",
        "Order Analytics",
        (
            "shipped orders",
            "shipped order count",
        ),
    ),
    ToolRoute(
        "order_status_distribution",
        "Order Analytics",
        (
            "order status distribution",
            "orders by status",
            "order status breakdown",
        ),
    ),
    ToolRoute(
        "orders_by_month",
        "Order Analytics",
        (
            "orders by month",
            "monthly orders",
            "order count by month",
        ),
    ),
    ToolRoute(
        "orders_by_weekday",
        "Order Analytics",
        (
            "orders by weekday",
            "weekday orders",
            "orders by day of week",
        ),
    ),
    ToolRoute(
        "orders_by_hour",
        "Order Analytics",
        (
            "orders by hour",
            "hourly orders",
            "orders by purchase hour",
        ),
    ),
    ToolRoute(
        "late_deliveries",
        "Delivery Analytics",
        (
            "late deliveries",
            "late delivery count",
            "delayed deliveries",
        ),
    ),
    ToolRoute(
        "on_time_deliveries",
        "Delivery Analytics",
        (
            "on time deliveries",
            "on-time deliveries",
            "on time delivery count",
        ),
    ),
    ToolRoute(
        "delivery_success_rate",
        "Delivery Analytics",
        (
            "delivery success rate",
            "on time delivery percentage",
            "delivery success percentage",
        ),
    ),
    ToolRoute(
        "average_delivery_variance",
        "Delivery Analytics",
        (
            "average delivery variance",
            "avg delivery variance",
            "delivery variance",
        ),
    ),
    ToolRoute(
        "payment_type_distribution",
        "Payment Analytics",
        (
            "payment type distribution",
            "payment method distribution",
            "payments by method",
        ),
    ),
    ToolRoute(
        "installments_distribution",
        "Payment Analytics",
        (
            "installments distribution",
            "installment category distribution",
            "installment breakdown",
        ),
    ),
    ToolRoute(
        "highest_payment_orders",
        "Payment Analytics",
        (
            "highest payment orders",
            "top payment orders",
            "largest payment orders",
        ),
    ),
    ToolRoute(
        "positive_reviews",
        "Review Analytics",
        (
            "positive reviews",
            "positive review count",
            "good reviews",
        ),
    ),
    ToolRoute(
        "negative_reviews",
        "Review Analytics",
        (
            "negative reviews",
            "negative review count",
            "bad reviews",
        ),
    ),
    ToolRoute(
        "reviews_by_month",
        "Review Analytics",
        (
            "reviews by month",
            "monthly reviews",
            "review count by month",
        ),
    ),
    ToolRoute(
        "average_comment_length",
        "Review Analytics",
        (
            "average comment length",
            "avg comment length",
            "review comment length",
        ),
    ),
    ToolRoute(
        "top_cities",
        "Geography Analytics",
        (
            "top cities",
            "top customer cities",
            "cities with most customers",
        ),
    ),
    ToolRoute(
        "top_states",
        "Geography Analytics",
        (
            "top states",
            "top customer states",
            "states with most customers",
        ),
    ),
    ToolRoute(
        "customer_density",
        "Geography Analytics",
        (
            "customer density",
            "customer density by city",
        ),
    ),
    ToolRoute(
        "seller_density",
        "Geography Analytics",
        (
            "seller density",
            "seller density by state",
        ),
    ),
    ToolRoute(
        "monthly_orders",
        "Time Intelligence",
        (
            "monthly order trend",
            "monthly order count",
        ),
    ),
    ToolRoute(
        "monthly_customers",
        "Time Intelligence",
        (
            "monthly customer trend",
            "monthly customer count",
        ),
    ),
    ToolRoute(
        "monthly_payments",
        "Time Intelligence",
        (
            "monthly payments",
            "monthly payment value",
            "payments by month",
        ),
    ),
    ToolRoute(
        "monthly_reviews",
        "Time Intelligence",
        (
            "monthly review trend",
            "monthly review count",
        ),
    ),
    ToolRoute(
        "month_over_month_growth",
        "Time Intelligence",
        (
            "month over month growth",
            "month over month",
            "mom growth",
            "monthly growth",
            "growth by month",
        ),
    ),
    ToolRoute(
        "year_over_year_growth",
        "Time Intelligence",
        (
            "year over year growth",
            "year over year",
            "yoy growth",
            "annual growth",
            "growth by year",
        ),
    ),
    ToolRoute(
        "quarterly_revenue",
        "Time Intelligence",
        (
            "quarterly revenue",
            "revenue by quarter",
            "quarter revenue",
            "sales by quarter",
        ),
    ),
    ToolRoute(
        "monthly_revenue",
        "Time Intelligence",
        (
            "monthly revenue",
            "revenue by month",
            "sales by month",
            "month wise revenue",
        ),
    ),
    ToolRoute(
        "yearly_revenue",
        "Time Intelligence",
        (
            "yearly revenue",
            "annual revenue",
            "revenue by year",
            "sales by year",
            "year wise revenue",
        ),
    ),
    ToolRoute(
        "highest_rated_products",
        "Review Analytics",
        (
            "highest rated products",
            "best rated products",
            "top rated products",
            "products with highest ratings",
        ),
    ),
    ToolRoute(
        "lowest_rated_products",
        "Review Analytics",
        (
            "lowest rated products",
            "worst rated products",
            "products with lowest ratings",
            "badly rated products",
        ),
    ),
    ToolRoute(
        "rating_distribution",
        "Review Analytics",
        (
            "rating distribution",
            "review distribution",
            "ratings breakdown",
            "reviews by rating",
            "rating split",
        ),
    ),
    ToolRoute(
        "average_rating",
        "Review Analytics",
        (
            "average rating",
            "average review",
            "average review score",
            "avg rating",
            "avg review",
        ),
    ),
    ToolRoute(
        "revenue_by_payment_type",
        "Payment Analytics",
        (
            "revenue by payment type",
            "payment type revenue",
            "payment method revenue",
            "sales by payment type",
            "payments by type",
        ),
    ),
    ToolRoute(
        "average_payment_value",
        "Payment Analytics",
        (
            "average payment value",
            "avg payment value",
            "average payment",
            "avg payment",
        ),
    ),
    ToolRoute(
        "payment_installments",
        "Payment Analytics",
        (
            "payment installments",
            "installments",
            "installment distribution",
            "payments installments",
        ),
    ),
    ToolRoute(
        "average_delivery_days",
        "Delivery Analytics",
        (
            "average delivery days",
            "avg delivery days",
            "average delivery time",
            "avg delivery time",
            "delivery days",
        ),
    ),
    ToolRoute(
        "delivery_performance",
        "Delivery Analytics",
        (
            "delivery performance",
            "delivery analytics",
            "delivery kpi",
            "delivery metric",
        ),
    ),
    ToolRoute(
        "sellers_by_state",
        "Seller Analytics",
        (
            "sellers by state",
            "seller count by state",
            "seller state",
            "seller distribution by state",
        ),
    ),
    ToolRoute(
        "top_sellers",
        "Seller Analytics",
        (
            "top sellers",
            "best sellers",
            "highest selling sellers",
            "top performing sellers",
        ),
    ),
    ToolRoute(
        "seller_revenue",
        "Seller Analytics",
        (
            "seller revenue",
            "seller sales",
            "seller performance",
        ),
    ),
    ToolRoute(
        "revenue_by_seller",
        "Revenue Analytics",
        (
            "revenue by seller",
            "sales by seller",
        ),
    ),
    ToolRoute(
        "seller_count",
        "Seller Analytics",
        (
            "seller count",
            "total sellers",
            "number of sellers",
            "how many sellers",
        ),
    ),
    ToolRoute(
        "best_selling_products",
        "Product Analytics",
        (
            "best selling products",
            "best selling product",
            "most sold products",
            "highest selling products",
            "products sold most",
        ),
    ),
    ToolRoute(
        "worst_selling_products",
        "Product Analytics",
        (
            "worst selling products",
            "worst selling product",
            "least sold products",
            "lowest selling products",
            "products sold least",
        ),
    ),
    ToolRoute(
        "products_by_category",
        "Product Analytics",
        (
            "products by category",
            "product count by category",
            "category product count",
            "products per category",
        ),
    ),
    ToolRoute(
        "average_product_price",
        "Product Analytics",
        (
            "average product price",
            "avg product price",
            "average item price",
            "avg item price",
        ),
    ),
    ToolRoute(
        "product_count",
        "Product Analytics",
        (
            "product count",
            "total products",
            "number of products",
            "how many products",
        ),
    ),
    ToolRoute(
        "customer_lifetime_value",
        "Customer Analytics",
        (
            "customer lifetime value",
            "customer ltv",
            "lifetime value",
            "clv",
        ),
    ),
    ToolRoute(
        "average_customer_spend",
        "Customer Analytics",
        (
            "average customer spend",
            "avg customer spend",
            "average spend per customer",
            "customer average spend",
        ),
    ),
    ToolRoute(
        "top_customers",
        "Customer Analytics",
        (
            "top customers",
            "best customers",
            "highest value customers",
            "customers by revenue",
            "customers by spend",
        ),
    ),
    ToolRoute(
        "customers_by_state",
        "Customer Analytics",
        (
            "customers by state",
            "customer count by state",
            "customer state",
            "customer distribution by state",
        ),
    ),
    ToolRoute(
        "customers_by_city",
        "Customer Analytics",
        (
            "customers by city",
            "customer count by city",
            "customer city",
            "customer distribution by city",
        ),
    ),
    ToolRoute(
        "bottom_categories",
        "Sales Analytics",
        (
            "bottom categories",
            "lowest categories",
            "worst categories",
            "least revenue categories",
        ),
    ),
    ToolRoute(
        "top_categories",
        "Sales Analytics",
        (
            "top categories",
            "top 10 product categories",
            "best categories",
            "highest revenue categories",
            "top product categories",
        ),
    ),
    ToolRoute(
        "bottom_products",
        "Sales Analytics",
        (
            "bottom products",
            "lowest products by revenue",
            "worst products by revenue",
            "least revenue products",
        ),
    ),
    ToolRoute(
        "top_products",
        "Sales Analytics",
        (
            "top products",
            "top product",
            "best products by revenue",
            "highest revenue products",
        ),
    ),
    ToolRoute(
        "revenue_by_category",
        "Revenue Analytics",
        (
            "revenue by category",
            "sales by category",
            "category revenue",
            "category sales",
            "product categories by revenue",
        ),
    ),
    ToolRoute(
        "revenue_by_product",
        "Revenue Analytics",
        (
            "revenue by product",
            "sales by product",
            "product revenue",
            "product sales",
        ),
    ),
    ToolRoute(
        "revenue_by_state",
        "Revenue Analytics",
        (
            "revenue by state",
            "sales by state",
            "state revenue",
            "state sales",
        ),
    ),
    ToolRoute(
        "revenue_by_city",
        "Revenue Analytics",
        (
            "revenue by city",
            "sales by city",
            "city revenue",
            "city sales",
        ),
    ),
    ToolRoute(
        "average_order_value",
        "Executive KPIs",
        (
            "average order value",
            "avg order value",
            "aov",
        ),
    ),
    ToolRoute(
        "revenue_per_customer",
        "Executive KPIs",
        (
            "revenue per customer",
            "average revenue per customer",
            "avg revenue per customer",
            "rpc",
        ),
    ),
    ToolRoute(
        "total_categories",
        "Executive KPIs",
        (
            "total categories",
            "category count",
            "number of categories",
            "how many categories",
        ),
    ),
    ToolRoute(
        "total_sellers",
        "Executive KPIs",
        (
            "total sellers",
        ),
    ),
    ToolRoute(
        "total_products",
        "Executive KPIs",
        (
            "total products",
        ),
    ),
    ToolRoute(
        "customer_count",
        "Executive KPIs",
        (
            "customer count",
            "customers count",
            "total customers",
            "number of customers",
            "how many customers",
        ),
    ),
    ToolRoute(
        "total_orders",
        "Executive KPIs",
        (
            "total orders",
            "order count",
            "orders count",
            "number of orders",
            "how many orders",
        ),
    ),
    ToolRoute(
        "total_revenue",
        "Executive KPIs",
        (
            "total revenue",
            "overall revenue",
            "business revenue",
            "total sales value",
            "sales amount",
        ),
    ),
)


def classify_intent(question: str) -> Intent:

    q = normalize_question(question)

    if contains_any(q, TOOL_DISCOVERY_KEYWORDS):
        return Intent.TOOL_DISCOVERY

    if contains_any(q, DATASET_INFORMATION_KEYWORDS):
        return Intent.DATASET_INFORMATION

    if contains_any(q, TECHNOLOGY_KEYWORDS) and contains_any(q, TECHNOLOGY_QUESTION_MARKERS):
        return Intent.TECHNOLOGY

    matched_route = find_tool_route(question)

    if matched_route is not None:
        return Intent.BUSINESS_KPI

    if contains_any(q, BUSINESS_KPI_TERMS):
        return Intent.BUSINESS_KPI

    if contains_any(q, TECHNOLOGY_KEYWORDS):
        return Intent.TECHNOLOGY

    if contains_any(q, CASE_STUDY_KEYWORDS):
        return Intent.CASE_STUDY

    if contains_any(q, KNOWLEDGE_KEYWORDS):
        return Intent.KNOWLEDGE

    return Intent.GENERAL


def find_tool_route(question: str) -> ToolRoute | None:

    q = normalize_question(question)

    for route in TOOL_ROUTES:
        if contains_any(q, route.keywords):
            return route

    return None


def route_question(question: str) -> tuple[Intent, ToolRoute | None]:

    intent = classify_intent(question)

    if intent == Intent.BUSINESS_KPI:
        return intent, find_tool_route(question)

    return intent, None


def group_registered_tools(tool_names: Iterable[str]) -> dict[str, list[str]]:

    grouped_tools: dict[str, list[str]] = {}
    route_by_tool = {
        route.tool_name: route
        for route in TOOL_ROUTES
    }

    for tool_name in sorted(set(tool_names)):
        route = route_by_tool.get(tool_name)
        category = route.category if route else "Other Business Intelligence Tools"
        grouped_tools.setdefault(category, []).append(tool_name)

    return grouped_tools
