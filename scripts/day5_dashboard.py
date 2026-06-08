"""
=============================================================
  DAY 5  --  Bluestock Mutual Fund Dashboard
  Generates:
    data/processed/  -> all required cleaned CSVs
    dashboard/       -> screenshots + Dashboard.pdf
=============================================================
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter
import matplotlib.patheffects as pe
from datetime import datetime

warnings.filterwarnings("ignore")

# ── Colour Palette (Bluestock Blue Theme) ─────────────────────────────────────
BG       = "#0D1B2A"   # dark navy background
CARD_BG  = "#112240"   # card / panel background
ACCENT1  = "#1A6FBF"   # primary blue
ACCENT2  = "#4FC3F7"   # light cyan-blue
ACCENT3  = "#00C9FF"   # highlight cyan
GOLD     = "#F5A623"   # accent gold
WHITE    = "#E8F4FD"   # near-white text
MUTED    = "#7FAACC"   # muted blue
GRID_C   = "#1E3A5F"   # subtle grid lines
GREEN    = "#2ECC71"
RED      = "#E74C3C"

PALETTE  = [ACCENT1, ACCENT2, ACCENT3, GOLD, "#9B59B6", GREEN, "#E67E22", RED,
            "#1ABC9C", "#3498DB", "#F39C12", "#E91E63"]

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC    = os.path.join(BASE, "data", "processed")
REPORTS = os.path.join(BASE, "reports")
DASH    = os.path.join(BASE, "dashboard")
SHOTS   = os.path.join(DASH, "screenshots")

for d in [DASH, SHOTS]:
    os.makedirs(d, exist_ok=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt_crore(x, pos=None):
    if abs(x) >= 1e5:
        return f"{x/1e5:.1f}L Cr"
    elif abs(x) >= 1e3:
        return f"{x/1e3:.0f}K Cr"
    return f"{x:.0f} Cr"

def fmt_k(x, pos=None):
    if abs(x) >= 1e6: return f"{x/1e6:.1f}M"
    if abs(x) >= 1e3: return f"{x/1e3:.0f}K"
    return f"{x:.0f}"

def set_dark_ax(ax):
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=WHITE, labelsize=7)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.title.set_color(WHITE)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.grid(color=GRID_C, linewidth=0.4, linestyle="--", alpha=0.6)

def add_logo_watermark(fig):
    fig.text(0.012, 0.97, "BLUESTOCK", fontsize=15, fontweight="bold",
             color=ACCENT3, va="top", ha="left", alpha=0.95,
             path_effects=[pe.withStroke(linewidth=2, foreground=BG)])
    fig.text(0.012, 0.962, "Mutual Fund Analytics", fontsize=6.5,
             color=MUTED, va="top", ha="left")
    fig.text(0.988, 0.97, f"Generated: {datetime.now().strftime('%d %b %Y')}",
             fontsize=6, color=MUTED, va="top", ha="right")

def kpi_card(fig, rect, label, value, sub="", delta=None, delta_pos=True):
    """Draw a KPI card on figure using axes coordinates."""
    ax = fig.add_axes(rect)
    ax.set_facecolor(CARD_BG)
    for sp in ax.spines.values():
        sp.set_edgecolor(ACCENT1)
        sp.set_linewidth(1.2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.72, label, ha="center", va="center",
            fontsize=7, color=MUTED, transform=ax.transAxes)
    ax.text(0.5, 0.42, value, ha="center", va="center",
            fontsize=16, fontweight="bold", color=WHITE, transform=ax.transAxes)
    if sub:
        ax.text(0.5, 0.18, sub, ha="center", va="center",
                fontsize=6.5, color=GOLD, transform=ax.transAxes)

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Generate required CSVs
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  STEP 1: Generating required CSV files")
print("=" * 60)

fund_master  = pd.read_csv(os.path.join(PROC, "01_fund_master_cleaned.csv"))
nav_history  = pd.read_csv(os.path.join(PROC, "02_nav_history_cleaned.csv"))
aum_src      = pd.read_csv(os.path.join(PROC, "03_aum_by_fund_house_cleaned.csv"))
sip_src      = pd.read_csv(os.path.join(PROC, "04_monthly_sip_inflows_cleaned.csv"))
cat_inflows  = pd.read_csv(os.path.join(PROC, "05_category_inflows_cleaned.csv"))
folio_src    = pd.read_csv(os.path.join(PROC, "06_industry_folio_count_cleaned.csv"))
scheme_perf  = pd.read_csv(os.path.join(PROC, "07_scheme_performance_cleaned.csv"))
investor_txn = pd.read_csv(os.path.join(PROC, "08_investor_transactions_cleaned.csv"))
benchmark    = pd.read_csv(os.path.join(PROC, "10_benchmark_indices_cleaned.csv"))
scorecard_df = pd.read_csv(os.path.join(REPORTS, "fund_scorecard.csv"))
alpha_beta_df= pd.read_csv(os.path.join(REPORTS, "alpha_beta.csv"))

print("  [OK] All source files loaded")

# 1. fund_master_cleaned.csv
fm = fund_master.copy()
latest_folio = folio_src.iloc[-1]["total_folios_crore"] * 1e7
fm["folios"]   = int(latest_folio / len(fm))
fm["plan_type"]= fm["plan"]
fm.to_csv(os.path.join(PROC, "fund_master_cleaned.csv"), index=False)
print(f"  [OK] fund_master_cleaned.csv  ({len(fm)} rows)")

# 2. nav_history_cleaned.csv
nav = nav_history.copy()
nav["date"]  = pd.to_datetime(nav["date"])
nav["year"]  = nav["date"].dt.year
nav["month"] = nav["date"].dt.to_period("M").astype(str)
nav.to_csv(os.path.join(PROC, "nav_history_cleaned.csv"), index=False)
print(f"  [OK] nav_history_cleaned.csv  ({len(nav)} rows)")

# 3. investor_transactions_cleaned.csv
txn = investor_txn.copy()
txn["transaction_date"] = pd.to_datetime(txn["transaction_date"])
txn["year"]  = txn["transaction_date"].dt.year
txn["month"] = txn["transaction_date"].dt.to_period("M").astype(str)
txn.to_csv(os.path.join(PROC, "investor_transactions_cleaned.csv"), index=False)
print(f"  [OK] investor_transactions_cleaned.csv  ({len(txn)} rows)")

# 4. scheme_performance_cleaned.csv
sp = scheme_perf.copy()
sp.to_csv(os.path.join(PROC, "scheme_performance_cleaned.csv"), index=False)
print(f"  [OK] scheme_performance_cleaned.csv  ({len(sp)} rows)")

# 5. aum_history_cleaned.csv
aum = aum_src.copy().rename(columns={"aum_crore": "aum"})
aum["date"]  = pd.to_datetime(aum["date"])
aum["year"]  = aum["date"].dt.year
aum["month"] = aum["date"].dt.to_period("M").astype(str)
aum.to_csv(os.path.join(PROC, "aum_history_cleaned.csv"), index=False)
print(f"  [OK] aum_history_cleaned.csv  ({len(aum)} rows)")

# 6. sip_inflows_cleaned.csv
sip = sip_src.copy().rename(columns={"sip_inflow_crore": "sip_amount"})
sip["month"] = pd.to_datetime(sip["month"])
sip["year"]  = sip["month"].dt.year
sip["month_str"] = sip["month"].dt.to_period("M").astype(str)
sip.to_csv(os.path.join(PROC, "sip_inflows_cleaned.csv"), index=False)
print(f"  [OK] sip_inflows_cleaned.csv  ({len(sip)} rows)")

# 7. investor_demographics_cleaned.csv
demo = (
    txn.groupby(["investor_id", "age_group", "gender", "city_tier", "annual_income_lakh"])
    .agg(total_invested=("amount_inr", "sum"),
         num_transactions=("amount_inr", "count"),
         avg_sip_amount=("amount_inr", "mean"))
    .reset_index()
)
demo.to_csv(os.path.join(PROC, "investor_demographics_cleaned.csv"), index=False)
print(f"  [OK] investor_demographics_cleaned.csv  ({len(demo)} rows)")

# 8. state_distribution_cleaned.csv
state_df = (
    txn.groupby(["state", "transaction_type"])
    .agg(transaction_amount=("amount_inr", "sum"),
         transaction_count=("amount_inr", "count"))
    .reset_index()
)
state_df.to_csv(os.path.join(PROC, "state_distribution_cleaned.csv"), index=False)
print(f"  [OK] state_distribution_cleaned.csv  ({len(state_df)} rows)")

# 9. fund_scorecard.csv (add score + cagr aliases)
sc = scorecard_df.copy()
sc["score"] = sc["composite_score"]
sc["cagr"]  = sc["cagr_3yr"]
sc["fund_name"] = sc["scheme_name"]
sc.to_csv(os.path.join(REPORTS, "fund_scorecard.csv"), index=False)
print(f"  [OK] reports/fund_scorecard.csv  ({len(sc)} rows)")

# 10. alpha_beta.csv
ab = alpha_beta_df.copy()
ab.to_csv(os.path.join(REPORTS, "alpha_beta.csv"), index=False)
print(f"  [OK] reports/alpha_beta.csv  ({len(ab)} rows)")

# ── Pre-compute aggregates used across all pages ───────────────────────────────
total_aum     = aum["aum"].sum()
total_sip     = sip["sip_amount"].sum()
total_folios  = fm["folios"].sum()
total_schemes = fm["amfi_code"].nunique()
avg_score     = sc["score"].mean()

# AUM by year (line chart data)
aum_by_year = aum.groupby("year")["aum"].sum().reset_index()

# AUM by fund house (bar chart)
aum_by_fh = aum.groupby("fund_house")["aum"].sum().reset_index().sort_values("aum")

# SIP trend
sip_trend = sip.sort_values("month")

# Benchmark (Nifty 50)
bench_n50 = benchmark[benchmark["index_name"].str.contains("Nifty 50", na=False)].copy()
bench_n50["date"] = pd.to_datetime(bench_n50["date"])
bench_n50 = bench_n50.sort_values("date")

bench_n100 = benchmark[benchmark["index_name"].str.contains("Nifty 100", na=False)].copy()
bench_n100["date"] = pd.to_datetime(bench_n100["date"])
bench_n100 = bench_n100.sort_values("date")

# Top NAV fund (sample)
sample_amfi = sp["amfi_code"].iloc[0]
nav_sample  = nav[nav["amfi_code"] == sample_amfi].sort_values("date")

# State totals
state_total = txn.groupby("state")["amount_inr"].sum().reset_index().sort_values("amount_inr")
state_top   = state_total.tail(15)

# Transaction type split
txn_type = txn.groupby("transaction_type")["amount_inr"].sum().reset_index()

# Age group
age_sip = (
    txn[txn["transaction_type"] == "SIP"]
    .groupby("age_group")["amount_inr"].mean().reset_index()
    .sort_values("amount_inr", ascending=False)
)

# Monthly txn trend
txn_monthly = txn.groupby("month")["amount_inr"].sum().reset_index().sort_values("month")

# Category inflows heatmap
cat_pivot = cat_inflows.copy()
cat_pivot["month"] = pd.to_datetime(cat_pivot["month"])
cat_pivot["month_label"] = cat_pivot["month"].dt.strftime("%b %Y")
cat_pivot["year"] = cat_pivot["month"].dt.year
cat_pivot = cat_pivot[cat_pivot["year"] >= 2023]
cat_heat = cat_pivot.pivot_table(index="category", columns="month_label",
                                  values="net_inflow_crore", aggfunc="sum")

# Top 5 categories
cat_top5 = cat_inflows.groupby("category")["net_inflow_crore"].sum().reset_index().nlargest(5, "net_inflow_crore")

# Scatter (risk-return)
sp_scatter = sp.dropna(subset=["return_3yr_pct", "std_dev_ann_pct", "aum_crore"])

print("\n  [OK] All aggregates computed\n")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — INDUSTRY OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  PAGE 1: Industry Overview")
print("=" * 60)

fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.suptitle("INDUSTRY OVERVIEW", fontsize=18, fontweight="bold",
             color=ACCENT3, y=0.97, x=0.5)
add_logo_watermark(fig)

# ── 4 KPI Cards ──────────────────────────────────────────────────────────────
card_y = 0.76
card_h = 0.17
card_w = 0.19
gap    = 0.012
start_x= 0.03

kpi_card(fig, [start_x + 0*(card_w+gap), card_y, card_w, card_h],
         "Total AUM", f"Rs {total_aum/1e5:.2f}L Cr", "Assets Under Management")
kpi_card(fig, [start_x + 1*(card_w+gap), card_y, card_w, card_h],
         "Total SIP Inflow", f"Rs {total_sip:,.0f} Cr", "Cumulative SIP")
kpi_card(fig, [start_x + 2*(card_w+gap), card_y, card_w, card_h],
         "Total Folios", f"{total_folios/1e7:.2f} Cr", "Investor Folios")
kpi_card(fig, [start_x + 3*(card_w+gap), card_y, card_w, card_h],
         "Total Schemes", f"{total_schemes}", "Active Schemes")
kpi_card(fig, [start_x + 4*(card_w+gap), card_y, card_w, card_h],
         "Avg Fund Score", f"{avg_score:.1f}", "Composite Score (0-100)")

# ── Line Chart: AUM Trend ─────────────────────────────────────────────────────
ax1 = fig.add_axes([0.03, 0.06, 0.45, 0.60])
set_dark_ax(ax1)
years  = aum_by_year["year"].values
values = aum_by_year["aum"].values / 1e5  # L Cr
ax1.fill_between(years, values, alpha=0.25, color=ACCENT1)
ax1.plot(years, values, color=ACCENT3, linewidth=2.5, marker="o",
         markersize=8, markerfacecolor=GOLD, markeredgecolor=WHITE, zorder=5)
for x, y in zip(years, values):
    ax1.annotate(f"Rs {y:.1f}L Cr", (x, y), textcoords="offset points",
                 xytext=(0, 10), ha="center", fontsize=7.5,
                 color=WHITE, fontweight="bold")
ax1.set_title("Industry AUM Trend (2022-2025)", fontsize=11, fontweight="bold",
              color=WHITE, pad=10)
ax1.set_xlabel("Year", fontsize=8); ax1.set_ylabel("AUM (Lakh Crore)", fontsize=8)
ax1.set_xticks(years)
ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}L"))

# ── Bar Chart: AUM by AMC ──────────────────────────────────────────────────────
ax2 = fig.add_axes([0.53, 0.06, 0.45, 0.60])
set_dark_ax(ax2)
aum_fh_sorted = aum_by_fh.tail(12)
colors_bar = plt.cm.Blues(np.linspace(0.35, 0.9, len(aum_fh_sorted)))
bars = ax2.barh(aum_fh_sorted["fund_house"], aum_fh_sorted["aum"] / 1e3,
                color=colors_bar, edgecolor=ACCENT1, linewidth=0.5)
for bar in bars:
    w = bar.get_width()
    ax2.text(w + 0.3, bar.get_y() + bar.get_height()/2,
             f"{w:.0f}K Cr", va="center", ha="left",
             fontsize=6.5, color=WHITE)
ax2.set_title("AUM by AMC (Top 12 Fund Houses)", fontsize=11,
              fontweight="bold", color=WHITE, pad=10)
ax2.set_xlabel("AUM (Thousand Crore)", fontsize=8)
ax2.set_ylabel("")

plt.savefig(os.path.join(SHOTS, "Industry_Overview.png"),
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  [OK] Industry_Overview.png saved")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — FUND PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
print("  PAGE 2: Fund Performance")

fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.suptitle("FUND PERFORMANCE", fontsize=18, fontweight="bold",
             color=ACCENT3, y=0.97, x=0.5)
add_logo_watermark(fig)

# ── Scatter Plot: Risk vs Return ───────────────────────────────────────────────
ax1 = fig.add_axes([0.03, 0.50, 0.45, 0.43])
set_dark_ax(ax1)
cats = sp_scatter["category"].unique()
cat_colors = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(cats)}
for cat, grp in sp_scatter.groupby("category"):
    sizes = np.clip(grp["aum_crore"] / grp["aum_crore"].max() * 300, 20, 300)
    sc_plot = ax1.scatter(grp["return_3yr_pct"], grp["std_dev_ann_pct"],
                          s=sizes, c=cat_colors[cat], alpha=0.75,
                          edgecolors=WHITE, linewidths=0.3, label=cat, zorder=4)
ax1.set_title("Risk vs Return (3-Year)", fontsize=10, fontweight="bold",
              color=WHITE, pad=8)
ax1.set_xlabel("3-Year Return (%)", fontsize=8)
ax1.set_ylabel("Std Dev / Risk (%)", fontsize=8)
ax1.axhline(sp_scatter["std_dev_ann_pct"].median(), color=GOLD,
            linestyle="--", linewidth=0.8, alpha=0.7)
ax1.axvline(sp_scatter["return_3yr_pct"].median(), color=GOLD,
            linestyle="--", linewidth=0.8, alpha=0.7)
leg = ax1.legend(fontsize=5.5, loc="upper left", framealpha=0.3,
                 labelcolor=WHITE, facecolor=CARD_BG)

# ── NAV vs Benchmark ──────────────────────────────────────────────────────────
ax2 = fig.add_axes([0.53, 0.50, 0.45, 0.43])
set_dark_ax(ax2)
if len(nav_sample) > 0:
    nav_s = nav_sample.tail(500)
    nav_norm = nav_s["nav"] / nav_s["nav"].iloc[0] * 100
    ax2.plot(range(len(nav_norm)), nav_norm.values,
             color=ACCENT3, linewidth=1.8, label="Fund NAV", zorder=4)
if len(bench_n50) > 0:
    n50_s = bench_n50.tail(500)
    n50_norm = n50_s["close_value"] / n50_s["close_value"].iloc[0] * 100
    ax2.plot(range(len(n50_norm)), n50_norm.values,
             color=GOLD, linewidth=1.4, linestyle="--", label="Nifty 50", zorder=3)
if len(bench_n100) > 0:
    n100_s = bench_n100.tail(500)
    n100_norm = n100_s["close_value"] / n100_s["close_value"].iloc[0] * 100
    ax2.plot(range(min(len(n100_norm), 500)), n100_norm.values[:500],
             color="#9B59B6", linewidth=1.2, linestyle="-.", label="Nifty 100", zorder=2)
ax2.set_title("NAV vs Benchmark (Indexed to 100)", fontsize=10,
              fontweight="bold", color=WHITE, pad=8)
ax2.set_xlabel("Trading Days", fontsize=8)
ax2.set_ylabel("Indexed Value", fontsize=8)
ax2.legend(fontsize=7, framealpha=0.3, labelcolor=WHITE, facecolor=CARD_BG)

# ── Fund Scorecard Table ───────────────────────────────────────────────────────
ax3 = fig.add_axes([0.03, 0.03, 0.94, 0.42])
ax3.set_facecolor(CARD_BG)
ax3.set_xticks([]); ax3.set_yticks([])
for sp_ax in ax3.spines.values():
    sp_ax.set_edgecolor(ACCENT1)

table_df = sc[["scheme_name", "score", "cagr", "sharpe_ratio",
               "alpha_annual", "beta"]].dropna().sort_values("score", ascending=False).head(15)
table_df.columns = ["Fund Name", "Score", "CAGR (3Y%)", "Sharpe", "Alpha", "Beta"]
table_df["Fund Name"] = table_df["Fund Name"].str[:40]
table_df = table_df.round(2)

col_widths = [0.38, 0.10, 0.12, 0.12, 0.12, 0.10]
headers    = list(table_df.columns)
x_pos = [0.01]
for w in col_widths[:-1]:
    x_pos.append(x_pos[-1] + w)

# Header row
for j, (h, x) in enumerate(zip(headers, x_pos)):
    ax3.text(x + col_widths[j]/2, 0.93, h, ha="center", va="center",
             fontsize=7.5, fontweight="bold", color=ACCENT3,
             transform=ax3.transAxes)

# Draw horizontal header line
ax3.axhline(0, xmin=0, xmax=1, color=ACCENT1, linewidth=0.6, alpha=0.7)

row_h = 0.84 / len(table_df)
for i, (_, row) in enumerate(table_df.iterrows()):
    y = 0.86 - i * row_h
    bg_col = "#0e2744" if i % 2 == 0 else CARD_BG
    rect = FancyBboxPatch((0, y - row_h*0.9), 1, row_h*0.88,
                           boxstyle="round,pad=0.002",
                           facecolor=bg_col, edgecolor="none",
                           transform=ax3.transAxes, clip_on=True)
    ax3.add_patch(rect)
    vals = list(row.values)
    for j, (v, x) in enumerate(zip(vals, x_pos)):
        clr = GREEN if j == 1 and float(v) >= 70 else (GOLD if j == 1 else WHITE)
        ax3.text(x + col_widths[j]/2, y - row_h*0.35, str(v),
                 ha="center", va="center", fontsize=6.5,
                 color=clr, transform=ax3.transAxes)
ax3.set_title("Fund Scorecard (Top 15 by Score, sorted DESC)",
              fontsize=10, fontweight="bold", color=WHITE, pad=8)

plt.savefig(os.path.join(SHOTS, "Fund_Performance.png"),
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  [OK] Fund_Performance.png saved")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — INVESTOR ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
print("  PAGE 3: Investor Analytics")

fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.suptitle("INVESTOR ANALYTICS", fontsize=18, fontweight="bold",
             color=ACCENT3, y=0.97, x=0.5)
add_logo_watermark(fig)

# ── State Bar Chart ────────────────────────────────────────────────────────────
ax1 = fig.add_axes([0.03, 0.52, 0.44, 0.41])
set_dark_ax(ax1)
colors_s = plt.cm.cool(np.linspace(0.2, 0.9, len(state_top)))
ax1.barh(state_top["state"], state_top["amount_inr"] / 1e7,
         color=colors_s, edgecolor=ACCENT1, linewidth=0.4)
ax1.set_title("Transaction Amount by State (Top 15)", fontsize=10,
              fontweight="bold", color=WHITE, pad=8)
ax1.set_xlabel("Amount (Crore)", fontsize=8)
ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}Cr"))

# ── Donut Chart ────────────────────────────────────────────────────────────────
ax2 = fig.add_axes([0.53, 0.52, 0.20, 0.41])
ax2.set_facecolor(CARD_BG)
for sp_ax in ax2.spines.values(): sp_ax.set_visible(False)
donut_vals  = txn_type["amount_inr"].values
donut_labs  = txn_type["transaction_type"].values
donut_clrs  = [ACCENT1, ACCENT3, GOLD, "#9B59B6", RED][:len(donut_vals)]
wedges, texts, autotexts = ax2.pie(
    donut_vals, labels=None, colors=donut_clrs,
    autopct="%1.1f%%", startangle=90,
    pctdistance=0.78, wedgeprops=dict(width=0.48, edgecolor=BG, linewidth=1.5)
)
for at in autotexts:
    at.set_fontsize(7.5); at.set_color(WHITE)
ax2.legend(donut_labs, loc="lower center", fontsize=7,
           labelcolor=WHITE, facecolor=CARD_BG, framealpha=0.4,
           bbox_to_anchor=(0.5, -0.08))
ax2.set_title("Transaction Type Split", fontsize=10, fontweight="bold",
              color=WHITE, pad=8)

# ── Age Group Column Chart ──────────────────────────────────────────────────────
ax3 = fig.add_axes([0.76, 0.52, 0.22, 0.41])
set_dark_ax(ax3)
age_colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(age_sip)))
ax3.bar(age_sip["age_group"], age_sip["amount_inr"] / 1e3,
        color=age_colors, edgecolor=ACCENT1, linewidth=0.5)
ax3.set_title("Avg SIP by Age Group", fontsize=10, fontweight="bold",
              color=WHITE, pad=8)
ax3.set_xlabel("Age Group", fontsize=8)
ax3.set_ylabel("Avg SIP (Thousand Rs)", fontsize=8)
plt.setp(ax3.get_xticklabels(), rotation=30, ha="right", fontsize=6.5)

# ── Monthly Transaction Trend ─────────────────────────────────────────────────
ax4 = fig.add_axes([0.03, 0.05, 0.94, 0.40])
set_dark_ax(ax4)
months_plot = txn_monthly["month"].values
amounts     = txn_monthly["amount_inr"].values / 1e7  # Crore
ax4.fill_between(range(len(months_plot)), amounts, alpha=0.20, color=ACCENT2)
ax4.plot(range(len(months_plot)), amounts, color=ACCENT2, linewidth=2,
         marker="o", markersize=4, markerfacecolor=WHITE, zorder=5)
step = max(1, len(months_plot) // 18)
ax4.set_xticks(range(0, len(months_plot), step))
ax4.set_xticklabels(months_plot[::step], rotation=45, ha="right", fontsize=6)
ax4.set_title("Monthly Transaction Trend (Transaction Amount)", fontsize=10,
              fontweight="bold", color=WHITE, pad=8)
ax4.set_xlabel("Month", fontsize=8)
ax4.set_ylabel("Amount (Crore)", fontsize=8)
ax4.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}Cr"))

plt.savefig(os.path.join(SHOTS, "Investor_Analytics.png"),
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  [OK] Investor_Analytics.png saved")

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — SIP & MARKET TRENDS
# ══════════════════════════════════════════════════════════════════════════════
print("  PAGE 4: SIP & Market Trends")

fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
fig.suptitle("SIP & MARKET TRENDS", fontsize=18, fontweight="bold",
             color=ACCENT3, y=0.97, x=0.5)
add_logo_watermark(fig)

# ── Combo Chart: SIP Inflow + Nifty 50 ────────────────────────────────────────
ax1 = fig.add_axes([0.03, 0.52, 0.55, 0.42])
set_dark_ax(ax1)
sip_plot = sip.sort_values("month").dropna(subset=["sip_amount"])
sip_labels = sip_plot["month_str"].values
sip_vals   = sip_plot["sip_amount"].values

x_idx = np.arange(len(sip_vals))
bars = ax1.bar(x_idx, sip_vals, color=ACCENT1, alpha=0.75, width=0.7,
               edgecolor=ACCENT2, linewidth=0.4, label="SIP Inflow (Cr)", zorder=3)

ax1b = ax1.twinx()
ax1b.set_facecolor("none")
if len(bench_n50) > 0:
    n50_monthly = (
        bench_n50.set_index("date")["close_value"]
        .resample("MS").last().reset_index()
    )
    n50_monthly["month_str"] = n50_monthly["date"].dt.to_period("M").astype(str)
    merged = pd.merge(sip_plot[["month_str"]], n50_monthly, on="month_str", how="left")
    n50_vals = merged["close_value"].values
    ax1b.plot(x_idx, n50_vals, color=GOLD, linewidth=2,
              marker="D", markersize=3, label="Nifty 50", zorder=5)
    ax1b.tick_params(colors=GOLD, labelsize=7)
    ax1b.yaxis.label.set_color(GOLD)
    ax1b.set_ylabel("Nifty 50 Level", fontsize=8, color=GOLD)

step = max(1, len(sip_labels) // 14)
ax1.set_xticks(x_idx[::step])
ax1.set_xticklabels(sip_labels[::step], rotation=45, ha="right", fontsize=6)
ax1.set_title("SIP Inflow vs Nifty 50 (2022-2025)", fontsize=10,
              fontweight="bold", color=WHITE, pad=8)
ax1.set_ylabel("SIP Inflow (Crore)", fontsize=8)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax1b.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper left",
           framealpha=0.3, labelcolor=WHITE, facecolor=CARD_BG)

# ── Top 5 Categories Bar Chart ─────────────────────────────────────────────────
ax2 = fig.add_axes([0.63, 0.52, 0.35, 0.42])
set_dark_ax(ax2)
top5_colors = [ACCENT1, ACCENT2, ACCENT3, GOLD, GREEN]
ax2.barh(cat_top5["category"], cat_top5["net_inflow_crore"],
         color=top5_colors, edgecolor=BG, linewidth=0.5)
for i, (v, cat) in enumerate(zip(cat_top5["net_inflow_crore"], cat_top5["category"])):
    ax2.text(v + 20, i, f"{v:,.0f} Cr", va="center",
             fontsize=7, color=WHITE)
ax2.set_title("Top 5 Categories by Net Inflow", fontsize=10,
              fontweight="bold", color=WHITE, pad=8)
ax2.set_xlabel("Net Inflow (Crore)", fontsize=8)

# ── Heatmap: Category x Month ─────────────────────────────────────────────────
ax3 = fig.add_axes([0.03, 0.05, 0.94, 0.42])
set_dark_ax(ax3)
if cat_heat.shape[0] > 0 and cat_heat.shape[1] > 0:
    heat_data = cat_heat.fillna(0)
    cols_to_show = list(heat_data.columns)[:20]
    heat_sub = heat_data[cols_to_show]
    im = ax3.imshow(heat_sub.values, cmap="Blues", aspect="auto",
                    vmin=heat_sub.values.min(), vmax=heat_sub.values.max())
    ax3.set_xticks(range(len(cols_to_show)))
    ax3.set_xticklabels(cols_to_show, rotation=45, ha="right", fontsize=5.5)
    ax3.set_yticks(range(len(heat_sub.index)))
    ax3.set_yticklabels(heat_sub.index, fontsize=7)
    ax3.tick_params(colors=WHITE)
    for i in range(heat_sub.shape[0]):
        for j in range(heat_sub.shape[1]):
            val = heat_sub.values[i, j]
            ax3.text(j, i, f"{val:.0f}", ha="center", va="center",
                     fontsize=5.5, color=WHITE if val < heat_sub.values.max()*0.6 else BG)
    cbar = plt.colorbar(im, ax=ax3, fraction=0.02, pad=0.01)
    cbar.ax.tick_params(colors=WHITE, labelsize=6)
    cbar.set_label("Net Inflow (Crore)", color=WHITE, fontsize=7)
ax3.set_title("Heatmap: Category Net Inflow by Month (Conditional Formatting)",
              fontsize=10, fontweight="bold", color=WHITE, pad=8)

plt.savefig(os.path.join(SHOTS, "SIP_Market_Trends.png"),
            dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("  [OK] SIP_Market_Trends.png saved")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Create Dashboard.pdf  (all 4 pages)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  STEP 3: Creating Dashboard.pdf")
print("=" * 60)

from matplotlib.backends.backend_pdf import PdfPages

pdf_path  = os.path.join(DASH, "Dashboard.pdf")
png_files = [
    ("Industry Overview",   os.path.join(SHOTS, "Industry_Overview.png")),
    ("Fund Performance",    os.path.join(SHOTS, "Fund_Performance.png")),
    ("Investor Analytics",  os.path.join(SHOTS, "Investor_Analytics.png")),
    ("SIP & Market Trends", os.path.join(SHOTS, "SIP_Market_Trends.png")),
]

with PdfPages(pdf_path) as pdf:
    for title, png_path in png_files:
        img_arr = plt.imread(png_path)
        fig = plt.figure(figsize=(20, 11.25), facecolor=BG)
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img_arr)
        ax.axis("off")
        d = pdf.infodict()
        d["Title"]   = "Bluestock MF Dashboard"
        d["Author"]  = "Bluestock Analytics"
        d["Subject"] = "Mutual Fund Analytics - Day 5"
        pdf.savefig(fig, dpi=150, bbox_inches="tight", facecolor=BG)
        plt.close()
        print(f"  [OK] Added page: {title}")

print(f"  [OK] Dashboard.pdf saved -> {pdf_path}")

# ══════════════════════════════════════════════════════════════════════════════
#  FINAL VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  FINAL VERIFICATION — All Deliverables")
print("=" * 60)

deliverables = {
    # CSVs
    "data/processed/fund_master_cleaned.csv":           os.path.join(PROC, "fund_master_cleaned.csv"),
    "data/processed/nav_history_cleaned.csv":           os.path.join(PROC, "nav_history_cleaned.csv"),
    "data/processed/investor_transactions_cleaned.csv": os.path.join(PROC, "investor_transactions_cleaned.csv"),
    "data/processed/scheme_performance_cleaned.csv":    os.path.join(PROC, "scheme_performance_cleaned.csv"),
    "data/processed/aum_history_cleaned.csv":           os.path.join(PROC, "aum_history_cleaned.csv"),
    "data/processed/sip_inflows_cleaned.csv":           os.path.join(PROC, "sip_inflows_cleaned.csv"),
    "data/processed/investor_demographics_cleaned.csv": os.path.join(PROC, "investor_demographics_cleaned.csv"),
    "data/processed/state_distribution_cleaned.csv":    os.path.join(PROC, "state_distribution_cleaned.csv"),
    "reports/fund_scorecard.csv":                       os.path.join(REPORTS, "fund_scorecard.csv"),
    "reports/alpha_beta.csv":                           os.path.join(REPORTS, "alpha_beta.csv"),
    # Dashboard outputs
    "dashboard/Dashboard.pdf":                          os.path.join(DASH, "Dashboard.pdf"),
    "dashboard/screenshots/Industry_Overview.png":      os.path.join(SHOTS, "Industry_Overview.png"),
    "dashboard/screenshots/Fund_Performance.png":       os.path.join(SHOTS, "Fund_Performance.png"),
    "dashboard/screenshots/Investor_Analytics.png":     os.path.join(SHOTS, "Investor_Analytics.png"),
    "dashboard/screenshots/SIP_Market_Trends.png":      os.path.join(SHOTS, "SIP_Market_Trends.png"),
}

all_ok = True
for label, path in deliverables.items():
    exists = os.path.exists(path)
    size   = os.path.getsize(path) if exists else 0
    status = "OK" if exists else "MISSING"
    size_s = f"{size/1024:.1f} KB" if size >= 1024 else f"{size} B"
    print(f"  [{status}]  {label:<55}  {size_s}")
    if not exists:
        all_ok = False

print()
if all_ok:
    print("  ALL DELIVERABLES READY!")
    print()
    print("  Next: Open Power BI Desktop and follow these steps:")
    print("  1. New Blank Report -> Save as: dashboard/bluestock_mf_dashboard.pbix")
    print("  2. Home -> Get Data -> Text/CSV -> load all 10 CSVs above")
    print("  3. Model View -> create 5 relationships (amfi_code, One-to-Many)")
    print("  4. Table View -> New Measure -> add 5 DAX measures")
    print("  5. Build 4 pages (Industry Overview / Fund Performance / Investor")
    print("     Analytics / SIP & Market Trends) using the screenshots as guide")
    print("  6. File -> Save -> File -> Export -> PDF")
else:
    print("  SOME DELIVERABLES MISSING -- check errors above")

print("=" * 60)
print("  Day 5 Script Complete!")
print("=" * 60)
