"""
Profitability Ratio Engine

Reusable financial ratio functions for the Nifty100 analytics pipeline.
"""


def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin (%)
    Formula:
        (Net Profit / Sales) * 100
    """

    if net_profit is None or sales is None or sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin (%)
    Formula:
        (Operating Profit / Sales) * 100
    """

    if operating_profit is None or sales is None or sales == 0:
        return None

    return (operating_profit / sales) * 100


def return_on_equity(net_profit, equity_capital, reserves):
    """
    Return on Equity (ROE) (%)

    Formula:
        Net Profit / (Equity Capital + Reserves) * 100
    """

    if (
        net_profit is None
        or equity_capital is None
        or reserves is None
    ):
        return None

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    operating_profit,
    interest,
    equity_capital,
    reserves,
    borrowings,
):
    """
    Return on Capital Employed (ROCE) (%)

    EBIT = Operating Profit + Interest

    Formula:
        EBIT / (Equity + Reserves + Borrowings) * 100
    """

    if (
        operating_profit is None
        or interest is None
        or equity_capital is None
        or reserves is None
        or borrowings is None
    ):
        return None

    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    ebit = operating_profit + interest

    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """
    Return on Assets (ROA) (%)

    Formula:
        (Net Profit / Total Assets) * 100
    """

    if (
        net_profit is None
        or total_assets is None
        or total_assets == 0
    ):
        return None

    return (net_profit / total_assets) * 100

def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt-to-Equity Ratio
    """

    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity is None or equity <= 0:
        return None

    return borrowings / equity


def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    Interest Coverage Ratio
    """

    if interest is None or interest == 0:
        return None

    ebit = operating_profit + other_income

    return ebit / interest


def net_debt(borrowings, investments):
    """
    Net Debt
    """

    if borrowings is None:
        borrowings = 0

    if investments is None:
        investments = 0

    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover Ratio
    """

    if total_assets is None or total_assets == 0:
        return None

    return sales / total_assets