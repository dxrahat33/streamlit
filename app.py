import streamlit as st
import pandas as pd

# পেজ সেটআপ - ড্যাশবোর্ডটিকে আধুনিক লুক দেওয়ার জন্য
st.set_page_config(page_title="PSSC Machine Tracker", layout="wide")

# কাস্টম সিএসএস (Tailwind Inspired)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }
    .main { background-color: #f9fafb; }
    h1 { color: #1f2937; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=600)  # ১০ মিনিট পর পর ডাটা অটো আপডেট হবে
def load_data():
    sheet_id = "16_qxMxo5n9XrMc2oXU8VQuOzgNs3rfGxx146CSzcfgU"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # স্পেস রিমুভ করা

    # ডেট কলামগুলো কনভার্ট করা
    df['DELIVERY'] = pd.to_datetime(df['DELIVERY'], dayfirst=True, errors='coerce')
    # RETURN কলাম যদি ডেট হয় তবে কনভার্ট করুন
    return df


try:
    df = load_data()

    st.title("🏭 PARVEZ SEWING & SERVICING CENTER")
    st.markdown("---")

    # --- ১. স্মার্ট সার্চ সেকশন ---
    search_query = st.text_input("🔍 Quick Search", placeholder="Type Serial, Company Name, or Machine Type...").lower()

    if search_query:
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    else:
        filtered_df = df

    # --- ২. মেট্রিক্স সেকশন (Unique Logic) ---
    unique_machines_df = df.drop_duplicates(subset=['SERIAL NUMBER'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Machines (Unique)", len(unique_machines_df))
    with col2:
        st.metric("Total Rent Records", len(df))
    with col3:
        # RETURN কলাম চেক করে ভাড়ায় থাকা মেশিন বের করা
        rented_count = len(df[df['RETURN'].isna() | (df['RETURN'] == "")])
        st.metric("Currently on Rent", rented_count)
    with col4:
        st.metric("Total Clients", df['RUNNING'].nunique() if 'RUNNING' in df.columns else 0)

    st.markdown("---")

    # --- ৩. মেইন কন্টেন্ট এলাকা (দুই কলামে ভাগ করা) ---
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader(f"📋 Records ({len(filtered_df)} found)")
        # টেবিল দেখানোর আগে ডেট ফরম্যাট সুন্দর করা
        display_df = filtered_df.copy()
        display_df['DELIVERY'] = display_df['DELIVERY'].dt.strftime('%d-%b-%Y')
        st.dataframe(display_df, use_container_width=True, height=500)

    with right_col:
        st.subheader("📝 Inventory Summary")
        # মেশিন টাইপ অনুযায়ী ইউনিক কাউন্ট
        type_summary = unique_machines_df['MACHINE NAME'].value_counts().reset_index()
        type_summary.columns = ['Machine Type', 'Stock']
        st.table(type_summary)

        # ডাউনলোড বাটন (CSV হিসেবে ব্যাকআপ রাখার জন্য)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full Backup", data=csv, file_name="machine_inventory_backup.csv",
                           mime="text/csv")

except Exception as e:
    st.error(f"Something went wrong: {e}")