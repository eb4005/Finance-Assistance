from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import os

app = FastAPI()

class EarningsAnalyzer:
    def __init__(self):
        self.portfolio = self.load_portfolio()
        
    def load_portfolio(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        
        portfolio_path = os.path.join(
            project_root,
            "data_ingestion",
            "portfolio.csv"
        )
        

        if not os.path.exists(portfolio_path):
            raise FileNotFoundError(f"Portfolio file missing at: {portfolio_path}")
            
        df = pd.read_csv(portfolio_path)
        return df[['ticker', 'sector', 'region', 'weight']].dropna()

    def get_asia_tech_exposure(self):
        filtered = self.portfolio[
            (self.portfolio['sector'].str.contains('Tech', case=False)) &
            (self.portfolio['region'].str.contains('Asia', case=False))
        ]
        return round(filtered['weight'].sum() * 100, 2)

    def get_earnings_surprises(self):
        surprises = {}
        
        for ticker in self.portfolio['ticker'].unique():
            try:
                stock = yf.Ticker(ticker)
                earnings = stock.quarterly_earnings
                if earnings.empty:
                    continue
                    
                latest = earnings.iloc[0]
                actual = latest['Actual']
                estimate = latest['Estimate']
                
                if pd.notna(actual) and pd.notna(estimate) and estimate != 0:
                    surprise = ((actual - estimate) / abs(estimate)) * 100
                    surprises[ticker] = round(surprise, 2)
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
        return surprises

analyzer = EarningsAnalyzer()

@app.get("/exposure")
def get_exposure():
    return {"exposure": analyzer.get_asia_tech_exposure()}

@app.get("/earnings_surprises")
def get_earnings():
    return analyzer.get_earnings_surprises()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

