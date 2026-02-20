#!/usr/bin/env python3
"""Genera CSV de pipeline_events."""

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42

APPLICATIONS = [
    "api-gateway",
    "auth-service",
    "payment-service",
    "user-service",
    "inventory-service",
    "notification-service",
    "analytics-service",
    "order-service",
]

REGIONS = ["us-east-1", "eu-west-1", "ap-south-1", "sa-east-1"]
TEAMS = ["platform", "backend", "frontend", "infra"]
AUTHORS = [
    "maria.garcia", "carlos.lopez", "ana.martinez", "jose.rodriguez",
    "lucia.fernandez", "david.sanchez", "elena.torres", "pablo.ramos",
]

ENVIRONMENTS = ["dev", "staging", "production"]
EVENT_TYPES = ["deployment", "build", "pipeline"]
STATUSES = ["success", "failed", "cancelled"]
BRANCHES = ["main", "develop", "feature/auth-v2", "feature/payment-fix", "release/2.1", "hotfix/critical"]
TRIGGERS = ["webhook", "merge_request", "manual", "schedule"]
FAILURE_REASONS = ["timeout", "test_failure", "infra_error", "config_error", "dependency_fail"]

ENV_WEIGHTS = [0.50, 0.30, 0.20]
STATUS_WEIGHTS = [0.88, 0.10, 0.02]
EVENT_TYPE_WEIGHTS = [0.35, 0.45, 0.20]
TRIGGER_WEIGHTS = [0.40, 0.35, 0.15, 0.10]
DURATION_RANGES = {
    "deployment": (45, 300),
    "build": (60, 600),
    "pipeline": (120, 900),
}


def generate_event(
    event_id: int, start_date: datetime, end_date: datetime, seed: int = SEED
) -> dict:
    random.seed(seed + event_id)
    delta = (end_date - start_date).total_seconds()
    ts = start_date + timedelta(seconds=random.uniform(0, delta))

    event_type = random.choices(EVENT_TYPES, weights=EVENT_TYPE_WEIGHTS, k=1)[0]
    environment = random.choices(ENVIRONMENTS, weights=ENV_WEIGHTS, k=1)[0]
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

    low, high = DURATION_RANGES[event_type]
    duration = random.randint(low, high)
    retry_count = random.randint(0, 2) if status == "failed" else 0

    branch = random.choice(BRANCHES)
    trigger = random.choices(TRIGGERS, weights=TRIGGER_WEIGHTS, k=1)[0]
    author = random.choice(AUTHORS)

    if event_type in ("build", "pipeline"):
        tests_run = random.randint(50, 500)
        tests_passed = int(tests_run * random.uniform(0.92, 1.0)) if status == "success" else int(tests_run * random.uniform(0.0, 0.90))
        artifact_size_mb = round(max(0.1, random.uniform(10, 800)), 2)
    else:
        tests_run = 0
        tests_passed = 0
        artifact_size_mb = 0.0

    cpu_seconds = int(duration * random.uniform(0.8, 1.5))
    sla_met = 1 if duration <= (low + high) // 2 else 0
    failure_reason = random.choice(FAILURE_REASONS) if status == "failed" else ""

    event_uuid = str(uuid.UUID(int=random.getrandbits(128)))

    return {
        "event_id": event_uuid,
        "timestamp": ts.isoformat(),
        "event_type": event_type,
        "status": status,
        "environment": environment,
        "application": random.choice(APPLICATIONS),
        "region": random.choice(REGIONS),
        "team": random.choice(TEAMS),
        "duration_seconds": duration,
        "build_number": event_id,
        "branch": branch,
        "trigger": trigger,
        "retry_count": retry_count,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
        "cpu_seconds": cpu_seconds,
        "artifact_size_mb": artifact_size_mb,
        "author": author,
        "sla_met": sla_met,
        "failure_reason": failure_reason,
    }


def main():
    parser = argparse.ArgumentParser(description="Genera CSV de eventos de pipeline CI/CD")
    parser.add_argument(
        "--rows",
        type=int,
        default=100000,
        help="Número de registros a generar (default: 100000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla para random (default: 42)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Rango temporal en días hacia atrás (default: 90)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/pipeline_events.csv",
        help="Ruta del archivo CSV de salida",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    if args.seed == 42:
        end_date = datetime(2025, 2, 15, 23, 59, 59)
    else:
        end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=args.days)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "event_id",
        "timestamp",
        "event_type",
        "status",
        "environment",
        "application",
        "region",
        "team",
        "duration_seconds",
        "build_number",
        "branch",
        "trigger",
        "retry_count",
        "tests_run",
        "tests_passed",
        "cpu_seconds",
        "artifact_size_mb",
        "author",
        "sla_met",
        "failure_reason",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(args.rows):
            event = generate_event(i, start_date, end_date, seed=args.seed)
            writer.writerow(event)

    print(f"Generados {args.rows} eventos en {output_path}")
    print(f"Semilla: {args.seed} | Rango: {start_date.date()} a {end_date.date()}")


if __name__ == "__main__":
    main()
