# from os import write
#
# import streamlit as st
# from PIL.ImageOps import expand
# from streamlit import markdown
# from  streamlit_option_menu import option_menu
# import  pandas as pd
#
# st.set_page_config("Uber Analytics",layout="wide")
# df=pd.read_csv("Uber data set ncr.xlsx - ncr_ride_bookings.csv")
#
# # sidebar menu
# with st.sidebar:
#     seleted=option_menu("Main Menu",["Dataset","Overview","Ride Analysis "],
#                         icons=["table","bar-chart","graph-up"],menu_icon="car-front",default_index=0)
#
# if seleted=="Dataset":
#     st.title("Data Explorer")
#     st.divider()
#
# # dataset overview
#     col1,col2,col3 = st.columns(3)
#     col1.metric("Total Rows",df.shape[0])
#     col2.metric("Total Columns",df.shape[1])
#     col3.metric("Missing value",df.isna().sum().sum())
#
#     st.divider()
#
#     # column selection
#     st.subheader("Select columns")
#     selected_column=st.multiselect("Select columns to display",df.columns,default=df.columns)
#     filtered_df=df[selected_column]
#
#     # search
#     st.subheader("Search in Dataset")
#     search_value=st.text_input("Enter Value to Search",icon=":material/search:")
#     if search_value:
#         filtered_df=filtered_df[filtered_df.astype(str).apply(
#             lambda row:row.str.contains(search_value,case=False).any(),axis=1
#             )]
#     expand=st.expander("Expand Data")
#     expand.write(filtered_df)
#
#     markdown("---------------------------------------")
#
#     select_col=st.selectbox("Select columns",df.columns)
#
#     if select_col in df.columns:
#         filtered_df=df[select_col]
#         expand=st.expander("Expand Data")
#         expand.write(filtered_df)
#
#     select_row=st.slider("Select Row",0,len(df),0)
#     filtered_df = df.iloc[:select_row]
#     expand = st.expander("Expand Data")
#     expand.write(filtered_df)

# --------------------------------------------------work----------------------------------------------

import streamlit as st
from PIL.ImageOps import expand
from click import style
from plotly.express import histogram
from streamlit import expander, success
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Uber Analytics Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("Uber data set ncr.xlsx - ncr_ride_bookings.csv")

# Sidebar
with st.sidebar:
    selected = option_menu(
        "Uber Analytics",
        ["DataSet", "Overview", "Ride Analytics","Data Assistant"],
        icons=["table", "bar-chart", "graph-up","person"],
        menu_icon="car-front",
        default_index=0
    )

# ===================== DATASET PAGE =====================
if selected == "DataSet":
    st.title("Data Explorer")
    st.divider()

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isna().sum().sum())

    # Column Selection
    st.subheader("Select Columns")
    selected_col = st.multiselect("Select Columns", df.columns, default=df.columns)
    filtered_df = df[selected_col]
    st.divider()

    # -------- Column Search --------
    st.subheader("Search in One Column")
    search_col = st.selectbox("Select Column to Search", filtered_df.columns)
    # Show only selected column values
    column_values = filtered_df[search_col].dropna().unique()
    search_val_col = st.selectbox("Select Value", column_values)
    if search_val_col:
        filtered_df = filtered_df[
            filtered_df[search_col].astype(str).str.contains(str(search_val_col), case=False, na=False)
        ]

    # -------- Lambda Search (Full Row) --------
    st.subheader("Search Entire Row ")
    search_val = st.text_input("Enter value to search in entire row")

    if search_val:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda row: row.str.contains(search_val, case=False,na=False).any(),
                axis=1
            )
        ]
    expand = st.expander("Data")
    data_get=pd.DataFrame(filtered_df)
    expand.write(data_get)
    col4.metric("Filtered Rows", filtered_df.shape[0])



    # Row Limit
    row_limit = st.slider("Rows to Display", 10, 500, 50)

    # Show Table
    st.subheader("Dataset Table")
    if filtered_df.empty:
        st.warning("No data found")
    else:
        st.dataframe(filtered_df.head(row_limit), use_container_width=True)

    # Download
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Filtered Data", csv, "Filtered_Data.csv", "text/csv")

# OVERVIEW
if selected == "Overview":
    st.header("Ride Overview")

    col1,col2 = st.columns(2)
    col1.metric("Ride Overview", len(df))
    col2.metric("Revenue" ,df["Booking Value"].sum())
    total_revenue = df["Booking Value"].sum()

    st.divider()

    #business unit performance
    st.header("Business Unit Performance Metrix")
    bu_matrix = df.groupby("Vehicle Type").agg(
        Total_Booking = ("Booking ID","count"),
        Revenue_Generated = ("Booking Value","count"),
        Avg_Distance = ("Ride Distance", "mean"),
        Avg_Rating = ("Driver Ratings", "mean")
    )
    bu_matrix["Revenue Share%"] = (bu_matrix["Revenue_Generated"]/total_revenue*100
                                    if (total_revenue)>0 else 0)
    st.dataframe(bu_matrix.style.format({
        "Revenue_Generated":"${:,.2f}",
        "Avg_Distance":"{:,.2f}km",
        "Avg_Rating":"{:,.1f}",
        "Revenue Share%":"{:,.1f}%"
    }).background_gradient(subset=["Revenue_Generated"],cmap="RdYlGn"))

    # OPERATION EFFICIENCY
    col_eff, col_can = st.columns (2)
    with col_eff:
        st.header("Operational Efficiency")
        eff_df = df.groupby("Vehicle Type")[["Avg VTAT","Avg CTAT"]].mean()
        st.write("Average Turn Around Time {%in Minutes%}")
        st.dataframe(eff_df.style.highlight_max(axis=0, color="#2bfb6b").highlight_min(axis=0,color="#fb352b"),
                    use_container_width=True)
    total_rides = len(df)
    with col_can:
        st.subheader("Cancellation Audit")
        status_count = df["Booking Status"].value_counts().to_frame (name="Count")
        status_count["Share %"]= (status_count["Count"]/total_rides*100)
        st.dataframe(status_count, use_container_width=True)
    st.divider()

    completed_rides=df.groupby("Payment Method")["Booking ID"].count()
    st.dataframe(completed_rides)

    # FINANCIAL ANALYSIS
    st.header("Financial Deep Dive")
    pay_col,reason_col = st.columns([4,6])
    with pay_col:
        st.markdown("**Payment Method Distribution")
        pay_summary = (completed_rides/completed_rides.sum())*100
        st.dataframe(pay_summary.to_frame().style.highlight_max(axis=0, color="#1a7a7d").highlight_min(axis=0,color="#5fa5f5"),)

    # with reason_col:

    #Data Quality
    with st.expander("Data Quality & Audit logs"):
        audit1,audit2 = st.columns(2)
        audit1.write(f"**Duplicate Records:{df.duplicated().sum()}")
        audit2.write(f"Missing Value:{df["Booking Status"].isna().sum()}")
        st.info("Missing Booking Value are Expected for cancellation and no driver acceptance")
        st.success("Executive Overview are generated from operational Dataset")

        st.title("Uber Operation")
        st.markdown("---")

#         Strategic kpi layer
        completed_rides=df[df["Booking Status"]=="Completed"]
        total_revenue=completed_rides["Booking Value"].sum()
        avg_distance=completed_rides["Ride Distance"].mean()
        success_rate=(len(completed_rides)/total_rides*100 if total_rides>0 else 0)
        avg_rating= completed_rides["Customer Rating"].dropna().mean()

        kpi1,kpi2,kpi3,kpi4 = st.columns(4)
        kpi1.metric(f"Gross Total Revenue",f"{total_revenue:,.0f}",
                   "target: %1.2M")
        kpi2.metric("Average Distance",f"{avg_distance:,.1f}")
        kpi3.metric("Fullfillment Rate",f"{success_rate:,.2f}",
                        "-2.4% v/s Last Month","red")
        kpi4.metric("Avg Customer Rating",f"{avg_rating:,.1f}")

    checkbox=st.checkbox("Data set")
    if checkbox:
        st.write(df)
        st.markdown("---")
        option = st.selectbox("Dataset of column value", ["Int", "Float"])
        if option == "int":
            int_data = df.select_dtypes(int)
            st.write(int_data)
        elif option == "Float":
            int_data = df.select_dtypes(float)
            st.write(int_data)

if selected == "Ride Analytics":
    st.title("Advance Ride Intellugence Dashboard")

    completed=df[df["Booking Status"]=="Completed"]
#     sunburst chart
    st.subheader("Revenue Hierarchy")
    fig1 = px.sunburst(completed,path=["Vehicle Type","Payment Method"],
                      values="Booking Value",
                      color="Booking Value",
                      color_continuous_scale="Turbo")
    fig1.update_layout(height=500)
    st.plotly_chart(fig1)

#     treemap
    st.subheader("Revenue Distribution")
    fig2 = px.treemap(completed,path=["Vehicle Type","Payment Method"],
                      values="Booking Value",
                      color="Booking Value",
                      color_continuous_scale="Blues")
    fig2.update_layout(margin=dict(l=0, r=0, b=0, t=20),height=420)
    st.plotly_chart(fig2)

    st.subheader("Customer Rating Spread")
    fig3=px.box(completed,x="Vehicle Type",y="Customer Rating",color="Vehicle Type")
    fig3.update_layout(showlegend=True,height=420)
    st.plotly_chart(fig3)

#     sankey diagram
    st.subheader("Ride Flow Analysis")
    flow=df.groupby(["Vehicle Type","Booking Status"]).size().reset_index(name="Count")
    st.dataframe(flow)
    source_label=flow["Vehicle Type"].unique().tolist()
    target_label=flow["Booking Status"].unique().tolist()

    labels=source_label+target_label

    source=flow["Vehicle Type"].apply(
        lambda x:labels.index(x)).tolist()

    target=flow["Booking Status"].apply(
        lambda x:labels.index(x)).tolist()

    value=flow["Count"].tolist()

    import plotly.graph_objects as go

    fig4=go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="blue",width=0.5),label=labels,
        ),
        link=dict(source=source,
                  target=target,
                  value=value)
    )])
    st.plotly_chart(fig4)


# --------------------------------------------------------work-------------------------------------------------
#     1. Ride Demand by Vehicle Type
#     bar_chart = df.groupby("Vehicle Type").size().reset_index(name="Total Booking")
#     # st.dataframe(bar_chart)
#     fig5 = px.bar(bar_chart, x="Vehicle Type", y="Total Booking", color="Vehicle Type")
#     st.plotly_chart(fig5)
#
# #     2. Revenue by Vehicle Type
#     barh_chart = df.groupby("Vehicle Type")["Booking Value"].sum().reset_index()
#     # st.dataframe(barh_chart)
#     fig6 = px.bar(barh_chart, x="Booking Value", y="Vehicle Type", color="Vehicle Type", orientation="h")
#     st.plotly_chart(fig6)
#
#     col1, col2 = st.columns(2)
#
#     with col1:
#     #     3.Booking Status Distribution
#         dount_chart = df["Booking Status"].value_counts().reset_index(name="Ride Count")
#
#         fig8 = px.pie(dount_chart, values="Ride Count", names="Booking Status", hole=0.5)
#         # fig8.update_traces(textinfo="label")
#         st.plotly_chart(fig8, use_container_width=True)
#
#     with col2:
#     #   4. Payment Method Usage
#         pie_chart = df["Payment Method"].value_counts().reset_index(name="Usage")
#
#         fig7 = px.pie(pie_chart, values="Usage", names="Payment Method")
#         st.plotly_chart(fig7, use_container_width=True)
#
# #     5. Ride Distance vs Booking Value
#     scatter_chart=px.scatter(df,"Ride Distance","Booking Value",color="Vehicle Type")
#     st.plotly_chart(scatter_chart, use_container_width=True)
#
# #     6. Customer Rating Distribution
#     histogram=px.histogram(df,"Customer Rating",nbins=10)
#     st.plotly_chart(histogram, use_container_width=True)
#
# #     7. Cancellation Reasons Analysis
#     Horizontal_Bar_Chart=pd.concat([df["Reason for cancelling by Customer"],df["Driver Cancellation Reason"]])
#     data=Horizontal_Bar_Chart.value_counts().reset_index()
#     data.columns = ["Reason", "Count"]
#     st.dataframe(data)
#     h_bar_chart=px.bar(data,"Count","Reason",color="Reason")
#     st.plotly_chart(h_bar_chart, use_container_width=True)
#
# #     8. Average Distance by Vehicle Type
#     avg_ride_dis=df.groupby("Vehicle Type")["Ride Distance"].mean()
#     st.dataframe(avg_ride_dis)
#     bar_chart=px.bar(df,"Vehicle Type","Ride Distance",color="Vehicle Type")
#     st.plotly_chart(bar_chart, use_container_width=True)
#
# #     9. Booking Value Distribution
#     his=px.histogram(df,"Booking Value",nbins=10)
#     st.plotly_chart(his, use_container_width=True)
#
    # # 10. Operational Efficiency (CTAT vs VTAT)
    # scatter=px.scatter(df,"Avg CTAT","Avg VTAT",color="Vehicle Type")
    # st.plotly_chart(scatter, use_container_width=True)

# DATA ASSISTANT
if selected=="Data Assistant":
    st.title("Data Assistant")
    st.divider()

    st.write("Ask Question about dataset and get visual analytics")
    user_Questions=st.text_input("Ask me Question")

    if user_Questions:
        Q =user_Questions.lower()

        completed=df[df["Booking Status"]=="Completed"]

        #total rides
        if "total rides" in Q:
            total_rides=len(df)
            st.success(f"Total Rides in Dataset {total_rides}")

            status=df["Booking Status"].value_counts()

            fig = px.bar(x=status.index, y=status.values,
                         labels={"x":"Booking Status","y":"Ride Count"},
                         title="Ride Distribution by status")
            st.plotly_chart(fig,use_container_width=True)

        #revenue analysis

        elif "revenue" in Q:
            revenue=completed.groupby("Vehicle Type")["Booking Value"].sum()
            st.success(f"Total Revenue {revenue.sum():,.2f}")

            fig=px.bar(x=revenue.index, y=revenue.values,
                       title="Revenue by vehicle type",
                       labels={"x":"Vehicale Type","y":"Revenue"},)
            st.plotly_chart(fig)

        elif "vehicle" in Q:
            vehicle=df["Vehicle Type"].value_counts()
            st.success(f"Most Used Vehicle:{vehicle.idxmax()}")

            fig=px.pie(names=vehicle.index,values=vehicle.values,title="Vehicle Usage Distribution")
            st.plotly_chart(fig)

        # payment analysis
        elif "payment" in Q:
            payment = completed["Payment Method"].value_counts()
            fig = px.pie(
                names=payment.index, values=payment.values,
                title="Payment Method"
            )

            st.plotly_chart(fig)

        # cancellation
        elif "cancel" in Q:
            cancel = df["Booking Status"].value_counts()
            fig = px.bar(x=cancel.index, y=cancel.values,
                         title="Ride Status",
                         labels={"x": "Status", "y": "Ride Count"})
            st.plotly_chart(fig)

        # rating
        elif "rating" in Q:
                fig = px.histogram(completed, x="Customer Rating", nbins=10, title="Customer Rating")
                st.plotly_chart(fig)
                st.success(f"Average Rating: {completed["Customer Rating"].mean() :,.2f}")

        # distance
        elif "distance" in Q:
            fig = px.scatter(completed, x="Ride Distance",
                             y="Booking Value",
                             color="Vehicle Type",
                             title="Ride Distance by Booking Value")
            st.plotly_chart(fig)

        else:
            st.warning("Question not recognized , Try something like, cancellation, distance, revenue, rating, vehicle etc")
            st.divider()







