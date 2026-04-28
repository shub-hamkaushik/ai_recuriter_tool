from sqlalchemy import inspect, text


def _add_column_if_missing(conn, inspector, table_name: str, column_name: str, sql_definition: str) -> None:
    existing = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in existing:
        return
    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}"))


def ensure_schema(engine) -> None:
    """Apply small additive schema updates for existing local databases."""
    with engine.begin() as conn:
        inspector = inspect(conn)
        tables = set(inspector.get_table_names())

        if "candidates" in tables:
            _add_column_if_missing(conn, inspector, "candidates", "status", "VARCHAR(50) DEFAULT 'New'")
            _add_column_if_missing(conn, inspector, "candidates", "education_details", "TEXT")
            _add_column_if_missing(conn, inspector, "candidates", "work_history_summary", "TEXT")
            _add_column_if_missing(conn, inspector, "candidates", "ai_summary", "TEXT")

        if "job_descriptions" in tables:
            _add_column_if_missing(conn, inspector, "job_descriptions", "location", "VARCHAR(255)")
            _add_column_if_missing(conn, inspector, "job_descriptions", "employment_type", "VARCHAR(100)")
            _add_column_if_missing(conn, inspector, "job_descriptions", "status", "VARCHAR(50) DEFAULT 'Open'")
            _add_column_if_missing(conn, inspector, "job_descriptions", "enhanced_description", "TEXT")

        if "match_results" in tables:
            _add_column_if_missing(conn, inspector, "match_results", "fit_explanation", "TEXT")
            _add_column_if_missing(conn, inspector, "match_results", "hiring_recommendation", "TEXT")
