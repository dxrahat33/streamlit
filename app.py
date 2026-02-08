import streamlit as st
import pandas as pd

# পেজ সেটআপ (রেসপন্সিভ এবং ডার্ক/লাইট মোড সাপোর্ট)
st.set_page_config(page_title="Machine Rental Dashboard", layout="wide")

# কাস্টম সিএসএস (টেইলউইন্ড এর মত লুক দেওয়ার জন্য)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-card { padding: 20px; border-radius: 10px; color: white; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)


# গুগল শিট থেকে ডাটা লোড করার ফাংশন
def load_data():
    sheet_id = "16_qxMxo5n9XrMc2oXU8VQuOzgNs3rfGxx146CSzcfgU"  # এখানে আপনার ID দিন
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    # ডেট কলাম ঠিক করা
    df['OUT DATE'] = pd.to_datetime(df['OUT DATE'], dayfirst=True, errors='coerce')
    return df


try:
    df = load_data()

    # --- সাইডবার ফিল্টার ---
    st.sidebar.header("🔍 Filter Options")
    month_list = ["All", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
    selected_month = st.sidebar.selectbox("Select Month", month_list)

    selected_brand = st.sidebar.multiselect("Select Brand", options=df["BRAND"].unique(), default=df["BRAND"].unique())

    # --- ডাটা ফিল্টারিং লজিক ---
    filtered_df = df[df["BRAND"].isin(selected_brand)]

    if selected_month != "All":
        month_idx = month_list.index(selected_month)
        filtered_df = filtered_df[filtered_df['OUT DATE'].dt.month == month_idx]

    # --- ড্যাশবোর্ড হেডার ---
    st.title("🧵 Machine Rental Pro-Dashboard")
    st.markdown(f"Showing results for: **{selected_month}**")

    # --- টপ কার্ডস (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Machines", len(filtered_df))
    col2.metric("Active Brands", filtered_df["BRAND"].nunique())
    col3.metric("On Rent", len(filtered_df[filtered_df['RETURN DATE'].isna()]))
    col4.metric("Returned", len(filtered_df[filtered_df['RETURN DATE'].notna()]))

    # --- মেইন ডাটা টেবিল ---
    st.subheader("📋 Machine Details List")
    st.dataframe(filtered_df, use_container_width=True)

    # --- চার্ট (ভিজ্যুয়ালাইজেশন) ---
    st.subheader("📊 Machine Distribution by Brand")
    brand_counts = filtered_df["BRAND"].value_counts()
    st.bar_chart(brand_counts)

except Exception as e:
    st.error("গুগল শিট কানেক্ট করতে সমস্যা হচ্ছে। আইডি ঠিক আছে কিনা চেক করুন।")