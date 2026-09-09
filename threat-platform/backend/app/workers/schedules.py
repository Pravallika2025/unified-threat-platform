"""Celery beat schedule.

TODO once Celery is enabled:
  pipeline_tick            every 1 minute
  feed_sync                every 6 hours
  retention_enforcement    daily at 02:00
  backup                   daily at 03:00
"""

SCHEDULE = {
    "pipeline-tick": {"task": "pipeline_tick", "schedule": 60.0},
    "feed-sync": {"task": "feed_sync", "schedule": 21600.0},
    "retention": {"task": "retention", "schedule": 86400.0},
}
