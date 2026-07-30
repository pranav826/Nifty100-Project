import sqlite3
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analytics.peer import generate_peer_comparison

import pandas as pd
import yaml

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "db" / "nifty100.db"
CONFIG_PATH = PROJECT_ROOT / "config" / "screener_config.yaml"


# =====================================================
# Load Financial Ratios
# =====================================================

def load_master_dataframe():
    """
    Load and merge all tables required for the screener.
    """

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    market = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            pe_ratio,
            pb_ratio,
            dividend_yield_pct
        FROM market_cap
        """,
        conn
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector,
            sub_sector
        FROM sectors
        """,
        conn
    )

    conn.close()
    print("\n========== RATIOS ==========")
    print(ratios.head(3))

    print("\n========== MARKET ==========")
    print(market.head(3))

    print("\n========== RATIOS YEARS ==========")
    print(ratios["year"].unique()[:10])

    print("\n========== MARKET YEARS ==========")
    print(market["year"].unique()[:10])

    # Merge financial ratios with market data
    df = ratios.merge(
        market,
        on=["company_id", "year"],
        how="left"
    )

    # Merge sector information
    df = df.merge(
    sectors,
    on="company_id",
    how="left"
)

# ---------------------------------------
# Keep only latest financial year
# One record per company
# ---------------------------------------

    df = (
        df.sort_values("year")
            .groupby("company_id", as_index=False)
            .tail(1)
            .reset_index(drop=True)
        )

    return df


# =====================================================
# Load Screener Configuration
# =====================================================

def load_screener_config():
    """
    Load analyst editable screener configuration.
    """

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    return config


# =====================================================
# Apply Threshold Filters
# =====================================================

def apply_filters(df, filters):
    """
    Apply threshold filters to the screener dataframe.
    """

    filtered = df.copy()

    # --------------------------
    # ROE
    # --------------------------
    if filters.get("roe_min") is not None:
        filtered = filtered[
            filtered["return_on_equity_pct"] >= filters["roe_min"]
        ]

    # --------------------------
    # Debt / Equity
    # Skip Financials
    # --------------------------
    if filters.get("de_max") is not None:

        financials = filtered[
            filtered["broad_sector"] == "Financials"
        ]

        others = filtered[
            filtered["broad_sector"] != "Financials"
        ]

        others = others[
            others["debt_to_equity"] <= filters["de_max"]
        ]

        filtered = pd.concat(
            [financials, others],
            ignore_index=True
        )

    # --------------------------
    # Free Cash Flow
    # --------------------------
    if filters.get("fcf_min") is not None:

        filtered = filtered[
            filtered["free_cash_flow_cr"] >= filters["fcf_min"]
        ]

    # --------------------------
    # Revenue CAGR
    # --------------------------
    if filters.get("revenue_cagr_5yr_min") is not None:

        filtered = filtered[
            filtered["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]
        ]

    # --------------------------
    # PAT CAGR
    # --------------------------
    if filters.get("pat_cagr_5yr_min") is not None:

        filtered = filtered[
            filtered["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]
        ]

    # --------------------------
    # Operating Margin
    # --------------------------
    if filters.get("opm_min") is not None:

        filtered = filtered[
            filtered["operating_profit_margin_pct"] >= filters["opm_min"]
        ]

    # --------------------------
    # PE
    # --------------------------
    if filters.get("pe_max") is not None:

        filtered = filtered[
            filtered["pe_ratio"] <= filters["pe_max"]
        ]

    # --------------------------
    # PB
    # --------------------------
    if filters.get("pb_max") is not None:

        filtered = filtered[
            filtered["pb_ratio"] <= filters["pb_max"]
        ]

    # --------------------------
    # Dividend Yield
    # --------------------------
    if filters.get("dividend_yield_min") is not None:

        filtered = filtered[
            filtered["dividend_yield_pct"] >= filters["dividend_yield_min"]
        ]

    # --------------------------
    # Interest Coverage
    # Debt Free = Infinity
    # --------------------------
    if filters.get("icr_min") is not None:

        icr = filtered["interest_coverage"].replace(
            "Debt Free",
            float("inf")
        )

        icr = pd.to_numeric(
            icr,
            errors="coerce"
        )

        filtered = filtered[
            icr >= filters["icr_min"]
        ]

    # --------------------------
    # Market Cap
    # --------------------------
    if filters.get("market_cap_min") is not None:

        filtered = filtered[
            filtered["market_cap_crore"] >= filters["market_cap_min"]
        ]

    # --------------------------
    # EPS CAGR
    # --------------------------
    if filters.get("eps_cagr_min") is not None:

        filtered = filtered[
            filtered["eps_cagr_5yr"] >= filters["eps_cagr_min"]
        ]

    # --------------------------
    # Asset Turnover
    # --------------------------
    if filters.get("asset_turnover_min") is not None:

        filtered = filtered[
            filtered["asset_turnover"] >= filters["asset_turnover_min"]
        ]

    # Sort by composite score
    if "composite_quality_score" in filtered.columns:

        filtered = filtered.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    return filtered

def run_preset(preset_name):
    """
    Execute a predefined screener.
    """

    df = load_master_dataframe()

    config = load_screener_config()

    preset = config["presets"][preset_name]

    return apply_filters(df, preset)


def run_all_presets():

    config = load_screener_config()

    results = {}

    for preset in config["presets"]:

        results[preset] = run_preset(preset)

    return results


    # --------------------------
    # ROE
    # --------------------------
    if filters.get("roe_min") is not None:
        filtered_df = filtered_df[
            filtered_df["return_on_equity_pct"] >= filters["roe_min"]
        ]

    # --------------------------
    # Debt to Equity
    # Skip Financial sector
    # --------------------------
    if filters.get("de_max") is not None:

        if "broad_sector" in filtered_df.columns:

            financials = filtered_df[
                filtered_df["broad_sector"] == "Financials"
            ]

            others = filtered_df[
                filtered_df["broad_sector"] != "Financials"
            ]

            others = others[
                others["debt_to_equity"] <= filters["de_max"]
            ]

            filtered_df = pd.concat(
                [financials, others],
                ignore_index=True
            )

        else:

            filtered_df = filtered_df[
                filtered_df["debt_to_equity"] <= filters["de_max"]
            ]

    # --------------------------
    # Free Cash Flow
    # --------------------------
    if filters.get("fcf_min") is not None:

        filtered_df = filtered_df[
            filtered_df["free_cash_flow_cr"] >= filters["fcf_min"]
        ]

    # --------------------------
    # Revenue CAGR
    # --------------------------
    if filters.get("revenue_cagr_5yr_min") is not None:

        filtered_df = filtered_df[
            filtered_df["revenue_cagr_5yr"] >= filters["revenue_cagr_5yr_min"]
        ]

    # --------------------------
    # PAT CAGR
    # --------------------------
    if filters.get("pat_cagr_5yr_min") is not None:

        filtered_df = filtered_df[
            filtered_df["pat_cagr_5yr"] >= filters["pat_cagr_5yr_min"]
        ]

    # --------------------------
    # Operating Margin
    # --------------------------
    if filters.get("opm_min") is not None:

        filtered_df = filtered_df[
            filtered_df["operating_profit_margin_pct"] >= filters["opm_min"]
        ]

    # --------------------------
    # Interest Coverage
    # Debt Free always passes
    # --------------------------
    if filters.get("icr_min") is not None:

        icr = filtered_df["interest_coverage"].copy()

        icr = icr.replace("Debt Free", float("inf"))

        icr = pd.to_numeric(
            icr,
            errors="coerce"
        )

        filtered_df = filtered_df[
            icr >= filters["icr_min"]
        ]

    # ------------------------------------------------
    # Remaining filters will be added once
    # database schema is verified
    # ------------------------------------------------

    return filtered_df


def export_screeners(results, peer_df):

    output_path = PROJECT_ROOT / "output" / "screener_output.xlsx"

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl"
    ) as writer:

        for name, df in results.items():

            df.to_excel(
                writer,
                sheet_name=name[:31],
                index=False
            )

        peer_df.to_excel(
            writer,
            sheet_name="Peer Comparison",
            index=False
        )

    print("\nExcel exported successfully.")

# =====================================================
# Screener Engine
# =====================================================

def run_screener():

    ratios = load_master_dataframe()

    config = load_screener_config()

    filters = config["filters"]

    result = apply_filters(
        ratios,
        filters
    )

    if "composite_quality_score" in result.columns:
        result = result.sort_values(
            by="composite_quality_score",
            ascending=False
        )

    return result


# =====================================================
# Test
# =====================================================
if __name__ == "__main__":

    df = load_master_dataframe()

    presets = run_all_presets()

    from analytics.peer import generate_peer_comparison

    peer = generate_peer_comparison(df, "TCS")

    export_screeners(
        presets,
        peer
    )

    print(peer.head())