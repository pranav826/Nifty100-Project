import pandas as pd


def generate_peer_comparison(df, company_id):
    """
    Generate peer comparison for a company within its sector.
    """

    company = df[df["company_id"] == company_id]

    if company.empty:
        raise ValueError(f"{company_id} not found.")

    sector = company.iloc[0]["broad_sector"]

    peers = (
        df[df["broad_sector"] == sector]
        .copy()
        .sort_values(
            "composite_quality_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    peers["sector_rank"] = peers.index + 1

    return peers