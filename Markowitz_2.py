"""
Package Import
"""
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import quantstats as qs
import gurobipy as gp
import warnings
import argparse
import sys

"""
Project Setup
"""
warnings.simplefilter(action="ignore", category=FutureWarning)

assets = [
    "SPY",
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
]

# Initialize Bdf and df
Bdf = pd.DataFrame()
for asset in assets:
    raw = yf.download(asset, start="2012-01-01", end="2024-04-01", auto_adjust = False)
    Bdf[asset] = raw['Adj Close']

df = Bdf.loc["2019-01-01":"2024-04-01"]

"""
Strategy Creation

Create your own strategy, you can add parameter but please remain "price" and "exclude" unchanged
"""


class MyPortfolio:
    """
    NOTE: You can modify the initialization function
    """

class MyPortfolio:
    def __init__(self, price, exclude="SPY", lookback=120, top_n=5):
        self.price = price
        self.returns = price.pct_change().fillna(0)
        self.exclude = exclude
        self.lookback = lookback
        self.top_n = top_n

    def calculate_weights(self):
        assets = self.price.columns[self.price.columns != self.exclude]
        self.portfolio_weights = pd.DataFrame(index=self.price.index, columns=self.price.columns)

        idx = self.price.index
        # 每月重平衡
        rebal_dates = idx.to_series().groupby([idx.year, idx.month]).first().values

        for i, date in enumerate(rebal_dates):
            pos = self.price.index.get_loc(date)
            start = max(0, pos - self.lookback)
            window = self.returns.iloc[start:pos][assets]

            # 計算平均報酬
            mean_ret = window.mean()

            # 選出 top_n
            top_assets = mean_ret.sort_values(ascending=False).iloc[:self.top_n].index

            # 權重 = 平均報酬正值比例
            weights = mean_ret[top_assets].clip(lower=0)
            if weights.sum() > 0:
                w = weights / weights.sum()
            else:
                w = pd.Series(1/self.top_n, index=top_assets)

            # full 權重
            full = pd.Series(0.0, index=self.price.columns)
            full.loc[top_assets] = w
            full[self.exclude] = 0.0

            # 填入當月
            if i + 1 < len(rebal_dates):
                next_date = rebal_dates[i+1]
            else:
                next_date = self.price.index[-1] + pd.Timedelta(days=1)
            mask = (self.price.index >= date) & (self.price.index < next_date)
            for col in self.price.columns:
                self.portfolio_weights.loc[mask, col] = full[col]

        self.portfolio_weights.ffill(inplace=True)
        self.portfolio_weights.fillna(0, inplace=True)


    def calculate_portfolio_returns(self):
        # Ensure weights are calculated
        if not hasattr(self, "portfolio_weights"):
            self.calculate_weights()

        # Calculate the portfolio returns
        self.portfolio_returns = self.returns.copy()
        assets = self.price.columns[self.price.columns != self.exclude]
        self.portfolio_returns["Portfolio"] = (
            self.portfolio_returns[assets]
            .mul(self.portfolio_weights[assets])
            .sum(axis=1)
        )

    def get_results(self):
        # Ensure portfolio returns are calculated
        if not hasattr(self, "portfolio_returns"):
            self.calculate_portfolio_returns()

        return self.portfolio_weights, self.portfolio_returns


if __name__ == "__main__":
    # Import grading system (protected file in GitHub Classroom)
    from grader_2 import AssignmentJudge
    
    parser = argparse.ArgumentParser(
        description="Introduction to Fintech Assignment 3 Part 12"
    )

    parser.add_argument(
        "--score",
        action="append",
        help="Score for assignment",
    )

    parser.add_argument(
        "--allocation",
        action="append",
        help="Allocation for asset",
    )

    parser.add_argument(
        "--performance",
        action="append",
        help="Performance for portfolio",
    )

    parser.add_argument(
        "--report", action="append", help="Report for evaluation metric"
    )

    parser.add_argument(
        "--cumulative", action="append", help="Cumulative product result"
    )

    args = parser.parse_args()

    judge = AssignmentJudge()
    
    # All grading logic is protected in grader_2.py
    judge.run_grading(args)
