from src.pipelines.definitions import (
    pipeline_1_facet,
    pipeline_2_rolling_avg,
    pipeline_3_percentiles,
    pipeline_4_bucket_histogram,
    pipeline_5_author_efficiency,
    pipeline_6_failure_correlation,
)

PIPELINE_REGISTRY = {
    "1_facet_dashboard": pipeline_1_facet,
    "2_rolling_avg": pipeline_2_rolling_avg,
    "3_percentiles": pipeline_3_percentiles,
    "4_bucket_histogram": pipeline_4_bucket_histogram,
    "5_author_efficiency": pipeline_5_author_efficiency,
    "6_failure_correlation": pipeline_6_failure_correlation,
}


def get_pipeline(name: str):
    if name not in PIPELINE_REGISTRY:
        raise KeyError(f"Pipeline desconocida: {name}")
    return PIPELINE_REGISTRY[name]
