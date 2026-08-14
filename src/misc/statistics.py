"""
=====================================================================
 statistics MODULE — COMPLETE WALKTHROUGH (Python 3.14, 20 functions)
 Applied to GA4-style time series visitor data
=====================================================================

Verified against the official docs: https://docs.python.org/3/library/statistics.html

All 20 module-level functions, in doc order:
  1.  mean()
  2.  fmean()
  3.  geometric_mean()
  4.  harmonic_mean()
  5.  kde()              <- new in 3.13
  6.  kde_random()       <- new in 3.13
  7.  median()
  8.  median_low()
  9.  median_high()
  10. median_grouped()
  11. mode()
  12. multimode()
  13. quantiles()
  14. pstdev()
  15. pvariance()
  16. stdev()
  17. variance()
  18. covariance()        <- needs a SECOND data series
  19. correlation()       <- needs a SECOND data series
  20. linear_regression() <- needs a SECOND data series

Bonus (separate class, not a module function): NormalDist

Data shape used throughout:
  MONTHLY_VISITORS -> array, 12 monthly totals (Jan-Dec)
  WEEKLY_VISITORS  -> dict, {month: [4 weekly totals]}
  MONTHLY_CONVERSIONS -> array, 12 monthly totals, paired 1:1 with
                         MONTHLY_VISITORS (needed for covariance/
                         correlation/linear_regression — those compare
                         TWO series, e.g. "does more traffic -> more
                         conversions", the kind of check you'd run
                         before writing a Postgres/ClickHouse view).
=====================================================================
"""

import sys
import statistics as stats

HAS_KDE = sys.version_info >= (3, 13)  # kde()/kde_random() need 3.13+

# ---------------------------------------------------------------
# 1. THE DATA
# ---------------------------------------------------------------

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

MONTHLY_VISITORS = [
    12500, 11800, 14200, 15100, 16800, 19500,
    21000, 20500, 18700, 17200, 15600, 22300,  # Dec spike = holiday traffic
]

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
    "Dec": [4200, 4300, 6500, 7300],  # week 3-4 = Black Friday/Xmas surge
}

# A second, correlated series -> "goal completions" per month.
# Needed for covariance() / correlation() / linear_regression().
MONTHLY_CONVERSIONS = [
    310, 275, 360, 410, 470, 560,
    640, 610, 540, 480, 400, 700,
]

SAMPLE_MONTH = "Dec"
weekly_sample = WEEKLY_VISITORS[SAMPLE_MONTH]

print("=" * 72)
print("GA4 TIME SERIES — statistics MODULE, ALL 20 FUNCTIONS")
print("=" * 72)
print(f"Monthly visitors (12 months): {MONTHLY_VISITORS}")
print(f"Monthly conversions (12 mo) : {MONTHLY_CONVERSIONS}")
print(f"Weekly visitors for {SAMPLE_MONTH}: {weekly_sample}")
if not HAS_KDE:
    print(f"[note] running on Python {sys.version.split()[0]} — kde()/kde_random()")
    print("       need 3.13+, so those two sections below are skipped/marked.")
print()


def section(n, title, desc):
    print("-" * 72)
    print(f"{n:>2}. {title}")
    print(f"    desc: {desc}")
    print("-" * 72)


# ---------------------------------------------------------------
# 1. mean()
# ---------------------------------------------------------------
section(1, "mean()", "arithmetic average of all data points")
print(f"    Monthly avg visitors      : {stats.mean(MONTHLY_VISITORS):.2f}")
print(f"    {SAMPLE_MONTH} weekly avg visitors   : {stats.mean(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 2. fmean()
# ---------------------------------------------------------------
section(2, "fmean()", "fast, float-based mean; optionally weighted (like mean() but faster, coerces to float)")
print(f"    Monthly fmean             : {stats.fmean(MONTHLY_VISITORS):.2f}")
# weighted example: give Nov/Dec (holiday months) more importance
weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3]
print(f"    Monthly fmean (holiday-weighted): {stats.fmean(MONTHLY_VISITORS, weights):.2f}")
print()

# ---------------------------------------------------------------
# 3. geometric_mean()
# ---------------------------------------------------------------
section(3, "geometric_mean()", "average of a MULTIPLICATIVE process — right tool for month-over-month growth rates")
mom_growth_factors = [
    MONTHLY_VISITORS[i] / MONTHLY_VISITORS[i - 1] for i in range(1, len(MONTHLY_VISITORS))
]
print(f"    Month-over-month growth factors: {[round(g, 3) for g in mom_growth_factors]}")
print(f"    Geometric mean growth factor    : {stats.geometric_mean(mom_growth_factors):.4f}"
      f"  (~{(stats.geometric_mean(mom_growth_factors) - 1) * 100:.2f}% avg MoM growth)")
print()

# ---------------------------------------------------------------
# 4. harmonic_mean()
# ---------------------------------------------------------------
section(4, "harmonic_mean()", "reciprocal-based average — right tool for rates (e.g. blended conversion rate)")
monthly_conv_rate = [c / v for c, v in zip(MONTHLY_CONVERSIONS, MONTHLY_VISITORS)]
print(f"    Monthly conversion rates  : {[round(r, 4) for r in monthly_conv_rate]}")
print(f"    Harmonic mean of rates    : {stats.harmonic_mean(monthly_conv_rate):.4f}")
print()

# ---------------------------------------------------------------
# 5. kde()
# ---------------------------------------------------------------
section(5, "kde()", "Kernel Density Estimation — builds a smooth probability curve from discrete monthly samples (needs Python 3.13+)")
if HAS_KDE:
    kde_fn = stats.kde(MONTHLY_VISITORS, h=1500)
    for x in (12000, 17000, 22000):
        print(f"    density at visitors={x:>6}: {kde_fn(x):.8f}")
else:
    print("    [skipped] requires Python 3.13+; not available in this runtime.")
print()

# ---------------------------------------------------------------
# 6. kde_random()
# ---------------------------------------------------------------
section(6, "kde_random()", "draws random samples FROM the kde() distribution — e.g. simulate plausible 'next month' visitor counts (needs 3.13+)")
if HAS_KDE:
    rand_fn = stats.kde_random(MONTHLY_VISITORS, h=1500, seed=42)
    simulated = [round(rand_fn()) for _ in range(5)]
    print(f"    5 simulated future-month visitor counts: {simulated}")
else:
    print("    [skipped] requires Python 3.13+; not available in this runtime.")
print()

# ---------------------------------------------------------------
# 7. median()
# ---------------------------------------------------------------
section(7, "median()", "middle value of sorted data; resistant to the Dec outlier spike, unlike mean()")
print(f"    Monthly median visitors   : {stats.median(MONTHLY_VISITORS)}")
print(f"    {SAMPLE_MONTH} weekly median         : {stats.median(weekly_sample)}")
print()

# ---------------------------------------------------------------
# 8. median_low()
# ---------------------------------------------------------------
section(8, "median_low()", "with an even count, returns the LOWER of the two middle values (always a real observed point)")
print(f"    Monthly median_low        : {stats.median_low(MONTHLY_VISITORS)}")
print()

# ---------------------------------------------------------------
# 9. median_high()
# ---------------------------------------------------------------
section(9, "median_high()", "with an even count, returns the UPPER of the two middle values (always a real observed point)")
print(f"    Monthly median_high       : {stats.median_high(MONTHLY_VISITORS)}")
print()

# ---------------------------------------------------------------
# 10. median_grouped()
# ---------------------------------------------------------------
section(10, "median_grouped()", "median of CONTINUOUS data grouped into class intervals — treats values as bucket midpoints")
print(f"    Monthly median_grouped (interval=1000): {stats.median_grouped(MONTHLY_VISITORS, interval=1000):.2f}")
print()

# ---------------------------------------------------------------
# 11. mode()
# ---------------------------------------------------------------
section(11, "mode()", "single most frequently occurring value")
try:
    print(f"    Monthly mode              : {stats.mode(MONTHLY_VISITORS)}")
except stats.StatisticsError as e:
    print(f"    Monthly mode              : no unique mode ({e})")
print()

# ---------------------------------------------------------------
# 12. multimode()
# ---------------------------------------------------------------
section(12, "multimode()", "ALL values tied for highest frequency (mode() only returns one)")
buckets = [round(v, -3) for v in weekly_sample]  # bucket to force realistic ties
print(f"    Monthly multimode (raw, all unique) : {stats.multimode(MONTHLY_VISITORS)}")
print(f"    {SAMPLE_MONTH} weekly buckets (nearest 1000)  : {buckets}")
print(f"    {SAMPLE_MONTH} weekly multimode (on buckets)  : {stats.multimode(buckets)}")
print()

# ---------------------------------------------------------------
# 13. quantiles()
# ---------------------------------------------------------------
section(13, "quantiles()", "cut points dividing data into n equal-probability groups (default n=4 -> quartiles)")
print(f"    Monthly quartiles (n=4)   : {stats.quantiles(MONTHLY_VISITORS, n=4)}")
print(f"    Monthly deciles (n=10)    : {[round(q, 1) for q in stats.quantiles(MONTHLY_VISITORS, n=10)]}")
print()

# ---------------------------------------------------------------
# 14. pstdev()
# ---------------------------------------------------------------
section(14, "pstdev()", "population standard deviation — use when your data IS the whole population you care about")
print(f"    Monthly population stdev  : {stats.pstdev(MONTHLY_VISITORS):.2f}")
print(f"    {SAMPLE_MONTH} weekly population stdev: {stats.pstdev(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 15. pvariance()
# ---------------------------------------------------------------
section(15, "pvariance()", "population variance — squared spread, whole-population (n) denominator")
print(f"    Monthly population variance: {stats.pvariance(MONTHLY_VISITORS):.2f}")
print()

# ---------------------------------------------------------------
# 16. stdev()
# ---------------------------------------------------------------
section(16, "stdev()", "sample standard deviation (n-1 denominator) — use when data is a SAMPLE of a bigger population")
print(f"    Monthly sample stdev      : {stats.stdev(MONTHLY_VISITORS):.2f}")
print(f"    {SAMPLE_MONTH} weekly sample stdev    : {stats.stdev(weekly_sample):.2f}")
print()

# ---------------------------------------------------------------
# 17. variance()
# ---------------------------------------------------------------
section(17, "variance()", "sample variance — squared spread, n-1 denominator")
print(f"    Monthly sample variance   : {stats.variance(MONTHLY_VISITORS):.2f}")
print()

# ---------------------------------------------------------------
# 18. covariance()
# ---------------------------------------------------------------
section(18, "covariance()", "how two series move TOGETHER (sign = direction, magnitude depends on units) — visitors vs conversions")
print(f"    Cov(visitors, conversions): {stats.covariance(MONTHLY_VISITORS, MONTHLY_CONVERSIONS):.2f}")
print()

# ---------------------------------------------------------------
# 19. correlation()
# ---------------------------------------------------------------
section(19, "correlation()", "Pearson correlation coefficient, -1..1, unit-free strength of linear relationship")
print(f"    Corr(visitors, conversions): {stats.correlation(MONTHLY_VISITORS, MONTHLY_CONVERSIONS):.4f}")
print()

# ---------------------------------------------------------------
# 20. linear_regression()
# ---------------------------------------------------------------
section(20, "linear_regression()", "fits conversions = slope * visitors + intercept — a 1-line forecasting/trend model")
reg = stats.linear_regression(MONTHLY_VISITORS, MONTHLY_CONVERSIONS)
print(f"    slope={reg.slope:.5f}, intercept={reg.intercept:.2f}")
predicted_next = reg.slope * 24000 + reg.intercept
print(f"    Predicted conversions if next month visitors = 24000: {predicted_next:.0f}")
print()

# ---------------------------------------------------------------
# BONUS: NormalDist — not a module function, a separate class,
# but lives in the same module and is the standard next step once
# you have mean()/stdev() (e.g. "what % of months exceed 20k visitors?")
# ---------------------------------------------------------------
print("=" * 72)
print("BONUS: NormalDist (class, not a module-level function)")
print("=" * 72)
nd = stats.NormalDist.from_samples(MONTHLY_VISITORS)
print(f"desc: models data as a normal distribution; gives pdf/cdf/quantiles/zscore")
print(f"    NormalDist -> mean={nd.mean:.1f}, stdev={nd.stdev:.1f}")
print(f"    P(visitors < 20000)        : {nd.cdf(20000):.4f}")
print(f"    P(visitors > 20000)        : {1 - nd.cdf(20000):.4f}")
print(f"    z-score of Dec (22300)     : {nd.zscore(22300):.3f}")
print()

# ---------------------------------------------------------------
# PIPELINE ROLLUP — per-month summary table (what you'd upsert into
# Postgres/ClickHouse as a monthly analytics_summary row)
# ---------------------------------------------------------------
print("=" * 72)
print("PER-MONTH SUMMARY TABLE (weekly stats rolled up per month)")
print("=" * 72)
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