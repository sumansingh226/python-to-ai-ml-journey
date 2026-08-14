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

import statistics as stats

# ---------------------------------------------------------------
# 1. THE DATA — pretend GA4 "Users" export, Jan–Dec
# ---------------------------------------------------------------

# Array: total unique visitors per month (12 months)
MONTHLY_VISITORS = [
    12500, 11800, 14200, 15100, 16800, 19500,
    21000, 20500, 18700, 17200, 15600, 22300,   # Dec spike = holiday traffic
]

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

# Object: each month broken into weekly visitor counts (GA4 weekly rollup)
# Numbers are built so they roughly sum toward the monthly total above.
WEEKLY_VISITORS = {
    "Jan": [2900, 3100, 3200, 3300],
    "Feb": [2700, 2900, 3000, 3200],
    "Mar": [3300, 3400, 3600, 3900],
    "Apr": [3600, 3700, 3800, 4000],
    "May": [3900, 4100, 4300, 4500],
    "Jun": [4500, 4700, 5000, 5300],
    "Jul": [4900, 5100, 5400, 5600],
    "Aug": [4800, 5000, 5200, 5500],
    "Sep": [4400, 4500, 4700, 5100],
    "Oct": [4000, 4200, 4400, 4600],
    "Nov": [3600, 3800, 4000, 4200],
    "Dec": [4200, 4300, 6500, 7300],   # week 3-4 = Black Friday/Xmas surge
}

SAMPLE_MONTH = "Dec"
weekly_sample = WEEKLY_VISITORS[SAMPLE_MONTH]

print("=" * 70)
print("GA4 TIME SERIES — statistics MODULE WALKTHROUGH")
print("=" * 70)
print(f"Monthly visitors (12 months): {MONTHLY_VISITORS}")
print(f"Weekly visitors for {SAMPLE_MONTH}: {weekly_sample}")
print()


def section(title, desc):
    print("-" * 70)
    print(f"{title}")
    print(f"  desc: {desc}")
    print("-" * 70)


# ---------------------------------------------------------------
# 2. mean() — arithmetic average
# ---------------------------------------------------------------
section("mean()", "arithmetic average of all data points")
print(f"  Monthly avg visitors           : {stats.mean(MONTHLY_VISITORS):.2f}")
print(f"  {SAMPLE_MONTH} weekly avg visitors        : {stats.mean(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 3. median() — middle value when data is sorted (robust to outliers,
#    e.g. that Dec holiday spike won't skew this like mean() does)
# ---------------------------------------------------------------
section("median()", "middle value of sorted data; resistant to outlier spikes")
print(f"  Monthly median visitors         : {stats.median(MONTHLY_VISITORS)}")
print(f"  {SAMPLE_MONTH} weekly median visitors       : {stats.median(weekly_sample)}")
print()

# ---------------------------------------------------------------
# 4. median_low() / median_high() — bonus pair, useful when you need
#    an *actual observed* data point instead of an averaged midpoint
# ---------------------------------------------------------------
section("median_low() / median_high()", "lower/upper of the two middle values (always a real data point, unlike median())")
print(f"  Monthly median_low / median_high : {stats.median_low(MONTHLY_VISITORS)} / {stats.median_high(MONTHLY_VISITORS)}")
print()

# ---------------------------------------------------------------
# 5. mode() — single most common value
# ---------------------------------------------------------------
section("mode()", "single most frequently occurring value")
try:
    print(f"  Monthly mode                    : {stats.mode(MONTHLY_VISITORS)}")
except stats.StatisticsError as e:
    print(f"  Monthly mode                    : no unique mode ({e})")
print()

# ---------------------------------------------------------------
# 6. multimode() — ALL values tied for most common (mode() only gives one)
# ---------------------------------------------------------------
section("multimode()", "list of all values tied for highest frequency")
print(f"  Monthly multimode                : {stats.multimode(MONTHLY_VISITORS)}")
# Rounding weekly numbers to nearest thousand to force real ties, showing
# how you'd bucket GA4 traffic into "traffic tiers" before finding repeats
buckets = [round(v, -3) for v in weekly_sample]
print(f"  {SAMPLE_MONTH} weekly buckets (rounded k)     : {buckets}")
print(f"  {SAMPLE_MONTH} weekly multimode (on buckets)  : {stats.multimode(buckets)}")
print()

# ---------------------------------------------------------------
# 7. variance() — sample variance (data = a SAMPLE of a bigger population,
#    e.g. these 12 months are a sample of "all months this site will ever have")
# ---------------------------------------------------------------
section("variance()", "sample variance — average squared deviation from mean, n-1 denominator")
print(f"  Monthly sample variance          : {stats.variance(MONTHLY_VISITORS):.2f}")
print(f"  {SAMPLE_MONTH} weekly sample variance        : {stats.variance(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 8. stdev() — sample standard deviation (sqrt of variance(); same units
#    as visitor counts, so it's directly interpretable, unlike variance)
# ---------------------------------------------------------------
section("stdev()", "sample standard deviation — spread of data in original units")
print(f"  Monthly sample stdev             : {stats.stdev(MONTHLY_VISITORS):.2f}")
print(f"  {SAMPLE_MONTH} weekly sample stdev            : {stats.stdev(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 9. pvariance() — POPULATION variance (use when your data IS the whole
#    population, e.g. "all 12 months of THIS specific year" - closed set)
# ---------------------------------------------------------------
section("pvariance()", "population variance — average squared deviation, n denominator (whole population, not a sample)")
print(f"  Monthly population variance      : {stats.pvariance(MONTHLY_VISITORS):.2f}")
print(f"  {SAMPLE_MONTH} weekly population variance     : {stats.pvariance(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 10. pstdev() — population standard deviation (sqrt of pvariance())
# ---------------------------------------------------------------
section("pstdev()", "population standard deviation — spread of the whole population, original units")
print(f"  Monthly population stdev         : {stats.pstdev(MONTHLY_VISITORS):.2f}")
print(f"  {SAMPLE_MONTH} weekly population stdev        : {stats.pstdev(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# BONUS (not in your list, but common in the same module — quick look)
# ---------------------------------------------------------------
section("quantiles()", "cut points that divide data into equal-probability groups (e.g. quartiles)")
print(f"  Monthly quartiles (n=4)          : {stats.quantiles(MONTHLY_VISITORS, n=4)}")
print()

section("harmonic_mean()", "reciprocal-based average; good for rates (e.g. avg session duration, conversion rate blends)")
print(f"  Monthly harmonic mean            : {stats.harmonic_mean(MONTHLY_VISITORS):.2f}")
print()

# ---------------------------------------------------------------
# 11. PUT IT ALL TOGETHER — a per-month summary "pipeline" pass,
#     the kind of row you'd insert into Postgres/ClickHouse as a
#     monthly analytics summary table.
# ---------------------------------------------------------------
print("=" * 70)
print("PER-MONTH SUMMARY TABLE (weekly stats rolled up per month)")
print("=" * 70)
header = f"{'Month':<5}{'Mean':>9}{'Median':>9}{'Stdev':>9}{'PStdev':>9}{'Var':>10}"
print(header)
print("-" * len(header))
for month in MONTH_NAMES:
    weeks = WEEKLY_VISITORS[month]
    row_mean = stats.mean(weeks)
    row_median = stats.median(weeks)
    row_stdev = stats.stdev(weeks) if len(weeks) > 1 else 0
    row_pstdev = stats.pstdev(weeks)
    row_var = stats.variance(weeks) if len(weeks) > 1 else 0
    print(f"{month:<5}{row_mean:>9.1f}{row_median:>9.1f}{row_stdev:>9.1f}{row_pstdev:>9.1f}{row_var:>10.1f}")