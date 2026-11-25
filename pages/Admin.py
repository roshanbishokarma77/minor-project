import ast
import base64
import os
import sqlite3
import pandas as pd
import streamlit as st
from auth import register_admin

# =========================================================
# CONFIGURATION
# =========================================================
MAIN_APP_FILE = "project.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "cleaned_travel_DATASET.csv")
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = r"D:\PROJECTBYME\cleaned_travel_DATASET.csv"

DB_PATH = os.path.join(BASE_DIR, "travel_database.db")

MONTH_OPTIONS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

st.set_page_config(
    page_title="Admin Dashboard - Discover Nepal",
    page_icon="🛠️",
    layout="wide",
)

# =========================================================
# DATABASE & FILE HELPER FUNCTIONS
# =========================================================
def load_data():
    """Safely load the dataset."""
    if os.path.exists(DATASET_PATH):
        try:
            return pd.read_csv(DATASET_PATH)
        except Exception as e:
            st.error(f"Error reading dataset: {e}")
            return None
    return None

def save_to_csv(df):
    """Save the DataFrame back to CSV."""
    try:
        df.to_csv(DATASET_PATH, index=False)
        return True
    except Exception as e:
        st.error(f"Failed to save CSV changes: {e}")
        return False

def sync_to_sqlite(df):
    """Sync the entire DataFrame into an SQLite database table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("destinations", conn, if_exists="replace", index=False)
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to sync with SQLite database: {e}")
        return False

def save_data_both(df):
    """Save data to both CSV and SQLite DB simultaneously."""
    csv_ok = save_to_csv(df)
    db_ok = sync_to_sqlite(df)
    return csv_ok and db_ok

initial_df = load_data()
if initial_df is not None:
    sync_to_sqlite(initial_df)

# =========================================================
# STYLING INJECTION (TEXT VISIBILITY FIX)
# =========================================================
def inject_admin_ui(image_path="images/nepal.jpg"):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
            bg_style = f"data:image/jpg;base64,{encoded}"
    else:
        bg_style = "https://t4.ftcdn.net/jpg/02/00/68/69/360_F_200686969_GJ7zbz2qaNIE4dyHSbZkQXvNPzRuwlr3.jpg"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
        .main, .block-container, [data-testid="stVerticalBlock"] {{
            background: transparent !important;
            background-color: transparent !important;
        }}

        .stApp {{
            background-image: url("{bg_style}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
        }}
        
        h1, h2, h3, h4, h5, h6, .stMarkdown p {{
            color: #FFFFFF !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            text-shadow: 0 3px 10px rgba(0, 0, 0, 0.95);
        }}

        label, div[data-testid="stWidgetLabel"] p {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}

        /* ENSURE INPUT FONT VISIBILITY ACROSS SEARCH & FORM FIELDS */
        input, select, textarea, div[data-baseweb="input"] input {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }}

        ::placeholder {{
            color: rgba(255, 255, 255, 0.6) !important;
            -webkit-text-fill-color: rgba(255, 255, 255, 0.6) !important;
        }}

        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
            background-color: rgba(15, 23, 42, 0.90) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
        }}

        div[data-baseweb="select"] span {{
            color: #FFFFFF !important;
        }}

        div.stButton > button {{
            width: 100%;
            height: 48px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
            background-color: #FFFFFF;
            color: #0F172A !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }}

        div.stButton > button:hover {{
            background-color: #3B82F6 !important;
            color: #FFFFFF !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_admin_ui()

# =========================================================
# AUTHENTICATION CHECKS
# =========================================================
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Please log in to access the Admin Dashboard.")
    if st.button("⬅️ Return to Login"):
        st.switch_page(MAIN_APP_FILE)
    st.stop()

if st.session_state.get("identity", "").strip().lower() != "admin":
    st.error(f"⛔ Access Denied! Logged in as: **'{st.session_state.get('identity', 'Unknown')}'**.")
    if st.button("🏠 Go to Home"):
        st.switch_page(MAIN_APP_FILE)
    st.stop()

# =========================================================
# ADMIN WORKSPACE
# =========================================================
st.title("🛠️ Admin Workspace - Nepal Destinations")
st.success(f"Welcome, **{st.session_state.get('username', 'Admin')}**!")
st.markdown("---")

option = st.selectbox(
    "Select Operation",
    ["View Destinations", "Add Destination", "Update Destination", "Delete Destination", "Register New Admin"],
)

df = load_data()

# ===========================
# 1. VIEW DESTINATIONS
# ===========================
if option == "View Destinations":
    st.subheader("📋 Destination Registry")

    if df is not None:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Destinations", len(df))
        m2.metric("Provinces Covered", df["province"].nunique() if "province" in df.columns else 0)
        m3.metric("Avg Cost (Min)", f"NPR {int(df['min_estimated_cost_per_person'].mean()):,}")
        m4.metric("Avg Cost (Max)", f"NPR {int(df['max_estimated_cost_per_person'].mean()):,}")

        st.markdown("<br>", unsafe_allow_html=True)

        col_search, col_prov = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("🔍 Search Destination", "", placeholder="Type destination name or tag...")
        with col_prov:
            prov_filter = st.selectbox("Province Filter", ["All"] + sorted(df["province"].unique().tolist()))

        df_filtered = df.copy()
        if prov_filter != "All":
            df_filtered = df_filtered[df_filtered["province"] == prov_filter]

        if search_query:
            df_filtered = df_filtered[
                df_filtered.astype(str)
                .apply(lambda row: row.str.contains(search_query, case=False))
                .any(axis=1)
            ]

        st.dataframe(df_filtered, use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Dataset as CSV",
            data=csv_data,
            file_name="cleaned_travel_DATASET.csv",
            mime="text/csv",
        )
    else:
        st.warning("⚠️ Could not load dataset file.")

# ===========================
# 2. ADD DESTINATION
# ===========================
elif option == "Add Destination":
    st.subheader("➕ Add New Destination")

    if df is not None:
        next_pid_default = int(df["pID"].max() + 1) if not df.empty else 1

        with st.form("add_destination_form"):
            c1, c2 = st.columns(2)
            with c1:
                pid_input = st.number_input("Destination ID (pID)*", min_value=1, value=next_pid_default, step=1)
                pname = st.text_input("Destination Name (pName)*")
                province = st.selectbox("Province", options=[1, 2, 3, 4, 5, 6, 7])
                min_days = st.number_input("Min Travel Days", min_value=1, value=1, step=1)
                max_days = st.number_input("Max Travel Days", min_value=1, value=3, step=1)
                min_cost = st.number_input("Min Estimated Cost (NPR)", min_value=0, value=5000, step=500)
                max_cost = st.number_input("Max Estimated Cost (NPR)", min_value=0, value=15000, step=1000)

            with c2:
                culture = st.slider("Culture Score", 0.0, 5.0, 3.0, step=0.5)
                adventure = st.slider("Adventure Score", 0.0, 5.0, 2.0, step=0.5)
                wildlife = st.slider("Wildlife Score", 0.0, 5.0, 1.0, step=0.5)
                sightseeing = st.slider("Sightseeing Score", 0.0, 5.0, 4.0, step=0.5)
                history = st.slider("History Score", 0.0, 5.0, 2.0, step=0.5)

            tags_input = st.text_input("Tags (comma or space-separated)", "temple, culture, scenic")
            months_selected = st.multiselect("Best Months to Visit", MONTH_OPTIONS, default=["October", "November"])

            submitted = st.form_submit_button("➕ Save Destination")

            if submitted:
                if pid_input in df["pID"].values:
                    st.error(f"pID `{pid_input}` already exists. Please enter a unique pID.")
                elif not pname.strip():
                    st.error("Please enter a valid Destination Name.")
                else:
                    tag_list = [t.strip().lower() for t in tags_input.replace(",", " ").split() if t.strip()]
                    tags_clean_str = " ".join(tag_list)
                    tags_clean_list_str = str(tag_list)
                    months_str = str(months_selected)

                    new_row = {
                        "pID": int(pid_input),
                        "pName": pname.strip(),
                        "culture": culture,
                        "adventure": adventure,
                        "wildlife": wildlife,
                        "sightseeing": sightseeing,
                        "history": history,
                        "province": province,
                        "min_travel_days": min_days,
                        "max_travel_days": max_days,
                        "min_estimated_cost_per_person": min_cost,
                        "max_estimated_cost_per_person": max_cost,
                        "tags_clean_list": tags_clean_list_str,
                        "tags_clean": tags_clean_str,
                        "best_months": months_str,
                    }

                    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data_both(updated_df):
                        st.success(f"✅ Created '{pname}' (pID: {pid_input}) successfully!")
                        st.rerun()

# ===========================
# 3. UPDATE DESTINATION
# ===========================
elif option == "Update Destination":
    st.subheader("✏️ Update Destination")

    if df is not None and not df.empty:
        dest_options = {f"{row['pName']} (pID: {row['pID']})": row['pID'] for _, row in df.iterrows()}
        selected_label = st.selectbox("Select Destination to Edit", list(dest_options.keys()))
        selected_pid = dest_options[selected_label]

        row_idx = df[df["pID"] == selected_pid].index[0]
        curr = df.loc[row_idx]

        def parse_list(val):
            try:
                parsed = ast.literal_eval(str(val))
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []

        curr_months = parse_list(curr.get("best_months", "[]"))
        default_months = [m for m in curr_months if m in MONTH_OPTIONS]

        with st.form("update_destination_form"):
            c1, c2 = st.columns(2)
            with c1:
                up_pid = st.number_input("Destination ID (pID)", value=int(curr["pID"]), disabled=True)
                up_pname = st.text_input("Destination Name (pName)", value=str(curr["pName"]))
                up_province = st.selectbox("Province", options=[1, 2, 3, 4, 5, 6, 7], index=int(curr["province"]) - 1)
                up_min_days = st.number_input("Min Travel Days", min_value=1, value=int(curr["min_travel_days"]), step=1)
                up_max_days = st.number_input("Max Travel Days", min_value=1, value=int(curr["max_travel_days"]), step=1)
                up_min_cost = st.number_input("Min Cost (NPR)", min_value=0, value=int(curr["min_estimated_cost_per_person"]), step=500)
                up_max_cost = st.number_input("Max Cost (NPR)", min_value=0, value=int(curr["max_estimated_cost_per_person"]), step=1000)

            with c2:
                up_culture = st.slider("Culture", 0.0, 5.0, float(curr["culture"]), step=0.5)
                up_adventure = st.slider("Adventure", 0.0, 5.0, float(curr["adventure"]), step=0.5)
                up_wildlife = st.slider("Wildlife", 0.0, 5.0, float(curr["wildlife"]), step=0.5)
                up_sightseeing = st.slider("Sightseeing", 0.0, 5.0, float(curr["sightseeing"]), step=0.5)
                up_history = st.slider("History", 0.0, 5.0, float(curr["history"]), step=0.5)

            up_tags = st.text_input("Tags", value=str(curr["tags_clean"]))
            up_months = st.multiselect("Best Months", MONTH_OPTIONS, default=default_months)

            submitted_update = st.form_submit_button("💾 Update Destination")

            if submitted_update:
                tag_list = [t.strip().lower() for t in up_tags.replace(",", " ").split() if t.strip()]

                df.at[row_idx, "pName"] = up_pname.strip()
                df.at[row_idx, "province"] = up_province
                df.at[row_idx, "min_travel_days"] = up_min_days
                df.at[row_idx, "max_travel_days"] = up_max_days
                df.at[row_idx, "min_estimated_cost_per_person"] = up_min_cost
                df.at[row_idx, "max_estimated_cost_per_person"] = up_max_cost
                df.at[row_idx, "culture"] = up_culture
                df.at[row_idx, "adventure"] = up_adventure
                df.at[row_idx, "wildlife"] = up_wildlife
                df.at[row_idx, "sightseeing"] = up_sightseeing
                df.at[row_idx, "history"] = up_history
                df.at[row_idx, "tags_clean"] = " ".join(tag_list)
                df.at[row_idx, "tags_clean_list"] = str(tag_list)
                df.at[row_idx, "best_months"] = str(up_months)

                if save_data_both(df):
                    st.success(f"✅ Destination '{up_pname}' updated successfully!")
                    st.rerun()

# ===========================
# 4. DELETE DESTINATION
# ===========================
elif option == "Delete Destination":
    st.subheader("🗑️ Delete Destination")

    if df is not None and not df.empty:
        dest_options = {f"{row['pName']} (pID: {row['pID']})": row['pID'] for _, row in df.iterrows()}
        selected_label = st.selectbox("Select Destination to Remove", list(dest_options.keys()))
        selected_pid = dest_options[selected_label]

        dest_row = df[df["pID"] == selected_pid].iloc[0]

        st.warning(f"⚠️ Are you sure you want to delete **{dest_row['pName']}** (pID: {dest_row['pID']})?")
        
        if st.button("Confirm Deletion"):
            updated_df = df[df["pID"] != selected_pid]
            if save_data_both(updated_df):
                st.success(f"🗑️ Deleted '{dest_row['pName']}' successfully!")
                st.rerun()

# ===========================
# 5. REGISTER NEW ADMIN
# ===========================
elif option == "Register New Admin":
    st.subheader("🛡️ Register New Admin Account")
    st.caption("Only accessible to logged-in admins. New admin accounts created here can log in from the main portal.")

    with st.form("register_admin_form"):
        admin_u = st.text_input("Admin Username", key="reg_adm_u")
        admin_email = st.text_input("Admin Email Address", key="reg_adm_e")
        admin_p = st.text_input("Admin Password", type="password", key="reg_adm_p")
        confirm_admin_p = st.text_input("Confirm Admin Password", type="password", key="reg_adm_cp")

        submitted_admin = st.form_submit_button("🛡️ Register Admin Account")

        if submitted_admin:
            if not admin_u or not admin_email or not admin_p:
                st.error("Please fill in all required fields.")
            elif admin_p != confirm_admin_p:
                st.error("Passwords do not match.")
            else:
                if register_admin(admin_u, admin_email, admin_p):
                    st.success(f"✅ Admin account '{admin_u}' registered successfully!")
                else:
                    st.error("Admin registration failed. Username may already exist.")

# ===========================
# LOGOUT ACTION
# ===========================
st.markdown("---")
if st.button("🚪 Logout of Admin Panel"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.identity = ""
    st.switch_page(MAIN_APP_FILE)