import streamlit as st
import pandas as pd

# পেজ সেটআপ
st.set_page_config(page_title="PSSC Dashboard", layout="wide")

# CSS দিয়ে লুক উন্নত করা
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)


# ডাটা লোড করার ফাংশন
def load_data():
    # আপনার শিট আইডি
    sheet_id = "16_qxMxo5n9XrMc2oXU8VQuOzgNs3rfGxx146CSzcfgU"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()  # কলামের নামের স্পেস মোছা
    return df


try:
    df = load_data()

    st.title("🏭 PARVEZ SEWING & SERVICING CENTER")

    # --- নতুন এন্ট্রি ফর্ম (শুধুমাত্র প্রদর্শনের জন্য) ---
    with st.expander("➕ Add New Entry Info"):
        last_sl = int(df['SL.'].max()) if not df.empty else 0
        st.write(f"পরবর্তী ক্রমিক নম্বর (SL): **{last_sl + 1}**")
        st.info("নতুন এন্ট্রি যোগ করতে সরাসরি আপনার Google Sheet-এ গিয়ে লিখুন। এখানে ১ মিনিটের মধ্যে আপডেট হয়ে যাবে।")

    # --- গ্লোবাল সার্চ ---
    search = st.text_input("🔍 Search (Serial, Company, Model...)", "")

    if search:
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
    else:
        filtered_df = df

    # --- মেট্রিক্স ---
    unique_m = df.drop_duplicates(subset=['SERIAL NUMBER'])

    c1, c2, c3 = st.columns(3)
    c1.metric("Unique Machines", len(unique_m))
    c2.metric("Total Transactions", len(df))
    # আপনার শিটে কলামের নাম 'RETURN DAT' আছে কিনা চেক করে নিন
    on_rent = len(df[df['RETURN DAT'].isna()]) if 'RETURN DAT' in df.columns else 0
    c3.metric("Currently On Rent", on_rent)

    # --- ডাটা টেবিল ---
    st.subheader("📋 Machine Records")
    st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")