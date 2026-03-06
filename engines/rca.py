import pandas as pd
import numpy as np
from typing import Dict, Any

import os
# Load the real dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/Target_Foods_Sales_2024_2025.csv')

def format_currency(val):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:.0f}"

def calculate_pvm_drivers(df_current, df_prev, dimension):
    """
    Calculates Price and Volume variance drivers across a given dimension (e.g., 'Brand', 'Channel').
    """
    # Aggregate by dimension
    curr_agg = df_current.groupby(dimension).agg(
        Revenue=('Net_Revenue', 'sum'),
        Volume=('Volume', 'sum')
    ).reset_index()
    
    prev_agg = df_prev.groupby(dimension).agg(
        Revenue=('Net_Revenue', 'sum'),
        Volume=('Volume', 'sum')
    ).reset_index()
    
    # Calculate implied gross prices
    curr_agg['Price'] = curr_agg['Revenue'] / curr_agg['Volume'].replace(0, np.nan)
    prev_agg['Price'] = prev_agg['Revenue'] / prev_agg['Volume'].replace(0, np.nan)
    
    # Merge
    merged = pd.merge(curr_agg, prev_agg, on=dimension, suffixes=('_curr', '_prev'), how='outer').fillna(0)
    
    # Mathematical PVM Formulas
    # Price Variance = (Current Price - Prev Price) * Current Volume
    merged['Price_Variance'] = (merged['Price_curr'] - merged['Price_prev']) * merged['Volume_curr']
    
    # Volume Variance = (Current Volume - Prev Volume) * Prev Price
    merged['Volume_Variance'] = (merged['Volume_curr'] - merged['Volume_prev']) * merged['Price_prev']
    
    drivers = []
    
    # Get top 2 price drivers
    price_impacts = merged.sort_values(by='Price_Variance', key=abs, ascending=False).head(2)
    for _, row in price_impacts.iterrows():
        if row['Price_Variance'] != 0:
            drivers.append({
                "metric": str(row[dimension]),
                "value": f"Price change: {format_currency(row['Price_curr'] - row['Price_prev'])}/unit",
                "variance": f"{'+' if row['Price_Variance'] > 0 else ''}{format_currency(row['Price_Variance'])}",
                "sentiment": "positive" if row['Price_Variance'] > 0 else "negative"
            })
            
    # Get top 2 volume drivers
    vol_impacts = merged.sort_values(by='Volume_Variance', key=abs, ascending=False).head(2)
    for _, row in vol_impacts.iterrows():
        if row['Volume_Variance'] != 0:
            drivers.append({
                "metric": str(row[dimension]),
                "value": f"Volume shift: {int(row['Volume_curr'] - row['Volume_prev']):,} units",
                "variance": f"{'+' if row['Volume_Variance'] > 0 else ''}{format_currency(row['Volume_Variance'])}",
                "sentiment": "positive" if row['Volume_Variance'] > 0 else "negative"
            })
            
    return drivers

def run_pvm_analysis() -> Dict[str, Any]:
    """
    Real Price-Volume-Mix (PVM) Variance Analysis Engine.
    Powered by actual Pandas calculations on generic FMCG data.
    """
    print("Loading data for RCA...")
    try:
        # Load the mock FMCG data generated
        df = pd.read_csv(DATA_PATH)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Split into current and previous period (e.g. Q4 vs Q3 for demonstration)
        df_prev = df[(df['Date'] >= '2023-01-01') & (df['Date'] < '2023-07-01')]
        df_curr = df[(df['Date'] >= '2023-07-01') & (df['Date'] <= '2023-12-31')]
        
        current_rev = df_curr['Net_Revenue'].sum()
        prev_rev = df_prev['Net_Revenue'].sum()
        current_vol = df_curr['Volume'].sum()
        prev_vol = df_prev['Volume'].sum()
        
    except Exception as e:
        print(f"Error loading RCA data: {e}")
        current_rev, prev_rev, current_vol, prev_vol = 0, 0, 0, 0
        df_curr, df_prev = pd.DataFrame(), pd.DataFrame()

    total_variance = current_rev - prev_rev
    pct_variance = (total_variance / prev_rev * 100) if prev_rev else 0
    
    # Calculate macro Price and Volume variance
    avg_price_curr = current_rev / current_vol if current_vol else 0
    avg_price_prev = prev_rev / prev_vol if prev_vol else 0
    
    macro_price_variance = (avg_price_curr - avg_price_prev) * current_vol
    macro_volume_variance = (current_vol - prev_vol) * avg_price_prev
    macro_mix_variance = total_variance - macro_price_variance - macro_volume_variance

    if not df_curr.empty and not df_prev.empty:
        brand_drivers = calculate_pvm_drivers(df_curr, df_prev, 'Brand')
        channel_drivers = calculate_pvm_drivers(df_curr, df_prev, 'Channel')
    else:
        brand_drivers, channel_drivers = [], []

    return {
        "metric": "Net Revenue",
        "value": format_currency(current_rev),
        "variance": f"{'+' if total_variance > 0 else ''}{format_currency(total_variance)} ({pct_variance:+.1f}%)",
        "sentiment": "positive" if total_variance > 0 else "negative",
        "impactPct": 100.0,
        "impactAbs": total_variance,
        "drivers": [
            {
                "metric": "Price Impact",
                "value": f"Avg {format_currency(avg_price_curr)}/unit",
                "variance": f"{'+' if macro_price_variance > 0 else ''}{format_currency(macro_price_variance)}",
                "sentiment": "positive" if macro_price_variance > 0 else "negative",
                "impactPct": round((macro_price_variance / total_variance * 100), 1) if total_variance else 0,
                "impactAbs": macro_price_variance,
                "description": f"Avg price: {format_currency(avg_price_prev)} \u2192 {format_currency(avg_price_curr)}/unit",
                "drivers": channel_drivers
            },
            {
                "metric": "Volume Impact",
                "value": f"{int(current_vol):,} units",
                "variance": f"{'+' if macro_volume_variance > 0 else ''}{format_currency(macro_volume_variance)}",
                "sentiment": "positive" if macro_volume_variance > 0 else "negative",
                "impactPct": round((macro_volume_variance / total_variance * 100), 1) if total_variance else 0,
                "impactAbs": macro_volume_variance,
                "description": f"Volume shifted {int(current_vol - prev_vol):+,} units vs prior period",
                "drivers": brand_drivers
            },
            {
                "metric": "Mix Impact",
                "value": "Portfolio Shift",
                "variance": f"{'+' if macro_mix_variance > 0 else ''}{format_currency(macro_mix_variance)}",
                "sentiment": "positive" if macro_mix_variance > 0 else "negative",
                "impactPct": round((macro_mix_variance / total_variance * 100), 1) if total_variance else 0,
                "impactAbs": macro_mix_variance,
                "description": "Residual after price/volume — reflects product & channel portfolio shift"
            }
        ]
    }
