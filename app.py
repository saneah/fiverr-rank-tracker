import streamlit as st
import pdfplumber
import re
import pandas as pd

# Function to clean extracted numbers
def clean_number(value):
    if value == "N/A" or value is None:
        return None
    return float(value.replace(",", "").strip())

# Function to extract financial metrics from PDF
def extract_financials(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    # 🔹 Print extracted text for debugging
    st.text("🔍 Extracted Text from PDF:")
    st.text(text[:1000])  # Print first 1000 characters to check formatting

    # 🔹 Improved regex patterns (handling variations in text format)
    profit = re.findall(r"Profit after tax\s*[:\s]+([\d,]+)", text, re.IGNORECASE)
    eps = re.findall(r"Earnings per share\s*\(Rs\.\)\s*[:\s]*([\d.]+)", text, re.IGNORECASE)
    cash = re.findall(r"Bank balances\s*[:\s]+([\d,]+)", text, re.IGNORECASE)

    return {
        "Profit After Tax": clean_number(profit[0]) if profit else None,
        "Earnings Per Share (EPS)": clean_number(eps[0]) if eps else None,
        "Cash & Bank Balances": clean_number(cash[0]) if cash else None
    }

# Function to calculate growth/decline
def calculate_growth(current, previous):
    if current is None or previous is None:
        return "Data Missing"
    growth = ((current - previous) / previous) * 100
    return f"{growth:.2f}% {'Growth' if growth > 0 else 'Decline'}"

# Function to estimate stock price using P/E ratio
def estimate_stock_price(eps, industry_pe):
    if eps is None:
        return "EPS Data Missing"
    return round(eps * industry_pe, 2)

# Streamlit UI
st.title("📊 Stock Financial Report Analyzer")
st.write("Upload a financial report, and we'll extract key financial metrics!")

# File uploader
pdf_file = st.file_uploader("Upload a Financial Report (PDF)", type=["pdf"])

# User input for industry P/E ratio
industry_pe = st.number_input("Enter Industry P/E Ratio:", min_value=1.0, max_value=50.0, value=10.0)

# **Previous Year Data** (From Financial Report)
previous_data = {
    "Profit After Tax": clean_number("1,602,379"),
    "Earnings Per Share (EPS)": clean_number("12.91"),
    "Cash & Bank Balances": clean_number("22,215,531")
}

if pdf_file:
    # Extract financial data from PDF
    financial_data = extract_financials(pdf_file)

    # Calculate growth
    growth_results = {key: calculate_growth(financial_data[key], previous_data[key]) for key in financial_data}

    # Estimate stock price
    expected_price = estimate_stock_price(financial_data["Earnings Per Share (EPS)"], industry_pe)

    # Display Results
    st.subheader("📈 Extracted Financial Data")
    st.write(pd.DataFrame(financial_data.items(), columns=["Metric", "Value"]))

    st.subheader("📊 Growth/Decline Analysis")
    st.write(pd.DataFrame(growth_results.items(), columns=["Metric", "Growth"]))

    st.subheader("💰 Expected Stock Price")
    st.write(f"Estimated Fair Value of Stock: **Rs. {expected_price}**")
