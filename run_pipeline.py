"""
Mutual Fund Analytics - Master Pipeline Runner
Orchestrates and executes all data engineering, database loading,
analytical computation, plot generation, and final report compiling phases.

Usage:
    python run_pipeline.py
"""

import os
import subprocess
import sys


def run_step(command_list: list[str], description: str) -> bool:
    """
    Run a pipeline step as a subprocess and log its outcome.

    Args:
        command_list (list): Command to run.
        description (str): Description of the step.

    Returns:
        bool: True if step completed with exit code 0, False otherwise.
    """
    print("=" * 70)
    print(f" RUNNING: {description}")
    print("=" * 70)
    
    try:
        # Run process, pipe output to terminal in real time
        result = subprocess.run(command_list, check=True)
        print(f"\n[OK] Completed successfully: {description}\n")
        return True
    except subprocess.CalledProcessError as err:
        print(f"\n[FAIL] Step failed with exit code {err.returncode}: {description}\n")
        return False
    except Exception as exc:
        print(f"\n[FAIL] Step failed with unexpected error: {exc}\n")
        return False


def main() -> None:
    """Orchestrate and execute all steps of the mutual fund analytics pipeline."""
    steps = [
        # 1. Ingestion Profile Scan
        {"cmd": [sys.executable, "data_ingestion.py"], "desc": "Raw Data Profiler"},
        
        # 2. Live API Fetch
        {"cmd": [sys.executable, "live_nav_fetch.py"], "desc": "Live NAV API Fetcher"},
        
        # 3. Clean and Load SQLite DB
        {"cmd": [sys.executable, os.path.join("scripts", "day2_clean_and_load.py")], "desc": "Data Cleaning & SQLite Loader"},
        
        # 4. Advanced Risk & Performance Analytics
        {"cmd": [sys.executable, os.path.join("scripts", "run_day6_analytics.py")], "desc": "Day 6 Advanced Analytics Engine"},
        
        # 5. Generate Extra Visualizations
        {"cmd": [sys.executable, os.path.join("scripts", "generate_extra_plots.py")], "desc": "Static Charts & Diagram Generator"},
        
        # 6. Compile Final PDF Report
        {"cmd": [sys.executable, os.path.join("scripts", "generate_pdf_report.py")], "desc": "20-Page PDF Report Compiler"},
        
        # 7. Compile PowerPoint Presentation
        {"cmd": [sys.executable, os.path.join("scripts", "generate_pptx.py")], "desc": "12-Slide PowerPoint Deck Compiler"},
    ]

    print("+" + "=" * 68 + "+")
    print("|             MUTUAL FUND ANALYTICS - END-TO-END PIPELINE            |")
    print("|                     Bluestock Capstone Project                     |")
    print("+" + "=" * 68 + "+")
    print()

    summary = []
    success_count = 0

    for step in steps:
        success = run_step(step["cmd"], step["desc"])
        status = "PASSED" if success else "FAILED"
        summary.append((step["desc"], status))
        if success:
            success_count += 1
        else:
            # Stop pipeline if a critical stage fails
            if step["desc"] in ["Data Cleaning & SQLite Loader", "Day 6 Advanced Analytics Engine"]:
                print("CRITICAL: Pipeline halted due to core analytics step failure.\n")
                break

    # Final summary display
    print("=" * 70)
    print("                        PIPELINE EXECUTION SUMMARY")
    print("=" * 70)
    for desc, status in summary:
        print(f"  {desc:<45} : [{status}]")
    print("=" * 70)

    if success_count == len(steps):
        print("SUCCESS: All pipeline steps executed successfully.")
        print("Deliverables Generated:")
        print("  - SQLite Database : data/db/bluestock_mf.db")
        print("  - Scorecard CSV   : reports/fund_scorecard.csv")
        print("  - VaR/CVaR CSV    : reports/var_cvar_report.csv")
        print("  - PDF Report      : reports/Final_Report.pdf (20 pages)")
        print("  - PowerPoint Deck : presentation/Bluestock_MF_Presentation.pptx (12 slides)")
        print()
    else:
        print("WARNING: Some pipeline steps failed. Please check the logs above.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
