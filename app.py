import streamlit as st
import pdfplumber
import re
import pandas as pd

# Function to extract financial metrics from the PDF
def extract_financials(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # Use regex to extract key financial data
    revenue = re.findall(r"Revenue\s+([\d,]+)", text)
    gross_profit = re.findall(r"Gross Profit\s+([\d,]+)", text)
    operating_profit = re.findall(r"Operating Profit\s+([\d,]+)", text)
    net_profit = re.findall(r"Profit for the year\s+([\d,]+)", text)
    eps = re.findall(r"Earnings per share\s*\(Rs.\)\s*([\d.]+)", text)

    return {
        "Revenue": revenue[0] if revenue else "N/A",
        "Gross Profit": gross_profit[0] if gross_profit else "N/A",
        "Operating Profit": operating_profit[0] if operating_profit else "N/A",
        "Net Profit": net_profit[0] if net_profit else "N/A",
        "EPS": eps[0] if eps else "N/A"
    }

# Function to calculate growth/decline
def calculate_growth(current, previous):
    if current == "N/A" or previous == "N/A":
        return "Data Missing"
    current, previous = float(current.replace(",", "")), float(previous.replace(",", ""))
    growth = ((current - previous) / previous) * 100
    return f"{growth:.2f}% {'Growth' if growth > 0 else 'Decline'}"

# Function to estimate stock price using P/E ratio
def estimate_stock_price(eps, industry_pe):
    if eps == "N/A":
        return "EPS Data Missing"
    eps = float(eps)
    return round(eps * industry_pe, 2)

# Streamlit UI
st.title("📊 Stock Financial Report Analyzer")
st.write("Upload a financial report, and we'll extract key financial metrics!")

# File uploader
pdf_file = st.file_uploader("Upload a Financial Report (PDF)", type=["pdf"])

# User input for industry P/E ratio
industry_pe = st.number_input("Enter Industry P/E Ratio:", min_value=1.0, max_value=50.0, value=10.0)

# **Previous Year Data** (Manually entered for now, but can be automated later)
previous_data = {
    "Revenue": "9,413,149",
    "Gross Profit": "1,133,637",
    "Operating Profit": "888,836",
    "Net Profit": "365,035",
    "EPS": "6.40"
}

if pdf_file:
    # Extract financial data from PDF
    financial_data = extract_financials(pdf_file)

    # Calculate growth
    growth_results = {key: calculate_growth(financial_data[key], previous_data[key]) for key in financial_data}

    # Estimate stock price
    expected_price = estimate_stock_price(financial_data["EPS"], industry_pe)

    # Display Results
    st.subheader("📈 Extracted Financial Data")
    st.write(pd.DataFrame(financial_data.items(), columns=["Metric", "Value"]))

    st.subheader("📊 Growth/Decline Analysis")
    st.write(pd.DataFrame(growth_results.items(), columns=["Metric", "Growth"]))

    st.subheader("💰 Expected Stock Price")
    st.write(f"Estimated Fair Value of Stock: **Rs. {expected_price}**")
