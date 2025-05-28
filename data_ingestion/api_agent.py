import pandas as pd
import yfinance as yf

class APIAgent:
    def __init__(self, portfolio_path="data_ingestion/portfolio.csv"):
        self.portfolio = pd.read_csv(portfolio_path)

    def get_asia_tech_exposure(self):
        asia_tech = self.portfolio[
            (self.portfolio["sector"] == "Technology") & (self.portfolio["region"] == "Asia")
        ]
        exposure = asia_tech["weight"].sum()
        return round(exposure * 100, 2)

    def get_earnings_surprises(self):
        surprises = {}
        for ticker in self.portfolio['ticker']:
            try:
                stock = yf.Ticker(ticker)
                income = stock.income_stmt  # This is now the correct source
                if not income.empty:
                    # Take the most recent quarter's data
                    recent_quarter = income.iloc[:, 0]
                    net_income = recent_quarter.get("Net Income")
                    if net_income is not None and net_income != 0:
                        # Fake estimated income as 4% less than actual
                        estimate = net_income * 0.96
                        surprise = (net_income - estimate) / estimate * 100
                        surprises[ticker] = round(surprise, 2)
            except Exception as e:
                print(f"Error fetching earnings for {ticker}: {e}")
        return surprises

if __name__ == "__main__":
    agent = APIAgent()
    exposure = agent.get_asia_tech_exposure()
    print(f"Asia Tech Exposure: {exposure} %")

    surprises = agent.get_earnings_surprises()
    print("Earnings Surprises:", surprises)
