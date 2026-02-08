import streamlit as st
import pandas as pd

# পেজ সেটআপ
st.set_page_config(page_title="Machine Inventory Dashboard", layout="wide")

# ড্যাশবোর্ড স্টাইল (Tailwind লুকের জন্য)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; }
    div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
    .main { background-color: #f3f4f6; }
    </style>
    """, unsafe_allow_html=True)


# ডাটা লোড করার ফাংশন
def load_data():
    sheet_id = "16_qxMxo5n9XrMc2oXU8VQuOzgNs3rfGxx146CSzcfgU"  # আপনার শিট আইডি এখানে দিন
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    df = pd.read_csv(url)

    # কলামের নামগুলো পরিষ্কার করা (Spaces থাকলে সরিয়ে দেওয়া)
    df.columns = df.columns.str.strip()

    # ডেট ফরম্যাট ঠিক করা
    df['OUT DATE'] = pd.to_datetime(df['OUT DATE'], dayfirst=True, errors='coerce')
    return df


try:
    df = load_data()

    # --- ১. ড্যাশবোর্ড হেডার এবং গ্লোবাল সার্চ ---
    st.title("🏭 Smart Machine Inventory System")

    # গ্লোবাল সার্চ বক্স (যেকোনো কিছু লিখে সার্চ করা যাবে)
    search_query = st.text_input("🔍 Search anything (Serial, Company, Challan, Brand...)", "").lower()

    # --- ২. ডাটা ফিল্টারিং লজিক (Global Search) ---
    if search_query:
        # সব কলামকে স্ট্রিং বানিয়ে সার্চ করা হচ্ছে যাতে সব ফিল্ডে কাজ করে
        filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    else:
        filtered_df = df

    # --- ৩. ড্যাশবোর্ড ক্যালকুলেশন (Unique Logic) ---
    # সিরিয়াল নম্বর অনুযায়ী ইউনিক মেশিন বের করা
    unique_machines_df = df.drop_duplicates(subset=['SERIAL NUMBER'])
    total_unique_machines = len(unique_machines_df)

    # মেশিন নাম অনুযায়ী ইউনিক কয়টা করে মেশিন আছে (আপনার চাওয়া অনুযায়ী)
    machine_type_counts = unique_machines_df['MACHINE NAME'].value_counts()

    # --- ৪. ড্যাশবোর্ড কার্ডস (Top Section) ---
    st.subheader("📊 Key Metrics (Total Inventory)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Unique Machines", total_unique_machines)
    with col2:
        st.metric("Total Transactions", len(df))
    with col3:
        # বর্তমানে কয়টি মেশিন বাইরে আছে (Return Date নেই)
        currently_out = len(df[df['RETURN DATE'].isna()])
        st.metric("Currently on Rent", currently_out)

    # --- ৫. মেশিন টাইপ অনুযায়ী ইউনিক তালিকা ---
    with st.expander("📝 Show Inventory Summary (Unique Counts per Machine Type)"):
        st.write("সিরিয়াল নম্বর অনুযায়ী কোন ধরণের মেশিন প্রকৃত পক্ষে কয়টি আছে:")
        st.table(machine_type_counts)

    # --- ৬. মেইন ডাটা টেবিল ---
    st.subheader(f"📋 Records ({len(filtered_df)} items found)")
    # টেবিলটি সুন্দরভাবে দেখানোর জন্য
    st.dataframe(filtered_df.sort_values(by='OUT DATE', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}. দয়া করে শিট আইডি এবং কলামের নামগুলো চেক করুন।")