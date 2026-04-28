import streamlit as st
import pandas as pd
import io
from datetime import datetime

st.set_page_config(page_title="Vendor CSV Mapper", page_icon="🔁")

st.title("🔁 Vendor CSV Mapper")
st.caption("Upload -> Map Columns -> Transform -> Export")

# Session State
if "step" not in st.session_state:
    st.session_state.step = 1
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "mapped_df" not in st.session_state:
    st.session_state.mapped_df = None
if "final_df" not in st.session_state:
    st.session_state.final_df = None
if "column_mapping" not in st.session_state:
    st.session_state.column_mapping = {}
if "filename" not in st.session_state:
    st.session_state.filename = "output"


SCHEMA = [
    {"name": "User_ID",          "required": True},
    {"name": "Transaction_Date", "required": True},
    {"name": "Amount",           "required": True},
]
REQUIRED = [f["name"] for f in SCHEMA if f["required"]]

# STEP 1: Upload 
if st.session_state.step == 1:
    st.subheader("Step 1: Upload your CSV file")
    st.write("Upload any vendor CSV file. Column names don't need to match the standard schema — you'll map them in the next step.")

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None:
        file_bytes = uploaded.read()

        @st.cache_data
        def load_csv(data):
            return pd.read_csv(io.BytesIO(data))

        df = load_csv(file_bytes)
        st.session_state.raw_df = df
        st.session_state.filename = uploaded.name.replace(".csv", "")

        st.success(f"File loaded: {uploaded.name}")
    
        st.write("**Preview (first 100 rows):**")
        st.dataframe(df.head(100))

    if st.button("Next ->", disabled=st.session_state.raw_df is None):
        st.session_state.step = 2
        st.rerun()

# STEP 2: Column Mapping 
elif st.session_state.step == 2:
    st.subheader("Step 2: Map Vendor Columns to Standard Schema")
    st.write("For each standard field, pick the matching column from your uploaded file. Required fields must be mapped.")

    df = st.session_state.raw_df
    vendor_cols = ["Choose"] + list(df.columns)
    mapping = {}

    for field in SCHEMA:
        fname = field["name"]
        label = fname + (" *(required)*" if field["required"] else " (optional)")
        saved = st.session_state.column_mapping.get(fname, "Choose")
        if saved not in vendor_cols:
            saved = "Choose"
        mapping[fname] = st.selectbox(label, vendor_cols, index=vendor_cols.index(saved), key=f"map_{fname}")

    st.session_state.column_mapping = mapping

    # Validate required fields
    errors = [f for f in REQUIRED if mapping.get(f) == "Choose"]
    if errors:
        st.error("Please map these required fields: " + ", ".join(errors))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("<- Back"):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("Next ->", disabled=bool(errors)):
            rename_map = {v: k for k, v in mapping.items() if v != "Choose"}
            mapped_df = df[list(rename_map.keys())].rename(columns=rename_map)
            st.session_state.mapped_df = mapped_df
            st.session_state.step = 3
            st.rerun()

# STEP 3: Transform 
elif st.session_state.step == 3:
    st.subheader("Step 3: Validate & Transform Data")

    df = st.session_state.mapped_df.copy()

    # Validation
    st.write("**Data Validation**")
    if "Amount" in df.columns:
        bad_amount = pd.to_numeric(df["Amount"], errors="coerce").isna().sum()
        if bad_amount > 0:
            st.error(f"Amount column has {bad_amount} non-numeric value(s).")
        else:
            st.success("Amount column looks good.")

    if "Transaction_Date" in df.columns:
        bad_dates = pd.to_datetime(df["Transaction_Date"], errors="coerce").isna().sum()
        if bad_dates > 0:
            st.warning(f"Transaction_Date has {bad_dates} unparseable value(s).")
        else:
            st.success("Transaction_Date column looks good.")

    total_nulls = df.isnull().sum().sum()
    if total_nulls > 0:
        st.warning(f"Total null values found: {total_nulls}")
    
    st.divider()

    # De-duplication
    st.write("**De-duplication**")
    dedup_on = st.checkbox("Remove duplicate rows")
    if dedup_on:
        dedup_col = st.selectbox("Select column to de-duplicate on:", df.columns.tolist())
        before = len(df)
        df = df.drop_duplicates(subset=[dedup_col])
        st.info(f"Removed {before - len(df)} duplicate(s) based on '{dedup_col}'.")

    st.divider()

    # Null handling
    st.write("**Null Handling**")
    null_on = st.checkbox("Handle null / empty cells")
    if null_on:
        strategy = st.radio("Choose strategy:", ["Fill with a value", "Fill with column mean"], horizontal=True)
        if strategy == "Fill with a value":
            fill_val = st.text_input("Fill value:", value="0")
            df = df.fillna(fill_val)
        else:
            num_cols = df.select_dtypes(include="number").columns.tolist()
            for c in num_cols:
                df[c] = df[c].fillna(df[c].mean())
            st.info("Filled numeric column nulls with their column mean.")

    st.divider()

    # Scaling
    st.write("**Amount Scaling**")
    scale_on = st.checkbox("Apply a multiplier to Amount column")
    if scale_on:
        if "Amount" not in df.columns:
            st.error("Amount column is not available.")
        else:
            multiplier = st.number_input("Multiplier (e.g. 1.18 for 18% tax):", min_value=0.0, value=1.0, step=0.01)
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df["Adjusted_Amount"] = df["Amount"] * multiplier
            st.write("Formula: Adjusted_Amount = Amount *", multiplier)
            st.dataframe(df[["Amount", "Adjusted_Amount"]].head(5))

    st.divider()

    st.write("**Preview after transformations (first 100 rows):**")
    st.dataframe(df.head(100))

    st.session_state.final_df = df

    col1, col2 = st.columns(2)
    with col1:
        if st.button("<- Back"):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Next ->"):
            st.session_state.step = 4
            st.rerun()

# STEP 4: Export 
elif st.session_state.step == 4:
    st.subheader("Step 4: Export Processed File")

    df = st.session_state.final_df
    st.write(f"Your file is ready to download. Final size: **{df.shape[0]} rows * {df.shape[1]} columns**")

    fmt = st.radio("Select export format:", ["CSV", "Excel (.xlsx)"], horizontal=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{st.session_state.filename}_processed_{timestamp}"

    if fmt == "CSV":
        data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Download CSV",
            data=data,
            file_name=filename + ".csv",
            mime="text/csv"
        )
    else:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Processed")
        st.download_button(
            label="⬇ Download Excel",
            data=buf.getvalue(),
            file_name=filename + ".xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.divider()
    st.write("**Final Data Preview (first 100 rows):**")
    st.dataframe(df.head(100))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
