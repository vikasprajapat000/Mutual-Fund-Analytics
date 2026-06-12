import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup styling
plt.style.use('seaborn-v0_8-darkgrid')
BASE_RPT = r'd:\Mutual Fund Analytic\Mutual-Fund-Analytics\reports'
os.makedirs(BASE_RPT, exist_ok=True)

def draw_architecture():
    """Draw a clean, professional architecture block diagram."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    ax.axis('off')
    
    # Define steps and colors
    steps = [
        "Raw Data",
        "ETL Ingestion",
        "Data Cleaning",
        "SQLite Database",
        "EDA Analysis",
        "Performance Analytics",
        "Advanced Analytics",
        "Power BI Dashboard",
        "Final Report"
    ]
    
    # Harmonic dark-mode style colors
    colors = [
        "#1e293b", # dark slate
        "#0f766e", # teal
        "#0369a1", # light blue
        "#1d4ed8", # royal blue
        "#6d28d9", # purple
        "#a21caf", # magenta
        "#be123c", # rose
        "#b45309", # amber
        "#15803d"  # green
    ]
    
    # Draw boxes
    box_width = 7.5
    box_height = 0.8
    y_start = 8.5
    y_gap = 1.0
    
    for i, (step, color) in enumerate(zip(steps, colors)):
        y = y_start - i * y_gap
        # Rectangle
        rect = patches.FancyBboxPatch(
            (5 - box_width/2, y), box_width, box_height,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor="none", alpha=0.9
        )
        ax.add_patch(rect)
        
        # Text
        ax.text(
            5, y + box_height/2, f"{i+1}. {step}",
            color="white", fontsize=11, fontweight="bold",
            ha="center", va="center"
        )
        
        # Down arrow (except for the last box)
        if i < len(steps) - 1:
            arrow_y = y - 0.1
            ax.annotate(
                "",
                xy=(5, arrow_y - 0.1),
                xytext=(5, arrow_y + 0.1),
                arrowprops=dict(
                    arrowstyle="->",
                    color="#64748b",
                    lw=2,
                    mutation_scale=15
                )
            )
            
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 10)
    plt.title("Mutual Fund Analytics - End-to-End Pipeline Architecture", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_RPT, 'project_architecture.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Generated: reports/project_architecture.png")

def generate_nav_trend():
    """Plot static NAV trend for top mutual funds."""
    # Paths
    processed_dir = r'd:\Mutual Fund Analytic\Mutual-Fund-Analytics\data\processed'
    nav_path = os.path.join(processed_dir, '02_nav_history_cleaned.csv')
    fund_path = os.path.join(processed_dir, '01_fund_master_cleaned.csv')
    
    if not os.path.exists(nav_path) or not os.path.exists(fund_path):
        print("Required CSV files for NAV trend do not exist yet. Run cleaning script first.")
        return
        
    nav_df = pd.read_csv(nav_path, parse_dates=['date'])
    fund_master = pd.read_csv(fund_path)
    
    # Pick a few key funds to show
    target_funds = {
        119551: 'SBI Bluechip Fund',
        120503: 'ICICI Prudential Bluechip',
        118632: 'Nippon India Large Cap',
        119092: 'Axis Bluechip Fund',
        120841: 'Kotak Bluechip Fund'
    }
    
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    
    for code, label in target_funds.items():
        fund_nav = nav_df[nav_df['amfi_code'] == code].sort_values('date')
        if not fund_nav.empty:
            ax.plot(fund_nav['date'], fund_nav['nav'], label=label, linewidth=2)
            
    ax.set_title('Historical NAV Trend (Normalized Comparison)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Net Asset Value (NAV)', fontsize=12)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_RPT, 'nav_trend.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Generated: reports/nav_trend.png")

if __name__ == "__main__":
    draw_architecture()
    generate_nav_trend()
