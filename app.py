import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# গুগল শিট কানেকশন সেটআপ
conn = st.connection("gsheets", type=GSheetsConnection)

# বর্তমান ডাটা রিড করা (যাতে SL. বের করা যায়)
existing_data = conn.read(spreadsheet="আপনার_শিট_URL_বা_নাম")
existing_data = existing_data.dropna(how="all")

# --- নতুন এন্ট্রি ফর্ম ---
with st.expander("➕ Add New Rental Entry"):
    with st.form(key="add_new_entry"):
        # স্বয়ংক্রিয়ভাবে পরবর্তী SL. নাম্বার জেনারেট করা
        next_sl = int(existing_data["SL."].max() + 1) if not existing_data.empty else 1
        st.write(f"Serial No: {next_sl}")

        col1, col2, col3 = st.columns(3)
        with col1:
            machine_name = st.selectbox("Machine Name", ["PLAIN MACHINE", "OVER LOCK", "FADE LOCK", "SNAP BUTTON"])
            brand = st.text_input("Brand")
        with col2:
            model = st.text_input("Model")
            serial_number = st.text_input("Serial Number")
        with col3:
            delivery_date = st.date_input("Delivery Date")
            challan = st.text_input("Challan No")

        running_factory = st.text_input("Running (Factory Name)")
        owner = st.selectbox("Owner", ["PSSC", "HS"])

        submit_button = st.form_submit_button(label="Save to Google Sheet")

        if submit_button:
            # নতুন ডাটার রো তৈরি
            new_data = pd.DataFrame([{
                "SL.": next_sl,
                "MACHINE NAME": machine_name.upper(),
                "BRAND": brand.upper(),
                "MODEL": model.upper(),
                "SERIAL NUMBER": serial_number,
                "DELIVERY": delivery_date.strftime('%d.%m.%Y'),
                "CHALLAN": challan,
                "OWNER": owner,
                "RUNNING": running_factory.upper()
            }])

            # আগের ডাটার সাথে নতুন ডাটা যোগ করা
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)

            # গুগল শিটে রাইট (Update) করা
            conn.update(spreadsheet="আপনার_শিট_URL", data=updated_df)
            st.success("Entry successfully saved to Google Sheet!")
            st.balloons()