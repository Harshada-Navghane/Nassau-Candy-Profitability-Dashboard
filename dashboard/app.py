#adding KPI Cards

import streamlit as st
import pandas as pd
import plotly.express as px

## Page Title
st.title("Nassau Candy Profitability Dashboard")

#Loading the data from the CSV file 
@st.cache_data
def load_data():
    df = pd.read_csv(
        r"C:\Users\harsh\OneDrive\Nassau_Project\data\Cleaned_Nassau_Candy_Distributor.csv"
    )
    df["Order Date"] = pd.to_datetime(df["Order Date"])     # Converting the "Order Date" text column to datetime format
    return df

df = load_data()


min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

#creating a sidebar for filters

st.sidebar.title("Filters")

selected_division = st.sidebar.selectbox(
    "Select Division",
    df["Division"].unique()
)

#creating a date range filter in the sidebar
selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
 
 #Convert selected dates
start_date = pd.to_datetime(selected_dates[0])
end_date = pd.to_datetime(selected_dates[1])

#creating a text input for product search in the sidebar
product_search = st.sidebar.text_input(
    "Search Product"
)

# Filter the dataframe based on selected division and date range
filtered_df = df[
    (df["Division"] == selected_division) &
    (df["Order Date"] >= start_date) &
    (df["Order Date"] <= end_date)
]
#product search filter
if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].str.contains(
            product_search,
            case=False
        )
    ]

#Margin Threshold Slider
margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin (%)",
    min_value=0,
    max_value=100,
    value=0
)


#create one master dataframe to store all the metrics and KPIs for the selected division

product_summary = (
    filtered_df.groupby("Product Name")
    .agg({
        "Sales": "sum",
        "Cost": "sum",
        "Gross Profit": "sum",
        "Units": "sum"
    })
    .reset_index()
)

product_summary["Gross Margin %"] = (
    product_summary["Gross Profit"] /
    product_summary["Sales"]
) * 100

product_summary["Profit per Unit"] = (
    product_summary["Gross Profit"] /
    product_summary["Units"]
)

# Filter the product summary based on the margin threshold
filtered_product_summary = product_summary[
    product_summary["Gross Margin %"] >= margin_threshold
]

#KPI
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
avg_margin = filtered_df["Gross Margin %"].mean()
total_units = filtered_df["Units"].sum()

#KPI Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue",f"{total_sales:,.0f}")
col2.metric("Total Profit",f"{total_profit:,.0f}")
col3.metric("Avg Margin %",f"{avg_margin:,.2f}%")
col4.metric("Units Sold",f"{total_units:,.0f}")

st.divider()

st.header("📊 Dashboard Analysis")

with st.expander("Dataset Preview"):
    st.write("Filtered Dataset Preview")
    st.dataframe(filtered_df.head())

#Division Performance Chart
#Comparison of all divisions → using df instead of filtered_df to show all divisions in the chart

st.divider()
st.header("🏢 Division Analysis")

st.subheader("Division Performance")

division_summary =(
df.groupby("Division")
.agg({
    "Sales" : "sum",
    "Gross Profit" : "sum",
}).reset_index()
)

#st.write(division_summary)

fig =px.bar(
    division_summary,
    x = "Division",
    y = ["Sales", "Gross Profit"],
    barmode = "group",
    title = "Revenue vs Profit by Division"
)
st.plotly_chart(fig, use_container_width=True)

# Margin Distribution by Division

st.subheader("Margin Distribution by Division")
division_margin = (
    df.groupby("Division")
    .agg({
        "Gross Margin %": "mean"
    })
    .reset_index()
)
st.write(division_margin)

#Creating a bar chart for Margin Distribution by Division

st.subheader("Average Gross Margin by Division")

fig7 = px.bar(
    division_margin,
    x="Division",
    y="Gross Margin %",
    title="Average Gross Margin by Division",
    text_auto=".2f"
)

st.plotly_chart(fig7, use_container_width=True)

#Top Products by Profit

st.divider()
st.header("📦 Product Profitability Analysis")

st.subheader("Top Products By Profit")
top_products = (
    filtered_product_summary
    .sort_values(by="Gross Profit", ascending=False)
    .head(10)
)
#st.write(top_products)

st.bar_chart(
    top_products.set_index("Product Name")
)

fig2 = px.bar(
    top_products,
    x="Gross Profit",
    y="Product Name",
    orientation = "h",  
    title = "Top Produts by Gross Profit"
)

fig2.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig2, use_container_width=True)

#Top Products by Gross Margin %

top_margin_products = (
    filtered_product_summary
    .sort_values(by="Gross Margin %", ascending=False)
    .head(10)
)
#st.write(top_margin_products.head(10))

#Creating the Gross Margin Chart

st.subheader("Top 10 Products by Gross Margin %")

fig3 = px.bar(
    top_margin_products,
    x = "Gross Margin %",
    y = "Product Name",
    orientation = "h",
    title = "Top 10 Products by Gross Margin(%)"
)
fig3.update_layout(
    yaxis=dict(categoryorder="total ascending")
)
st.plotly_chart(fig3, use_container_width=True)

#calculating High-sales / low-margin products

avg_sales = filtered_product_summary["Sales"].mean()
avg_margin = filtered_product_summary["Gross Margin %"].mean()

high_sales_low_margin = filtered_product_summary[
    (filtered_product_summary["Sales"] > avg_sales) &
    (filtered_product_summary["Gross Margin %"] < avg_margin)
]

st.subheader("High Sales, Low Margin Products")

st.dataframe(high_sales_low_margin)


#visualizing some of the high-sales low-margin products using a bar chart

fig4 = px.bar(
    high_sales_low_margin,
    x = "Sales",
    y = "Product Name",
    color = "Gross Margin %",
    orientation  = "h",
    title = "High Sales, Low Margin Products"
    )
fig4.update_layout(
    yaxis=dict(categoryorder="total ascending")
)
st.plotly_chart(fig4,use_container_width=True)

st.info(
    "💡 Business Insight: These products generate above-average sales but below-average margins. "
    "Review pricing strategies, supplier costs, or discounts to improve profitability."
)

#Calculating Low-sales / low-profit products


avg_profit = filtered_product_summary["Gross Profit"].mean()

low_sales_low_profit = filtered_product_summary[
    (filtered_product_summary["Sales"] < avg_sales) &
    (filtered_product_summary["Gross Profit"] < avg_profit)
]


st.subheader("Low Sales, Low Profit Products")
st.dataframe(low_sales_low_profit)


fig5 = px.bar(
    low_sales_low_profit,
    x="Sales",
    y="Product Name",
    color="Gross Profit",
    orientation="h",
    title="Low Sales, Low Profit Products"
)
fig5.update_layout(
    yaxis=dict(categoryorder="total ascending")
)
st.plotly_chart(fig5, use_container_width=True)

st.info(
    "💡 Business Insight: These products contribute little to both revenue and profit. "
    "Consider discontinuing them, bundling them with popular products, or running targeted promotions."
)
st.divider()
#Calculating Profit Contribution % for each product

filtered_product_summary["Profit Contribution %"] = (
    filtered_product_summary["Gross Profit"] /
    filtered_product_summary["Gross Profit"].sum()
) * 100

#Calculating Top 10 Profit Contributors
top_profit_contributors = (
    filtered_product_summary
    .sort_values(by="Profit Contribution %", ascending=False)
    .head()
)

st.subheader("Top Profit Contributors")

st.dataframe(top_profit_contributors)

#Creating a bar Chart for Top Profit Contributors

fig6 = px.bar(
    top_profit_contributors,
    x="Profit Contribution %",
    y="Product Name",
    orientation="h",
    title="Top Products by Profit Contribution (%)"
)
fig6.update_layout(
    yaxis=dict(categoryorder="total ascending")
)
st.plotly_chart(fig6, use_container_width=True)

#the Scatter Plot for Cost vs Sales Diagnostics

st.divider()
st.header("💰 Cost vs Margin Diagnostics")

st.subheader("Cost vs Sales Diagnostics")

fig8 = px.scatter(
    filtered_product_summary,
    x="Cost",
    y="Sales",
    color="Gross Margin %",
    hover_name="Product Name",
    title="Cost vs Sales by Product"
)

st.plotly_chart(fig8, use_container_width=True)

avg_cost = product_summary["Cost"].mean()

margin_risk = product_summary[
    (product_summary["Cost"] > avg_cost) &
    (product_summary["Gross Margin %"] < avg_margin)
]

st.subheader("Margin Risk Products")

st.dataframe(margin_risk)

#Creating a bar chart for Margin Risk Products
#This visualization identifies products that incur above-average production costs 
# while generating below-average gross margins. These products may require 
# pricing adjustments, supplier negotiations, or cost optimization to improve profitability.

fig9 = px.bar(
    margin_risk,
    x="Cost",
    y="Product Name",
    color="Gross Margin %",
    orientation="h",
    title="High Cost, Low Margin Products"
)
fig9.update_layout(
    yaxis=dict(categoryorder="total ascending")
)

st.plotly_chart(fig9, use_container_width=True)

st.info(
    "💡 Business Insight: These products have above-average costs but below-average margins. "
    "They should be prioritized for cost reduction or pricing optimization."
)

#pareto analysis, sorting the products by profit.

pareto_df = (
    filtered_product_summary
    .sort_values(by="Gross Profit", ascending=False)
    .reset_index(drop=True)
)
st.divider()
st.header("📈 Profit Concentration Analysis")

st.subheader("Pareto Analysis")

#st.dataframe(pareto_df)

pareto_df["Cumulative Profit"] = (
    pareto_df["Gross Profit"].cumsum()
)
#st.write(pareto_df)

#Calculate Cumulative Profit %

pareto_df["Cumulative Profit %"] = (
    pareto_df["Cumulative Profit"] /
    pareto_df["Gross Profit"].sum()
) * 100

#st.write(pareto_df)

#creating pareto chart

import plotly.graph_objects as go

fig10 = go.Figure()

#Bar chart (Gross Profit)

fig10.add_bar (
    x=pareto_df["Product Name"],    
    y=pareto_df["Gross Profit"],
    name="Gross Profit"
)

# Line Chart (Cumulative Profit %)
fig10.add_scatter(
    x=pareto_df["Product Name"],
    y=pareto_df["Cumulative Profit %"],
    mode="lines+markers",
    name="Cumulative Profit %",
    yaxis="y2"
)

fig10.update_layout(
    title="Pareto Analysis of Product Profitability",
    xaxis_title="Product Name",
    yaxis_title="Gross Profit",
    yaxis2=dict(
        title="Cumulative Profit %",
        overlaying="y",
        side="right",
        range=[0, 100]
    )
)

st.plotly_chart(fig10, use_container_width=True)

st.info(
    "💡 Business Insight: A small number of products contribute to the majority of total profit. "
    "Protecting and growing these high-performing products can have the greatest business impact."
)
