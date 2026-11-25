import base64
import os
import streamlit as st

# ==========================
# Page Configuration
# ==========================
st.set_page_config(
    page_title="Discover Nepal",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================
# Initialize Session States
# ==========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "identity" not in st.session_state:
    st.session_state.identity = ""  # 'user', 'admin', or 'guest'


# ==========================
# Styling & Theme Injection
# ==========================
def inject_custom_ui(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
            bg_style = f"data:image/jpg;base64,{encoded}"
    else:
        bg_style = "https://images.unsplash.com/photo-1544735716-392fe2489ffa?q=80&w=1920&auto=format&fit=crop"

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* -------------------------------------------------------------
           1. FORCE ROOT & ALL CONTAINER TRANSPARENCY
        ------------------------------------------------------------- */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
        .main, .block-container, [data-testid="stVerticalBlock"], 
        [data-testid="stAppViewBlockContainer"] {{
            background: transparent !important;
            background-color: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            filter: none !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }}

        /* 2. BACKGROUND IMAGE */
        .stApp {{
            background-image: url("{bg_style}") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        /* 3. TYPOGRAPHY & DROP-SHADOWS */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: #FFFFFF !important;
        }}
        
        h1, h2, h3, h4, h5, h6, .hero-title, .stMarkdown p {{
            color: #FFFFFF !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            text-shadow: 0 3px 10px rgba(0, 0, 0, 0.95), 0 1px 4px rgba(0, 0, 0, 0.9);
        }}

        /* 4. MAIN CONTAINER FRAMEWORK - NO BORDER OR SHADOW */
        [data-testid="stMainBlockContainer"] {{
            background: transparent !important;
            background-color: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: none !important;
            outline: none !important;
            border-radius: 0px !important;
            padding: 40px 35px !important;
            margin-top: 20px !important;
            margin-bottom: 20px !important;
            box-shadow: none !important;
        }}

        /* Hero Container */
        .hero-container {{
            text-align: center;
            color: #FFFFFF;
            margin-bottom: 30px;
            padding: 10px 0;
        }}
        
        .hero-title {{
            font-size: 2.8rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            margin-bottom: 10px;
            color: #FFFFFF !important;
            text-shadow: 0 4px 14px rgba(0, 0, 0, 0.95);
        }}

        .hero-subtitle {{
            font-size: 1.15rem;
            color: #FFFFFF !important;
            margin-bottom: 0px;
            font-weight: 600;
            text-shadow: 0 3px 8px rgba(0, 0, 0, 0.95);
        }}

        .glass-panel {{
            padding: 10px 0px;
        }}

        /* Labels */
        label, div[data-testid="stWidgetLabel"] p {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            text-shadow: 0 2px 6px rgba(0, 0, 0, 0.95);
        }}

        /* Badges */
        .badge-pill {{
            display: inline-block;
            font-size: 0.85rem;
            padding: 5px 14px;
            border-radius: 50px;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            vertical-align: middle;
            margin-left: 8px;
        }}
        .badge-guest {{
            background: rgba(245, 158, 11, 0.6);
            color: #FBBF24 !important;
            border: 1px solid #F59E0B;
        }}
        .badge-admin {{
            background: rgba(59, 130, 246, 0.6);
            color: #93C5FD !important;
            border: 1px solid #3B82F6;
        }}
        .badge-user {{
            background: rgba(16, 185, 129, 0.6);
            color: #6EE7B7 !important;
            border: 1px solid #10B981;
        }}

        /* Tabs Cleaned Up (Removed Red Active Colors/Highlight Borders) */
        div[data-baseweb="tab-list"] {{
            gap: 10px;
            background-color: rgba(15, 23, 42, 0.75) !important;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
        }}

        div[data-baseweb="tab"] {{
            height: 44px;
            border-radius: 8px;
            color: #E2E8F0 !important;
            font-weight: 600 !important;
            border: none !important;
            background-color: transparent !important;
        }}

        div[data-baseweb="tab"][aria-selected="true"] {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            box-shadow: none !important;
        }}

        div[data-baseweb="tab-highlight"] {{
            background-color: transparent !important;
        }}

        /* Inputs & Select Boxes */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
            background-color: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
        }}
        
        div[data-baseweb="input"] input {{
            color: #FFFFFF !important;
            font-weight: 500 !important;
            font-size: 1rem !important;
        }}

        /* Primary Action Buttons */
        div.stButton > button {{
            width: 100%;
            height: 48px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 700;
            background-color: #FFFFFF;
            color: #0F172A !important;
            border: none !important;
            transition: all 0.25s ease-in-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        }}

        div.stButton > button:hover {{
            background-color: #3B82F6 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(59, 130, 246, 0.6);
        }}

        /* Image Display Cards */
        [data-testid="stImage"] img {{
            border-radius: 12px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
        }}
        [data-testid="stImage"] img:hover {{
            transform: scale(1.02);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7);
        }}

        /* Alerts */
        div[data-testid="stAlert"] {{
            background-color: rgba(15, 23, 42, 0.85) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            color: #FFFFFF !important;
            border-radius: 12px;
            font-weight: 500;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_ui("images/nepal.jpg")

# =========================================================
# VIEW 1: AUTHENTICATION (If NOT Logged In)
# =========================================================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-title">🏔️ Tourist Destination Recommendation System</div>
            <p class="hero-subtitle">Discover tailored travel pathways across the heart of the Himalayas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center authentication form container
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2.2, 1])

    with auth_col2:
        auth_tab1, auth_tab2, auth_tab3 = st.tabs(
            ["🔑 Login", "👤 User Register", "🛡️ Admin Register"]
        )

        # ------------------
        # Tab 1: Login
        # ------------------
        with auth_tab1:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.subheader("Account Login")
            login_user = st.text_input("Username", key="login_u")
            login_pass = st.text_input(
                "Password", type="password", key="login_p"
            )

            login_role = st.selectbox(
                "Login As", ["User", "Admin"], key="login_role"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", key="btn_login_submit"):
                if login_user and login_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.session_state.identity = login_role.lower()
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Please enter both Username and Password.")

            st.markdown("---")
            if st.button("🌐 Continue as Guest", key="btn_guest_submit"):
                st.session_state.logged_in = True
                st.session_state.username = "Traveler"
                st.session_state.identity = "guest"
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # ------------------
        # Tab 2: User Register
        # ------------------
        with auth_tab2:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.subheader("Create New User Account")
            new_u = st.text_input("Choose Username", key="reg_u")
            new_email = st.text_input("Email Address", key="reg_e")
            new_p = st.text_input("Password", type="password", key="reg_p")
            confirm_p = st.text_input(
                "Confirm Password", type="password", key="reg_cp"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register User Account", key="btn_reg_user"):
                if not new_u or not new_p:
                    st.error("Please fill in all required fields.")
                elif new_p != confirm_p:
                    st.error("Passwords do not match.")
                else:
                    st.success(
                        "Registration successful! Please go to the Login tab."
                    )

            st.markdown("</div>", unsafe_allow_html=True)

        # ------------------
        # Tab 3: Admin Register
        # ------------------
        with auth_tab3:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.subheader("Create Admin Account")
            admin_u = st.text_input("Admin Username", key="adm_u")
            admin_p = st.text_input(
                "Admin Password", type="password", key="adm_p"
            )
            secret_key = st.text_input(
                "Admin Secret Key / Token", type="password", key="adm_key"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Register Admin Account", key="btn_reg_admin"):
                if secret_key != "NEPAL_ADMIN_2026":
                    st.error("Invalid Secret Key. Registration denied.")
                elif not admin_u or not admin_p:
                    st.error("Please fill in all required fields.")
                else:
                    st.success(
                        "Admin registration successful! You can now log in as Admin."
                    )

            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# VIEW 2: HOMEPAGE DASHBOARD (If Logged In)
# =========================================================
else:
    is_guest = st.session_state.identity == "guest"
    is_admin = st.session_state.identity == "admin"
    user_display = st.session_state.username

    if is_guest:
        badge = '<span class="badge-pill badge-guest">Guest Mode</span>'
    elif is_admin:
        badge = '<span class="badge-pill badge-admin">Admin</span>'
    else:
        badge = '<span class="badge-pill badge-user">User</span>'

    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-title">🏔️ Tourist Destination Recommendation System</div>
            <h3>Namaste, {user_display} 👋 {badge}</h3>
            <p class="hero-subtitle">Discover tailor-made experiences across the landscapes of Nepal.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_guest:
        st.info(
            "💡 You are currently exploring in **Guest Mode**. Feel free to search destinations and view sample recommendations!"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Explore Modules")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Search Destinations", key="btn_search"):
            st.info("Search page module selected.")

    with col2:
        if st.button("⭐ Get Personal Recommendations", key="btn_recommendation"):
            st.info("Recommendation page module selected.")

    if is_admin:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🛡️ Admin Workspace")
        if st.button("⚙️ Manage Destinations & Database", key="btn_admin"):
            st.info("Admin dashboard will be opened.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Featured Destination Gallery
    st.subheader("📸 Popular Destinations")
    img_col1, img_col2, img_col3 = st.columns(3)

    with img_col1:
        st.image(
            "https://media.istockphoto.com/id/474395838/photo/tents-in-everest-base-camp-nepal-himalayas.webp?a=1&b=1&s=612x612&w=0&k=20&c=WeCF-ztfvjyNNKAYAQf7uwwJDhSV7eFwxSMhsLJ9mmM=",
            caption="Himalayan Ranges",
        )

    with img_col2:
        st.image(
            "https://images.unsplash.com/photo-1611516491426-03025e6043c8?w=600&auto=format&fit=crop",
            caption="Kathmandu Heritage",
        )

    with img_col3:
        st.image(
            "https://images.unsplash.com/photo-1662441646729-77e1a3f90bd0?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bHVtYmluaSUyMG5lcGFsfGVufDB8fDB8fHww",
            caption="Pokhara Phewa Lake",
        )

    st.markdown("<br><hr>", unsafe_allow_html=True)

    logout_label = "🚪 Exit Guest Mode" if is_guest else "🚪 Logout"
    if st.button(logout_label, key="logout_home"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.identity = ""
        st.rerun()