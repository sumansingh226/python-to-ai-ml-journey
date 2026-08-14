
"""
=====================================================================
 statistics MODULE — FULL WALKTHROUGH USING GA4-STYLE VISITOR DATA
=====================================================================
 
The statistics module provides functions for working with numerical
data. Here we treat it as a mini time-series analytics pipeline —
the kind you'd run on GA4 "users per day/week/month" exports before
they hit Postgres/ClickHouse for storage or a dashboard.
 
Data shape we use throughout:
  1. MONTHLY_VISITORS  -> a flat list (array) of 12 monthly totals
  2. WEEKLY_VISITORS   -> a dict (object) of {month: [4-5 weekly values]}
 
Every statistics function below gets:
  - a 1-line description (its own docstring, "desc for each module")
  - a run on the monthly array (macro trend)
  - a run on one month's weekly array (micro trend)
so you see the exact same method applied at two granularities, the
way you'd zoom in/out on a GA4 time series.
=====================================================================
"""