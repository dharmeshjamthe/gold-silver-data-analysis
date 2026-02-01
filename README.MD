# 📊 Gold & Silver Market Data Analytics Dashboard

An end-to-end data analytics project that automates the collection, processing, analysis, and visualization of gold and silver market prices using Python, SQL Server, and Power BI.

---

## 🚀 Project Overview

This project fetches daily gold and silver price data from financial markets, stores it in a SQL Server database, performs analytical computations such as returns, volatility, and correlation, and visualizes insights through an interactive Power BI dashboard.

It simulates a real-world financial data pipeline used in investment analytics and business intelligence systems.

---

## 🛠️ Tools & Technologies

- Python (yfinance, pandas, pyodbc)
- SQL Server
- Power BI
- Git & GitHub

---

## 🔄 Data Pipeline Flow

Market Data → Python Processing → SQL Server Storage → SQL Analytics → Power BI Dashboard

---

## 📈 Key Features

✔ Automated daily price ingestion  
✔ Currency & unit conversion (USD to INR, gold in 10g, silver in 1kg)  
✔ Trend analysis & moving averages  
✔ Volatility & risk-return metrics  
✔ Correlation analysis  
✔ Interactive Power BI dashboards  
✔ Live data refresh capability  

---

## 📊 Dashboard Highlights

- Latest price KPI cards  
- Daily price change indicators  
- Trend charts with moving averages  
- Risk vs return scatter plot  
- Performance comparison visuals  
- Date-based slicers for dynamic analysis  

---

## 📁 Project Structure

gold-silver-data-analysis/
│
├── python/
│ ├── daily_update.py
│ └── full_history_load.py
│
├── sql/
│ └── analysis_queries.sql
│
├── powerbi/
│ └── dashboard.pbix
│
└── README.md