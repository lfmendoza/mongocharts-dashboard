use platform_analytics;

const pipeline_1_facet_dashboard = [
  {
    $match: {
      timestamp: { $exists: true }
    }
  },
  {
    $facet: {
      deployments_by_week: [
        {
          $match: { event_type: "deployment" }
        },
        {
          $group: {
            _id: { $dateToString: { format: "%Y-W%V", date: "$timestamp" } },
            count: { $sum: 1 },
            success: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } },
            failed: { $sum: { $cond: [{ $eq: ["$status", "failed"] }, 1, 0] } }
          }
        },
        { $sort: { _id: 1 } }
      ],
      cfr_by_region: [
        {
          $match: { event_type: "deployment", status: { $in: ["success", "failed"] } }
        },
        {
          $group: {
            _id: "$region",
            total: { $sum: 1 },
            failed: { $sum: { $cond: [{ $eq: ["$status", "failed"] }, 1, 0] } }
          }
        },
        {
          $project: {
            region: "$_id",
            cfr_pct: { $multiply: [{ $divide: ["$failed", "$total"] }, 100] },
            total: 1,
            _id: 0
          }
        }
      ],
      top_failure_reasons: [
        {
          $match: { status: "failed", failure_reason: { $ne: "" } }
        },
        {
          $group: {
            _id: "$failure_reason",
            count: { $sum: 1 },
            by_environment: {
              $push: "$environment"
            }
          }
        },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ],
      sla_by_team: [
        {
          $group: {
            _id: "$team",
            total: { $sum: 1 },
            sla_met: { $sum: "$sla_met" }
          }
        },
        {
          $project: {
            team: "$_id",
            sla_pct: { $multiply: [{ $divide: ["$sla_met", "$total"] }, 100] },
            _id: 0
          }
        }
      ],
      trigger_distribution: [
        {
          $group: {
            _id: "$trigger",
            count: { $sum: 1 }
          }
        },
        { $sort: { count: -1 } }
      ]
    }
  }
];

const pipeline_2_rolling_avg_duration = [
  {
    $match: {
      event_type: "pipeline",
      duration_seconds: { $gt: 0 }
    }
  },
  {
    $sort: { timestamp: 1 }
  },
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } },
      avg_duration: { $avg: "$duration_seconds" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { _id: 1 }
  },
  {
    $setWindowFields: {
      partitionBy: null,
      sortBy: { _id: 1 },
      output: {
        rolling_avg_7d: {
          $avg: "$avg_duration",
          window: { documents: [-6, 0] }
        },
        cumulative_count: {
          $sum: "$count",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: "$_id",
      avg_duration: 1,
      rolling_avg_7d: 1,
      count: 1,
      cumulative_count: 1,
      _id: 0
    }
  }
];

const pipeline_3_percentiles_by_team = [
  {
    $match: {
      event_type: { $in: ["build", "pipeline"] },
      duration_seconds: { $gt: 0 }
    }
  },
  {
    $group: {
      _id: "$team",
      durations: { $push: "$duration_seconds" }
    }
  },
  {
    $project: {
      team: "$_id",
      durations: 1,
      n: { $size: "$durations" }
    }
  },
  {
    $project: {
      team: 1,
      durations: { $sortArray: { input: "$durations", sortBy: 1 } },
      n: 1
    }
  },
  {
    $project: {
      team: 1,
      n: 1,
      p50_idx: { $floor: { $multiply: [{ $subtract: ["$n", 1] }, 0.5] } },
      p90_idx: { $floor: { $multiply: [{ $subtract: ["$n", 1] }, 0.9] } },
      p99_idx: { $floor: { $multiply: [{ $subtract: ["$n", 1] }, 0.99] } }
    }
  },
  {
    $project: {
      team: 1,
      n: 1,
      p50_seconds: { $arrayElemAt: ["$durations", "$p50_idx"] },
      p90_seconds: { $arrayElemAt: ["$durations", "$p90_idx"] },
      p99_seconds: { $arrayElemAt: ["$durations", "$p99_idx"] }
    }
  },
  { $project: { team: 1, p50_seconds: 1, p90_seconds: 1, p99_seconds: 1, _id: 0 } }
];

const pipeline_4_duration_histogram_with_failures = [
  {
    $match: {
      event_type: { $in: ["build", "pipeline"] },
      duration_seconds: { $gte: 0 }
    }
  },
  {
    $bucket: {
      groupBy: "$duration_seconds",
      boundaries: [0, 60, 120, 180, 300, 450, 600, 900, 1200],
      default: "overflow",
      output: {
        count: { $sum: 1 },
        failed: { $sum: { $cond: [{ $eq: ["$status", "failed"] }, 1, 0] } },
        avg_cpu: { $avg: "$cpu_seconds" },
        apps: { $addToSet: "$application" }
      }
    }
  },
  {
    $project: {
      range: "$_id",
      range_label: {
        $switch: {
          branches: [
            { case: { $eq: ["$_id", "overflow"] }, then: "1200+ s" },
            { case: { $eq: ["$_id", 0] }, then: "0-60 s" },
            { case: { $eq: ["$_id", 60] }, then: "60-120 s" },
            { case: { $eq: ["$_id", 120] }, then: "120-180 s" },
            { case: { $eq: ["$_id", 180] }, then: "180-300 s" },
            { case: { $eq: ["$_id", 300] }, then: "300-450 s" },
            { case: { $eq: ["$_id", 450] }, then: "450-600 s" },
            { case: { $eq: ["$_id", 600] }, then: "600-900 s" },
            { case: { $eq: ["$_id", 900] }, then: "900-1200 s" }
          ],
          default: { $concat: [{ $toString: "$_id" }, "+ s"] }
        }
      },
      count: 1,
      failed: 1,
      failure_rate_pct: {
        $cond: [
          { $gt: ["$count", 0] },
          { $multiply: [{ $divide: ["$failed", "$count"] }, 100] },
          0
        ]
      },
      avg_cpu: { $round: ["$avg_cpu", 2] },
      apps_count: { $size: "$apps" }
    }
  }
];

const pipeline_5_author_efficiency_score = [
  {
    $match: {
      author: { $exists: true, $ne: "" }
    }
  },
  {
    $group: {
      _id: "$author",
      deployments: { $sum: { $cond: [{ $eq: ["$event_type", "deployment"] }, 1, 0] } },
      builds: { $sum: { $cond: [{ $eq: ["$event_type", "build"] }, 1, 0] } },
      total_events: { $sum: 1 },
      success_count: { $sum: { $cond: [{ $eq: ["$status", "success"] }, 1, 0] } },
      sla_met_count: { $sum: "$sla_met" },
      total_cpu: { $sum: "$cpu_seconds" },
      total_duration: { $sum: "$duration_seconds" }
    }
  },
  {
    $addFields: {
      success_rate: {
        $cond: [
          { $gt: ["$total_events", 0] },
          { $divide: ["$success_count", "$total_events"] },
          0
        ]
      },
      sla_rate: {
        $cond: [
          { $gt: ["$total_events", 0] },
          { $divide: ["$sla_met_count", "$total_events"] },
          0
        ]
      }
    }
  },
  {
    $addFields: {
      throughput_score: { $add: ["$deployments", { $multiply: ["$builds", 0.5] }] },
      quality_score: { $add: ["$success_rate", "$sla_rate"] }
    }
  },
  {
    $project: {
      author: "$_id",
      deployments: 1,
      builds: 1,
      total_events: 1,
      success_rate_pct: { $multiply: ["$success_rate", 100] },
      sla_rate_pct: { $multiply: ["$sla_rate", 100] },
      total_cpu_min: { $round: [{ $divide: ["$total_cpu", 60] }, 2] },
      efficiency_score: {
        $round: [
          {
            $add: [
              { $multiply: ["$throughput_score", 0.4] },
              { $multiply: ["$quality_score", 50] },
              { $multiply: [{ $divide: [1, { $add: ["$total_cpu", 1] }] }, 100] }
            ]
          },
          2
        ]
      },
      _id: 0
    }
  },
  { $sort: { efficiency_score: -1 } }
];

const view_deployments_by_week = [
  { $match: { timestamp: { $exists: true } } },
  { $match: { event_type: "deployment" } },
  { $group: { _id: { $dateToString: { format: "%Y-W%V", date: "$timestamp" } }, count: { $sum: 1 } } },
  { $sort: { _id: 1 } },
  { $project: { week: "$_id", count: 1, _id: 0 } }
];
const view_cfr_by_region = [
  { $match: { event_type: "deployment", status: { $in: ["success", "failed"] } } },
  { $group: { _id: "$region", total: { $sum: 1 }, failed: { $sum: { $cond: [{ $eq: ["$status", "failed"] }, 1, 0] } } } },
  { $project: { region: "$_id", cfr_pct: { $multiply: [{ $divide: ["$failed", "$total"] }, 100] }, _id: 0 } }
];
const view_top_failure_reasons = [
  { $match: { status: "failed", failure_reason: { $ne: "" } } },
  { $group: { _id: "$failure_reason", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 },
  { $project: { failure_reason: "$_id", count: 1, _id: 0 } }
];
const view_sla_by_team = [
  { $group: { _id: "$team", total: { $sum: 1 }, sla_met: { $sum: "$sla_met" } } },
  { $project: { team: "$_id", sla_pct: { $multiply: [{ $divide: ["$sla_met", "$total"] }, 100] }, _id: 0 } }
];
const view_trigger_distribution = [
  { $group: { _id: "$trigger", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $project: { trigger: "$_id", count: 1, _id: 0 } }
];

const pipeline_6_failure_correlation_analysis = [
  {
    $match: {
      status: "failed",
      failure_reason: { $ne: "" }
    }
  },
  {
    $group: {
      _id: {
        environment: "$environment",
        failure_reason: "$failure_reason",
        trigger: "$trigger"
      },
      count: { $sum: 1 },
      avg_retry: { $avg: "$retry_count" },
      avg_duration: { $avg: "$duration_seconds" }
    }
  },
  {
    $group: {
      _id: "$_id.environment",
      reasons: {
        $push: {
          reason: "$_id.failure_reason",
          trigger: "$_id.trigger",
          count: "$count",
          avg_retry: { $round: ["$avg_retry", 2] },
          avg_duration: { $round: ["$avg_duration", 2] }
        }
      }
    }
  },
  {
    $project: {
      environment: "$_id",
      top_reasons: { $slice: [{ $sortArray: { input: "$reasons", sortBy: { count: -1 } } }, 5] },
      _id: 0
    }
  }
];
