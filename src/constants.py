REQUIRED_CSV_FIELDS = ("event_id",)
INT_FIELDS = (
    "duration_seconds",
    "build_number",
    "retry_count",
    "tests_run",
    "tests_passed",
    "cpu_seconds",
    "sla_met",
)
FLOAT_FIELDS = ("artifact_size_mb",)
COLLECTION_INDEXES = [
    "timestamp",
    [("environment", 1), ("timestamp", 1)],
    [("event_type", 1), ("status", 1)],
    "team",
    "region",
    "branch",
    "trigger",
    "author",
    "failure_reason",
]
