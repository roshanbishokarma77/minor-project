import base64
import os
import streamlit as st
from auth import login_admin, login_user, register_user
from backend import DestinationRecommender

# =========================================================
# FILE OVERVIEW (project.py)
# =========================================================
# 1) Page config + session state initialization
# 2) get_bg_url()          -> background image helper
# 3) get_logo_data_uri()   -> loads Nepal Tourism logo
# 4) inject_custom_ui()    -> CSS with uniform light-slate button styling
# 5) render_nav_buttons()  -> top navigation links
# 6) render_info_page()    -> generic grid layout helper
# 7) render_province_page(), render_heritage_page(), render_mountain_page(),
#    render_adventure_page(), render_festival_page() -> content pages
# 8) Main Views            -> handles render states and authentication tab UI
# =========================================================

# ==========================
# Page Configuration
# ==========================
st.set_page_config(
    page_title="Discover Nepal - Tourism Portal",
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
if "show_auth" not in st.session_state:
    st.session_state.show_auth = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False


# ==========================
# Load Recommendation Engine (cached so it only trains/loads once)
# ==========================
@st.cache_resource
def load_recommender():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "cleaned_travel_DATASET.csv")
    cache_path = os.path.join(script_dir, "model_cache.pkl")
    return DestinationRecommender(data_path, model_cache_path=cache_path)


engine = load_recommender()


# ==========================
# Styling & Background Injection
# ==========================
def get_bg_url(image_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, image_path)

    if os.path.exists(full_path):
        with open(full_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
            return f"data:image/jpeg;base64,{encoded}"
    elif os.path.exists(image_path):
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
            return f"data:image/jpeg;base64,{encoded}"
    else:
        return "https://images.unsplash.com/photo-1544735716-392fe2489ffa?q=80&w=1920&auto=format&fit=crop"


def get_logo_data_uri():
    candidates = [
        "images/web_logo.jpeg",
        "web_logo.jpeg",
        "images/web_logo.jpg",
        "web_logo.jpg",
        "images/web_logo.png",
        "web_logo.png",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))

    for relative_path in candidates:
        full_path = os.path.join(script_dir, relative_path)
        for target in (full_path, relative_path):
            if os.path.exists(target):
                ext = target.split(".")[-1].lower()
                mime = "png" if ext == "png" else "jpeg"
                with open(target, "rb") as img:
                    encoded = base64.b64encode(img.read()).decode()
                    return f"data:image/{mime};base64,{encoded}"

    return "https://cdn-icons-png.flaticon.com/512/3014/3014287.png"


def inject_custom_ui(image_path, is_logged_in=False):
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap');

        /* Clean Background & Typography Base */
        html, body, .stApp, [data-testid="stAppViewContainer"] {
            background-color: #F8FAFC !important;
            font-family: 'Inter', sans-serif;
            color: #1E293B !important;
        }

        /* Ensure default headers don't overlap layout */
        [data-testid="stHeader"] {
            display: none !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding-top: 20px !important;
            padding-bottom: 40px !important;
        }

        /* Top Bar Toggle / Close Button Styling Base */
        .st-key-profile_toggle_btn button {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            border-radius: 8px !important;
            padding: 8px 20px !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            cursor: pointer !important;
            float: right;
            transition: all 0.2s ease-in-out !important;
        }

        .st-key-profile_toggle_btn button p,
        .st-key-profile_toggle_btn button span {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        .st-key-profile_toggle_btn button:hover {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
        }

        /* ALL TABS MATCHING LOGIN/REGISTER BUTTON STYLE */
        button[data-baseweb="tab"] {
            background-color: #E2E8F0 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 8px 16px !important;
            margin-right: 4px !important;
            transition: all 0.2s ease-in-out !important;
        }

        /* Fully visible tab text */
        button[data-baseweb="tab"] p, 
        button[data-baseweb="tab"] div,
        button[data-baseweb="tab"] span {
            color: #0F172A !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"]:hover {
            background-color: #CBD5E1 !important;
        }

        /* Selected Active Tab Highlight */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
            border-bottom: 2px solid #059669 !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] div,
        button[data-baseweb="tab"][aria-selected="true"] span {
            color: #0F172A !important;
        }

        /* FORM SUBMIT BUTTONS MATCHING LOGIN/REGISTER */
        .st-key-login_card button {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .st-key-login_card button p, 
        .st-key-login_card button span {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        .st-key-login_card button:hover {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
        }

        /* SET RECOMMENDATIONS BUTTON MATCHING LOGIN/REGISTER STYLE */
        .st-key-btn_rec_main button {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .st-key-btn_rec_main button p, 
        .st-key-btn_rec_main button span {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        .st-key-btn_rec_main button:hover {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
        }

        /* LOGOUT BUTTON MATCHING LOGIN/REGISTER STYLE */
        .st-key-bottom_logout_btn button {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .st-key-bottom_logout_btn button p, 
        .st-key-bottom_logout_btn button span {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        .st-key-bottom_logout_btn button:hover {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
        }

        /* GENERIC FORM SUBMIT BUTTONS (e.g. preference quiz "Get My Recommendations")
           These have no explicit .st-key-* class, so they were falling back to
           the default (dark-on-dark) theme. Matching the same light-slate style
           used everywhere else. */
        div[data-testid="stFormSubmitButton"] button {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease-in-out !important;
        }

        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stFormSubmitButton"] button span,
        div[data-testid="stFormSubmitButton"] button div {
            color: #0F172A !important;
            font-weight: 700 !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background-color: #CBD5E1 !important;
            border-color: #94A3B8 !important;
        }

        /* Input Fields Styling */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stSelectbox div[role="combobox"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }

        .stTextInput label, .stSelectbox label {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        .stTextInput input::placeholder {
            color: #94A3B8 !important;
        }

        /* Number Input Fields (e.g. budget, travel days) --
           previously unstyled, causing low-contrast text */
        div[data-testid="stNumberInput"] input {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            font-weight: 600 !important;
            -webkit-text-fill-color: #0F172A !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stNumberInput"] label {
            color: #1E293B !important;
            font-weight: 600 !important;
        }

        div[data-testid="stNumberInput"] button {
            background-color: #E2E8F0 !important;
            border: 1px solid #CBD5E1 !important;
        }

        div[data-testid="stNumberInput"] button svg {
            fill: #0F172A !important;
        }

        /* Slider Labels (e.g. Culture, Adventure, Wildlife, Sightseeing, History) --
           previously unstyled, causing invisible/low-contrast label text */
        div[data-testid="stSlider"] label,
        div[data-testid="stSlider"] label p,
        div[data-testid="stSlider"] label div,
        div[data-testid="stSlider"] label span {
            color: #1E293B !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        .login-nav-logo-title {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .login-nav-logo-title h2 {
            margin: 0;
            font-size: 1.6rem;
            font-weight: 800;
            color: #1E3A8A !important;
            letter-spacing: -0.02em;
        }
        .login-nav-logo-img {
            height: 48px;
            width: 48px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #CBD5E1;
            flex-shrink: 0;
        }

        .nav-contact-info {
            text-align: right;
        }
        .nav-contact-item {
            font-size: 0.82rem;
            color: #475569 !important;
            font-weight: 600;
            line-height: 1.5;
        }

        .nav-divider {
            border-top: 1px solid #E2E8F0;
            margin: 12px 0;
        }

        /* Nav Category Buttons */
        .st-key-nav_links_row div.stButton > button {
            background-color: transparent !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            border-radius: 0px !important;
            box-shadow: none !important;
            font-size: 0.85rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
            padding: 6px 0px !important;
            width: 100% !important;
            cursor: pointer !important;
        }

        .st-key-nav_links_row div.stButton > button p,
        .st-key-nav_links_row div.stButton > button span {
            color: #334155 !important;
            font-weight: 700 !important;
        }

        .st-key-nav_links_row div.stButton > button:hover p,
        .st-key-nav_links_row div.stButton > button:hover span {
            color: #059669 !important;
        }
        
        .st-key-nav_links_row div.stButton > button:hover {
            border-bottom: 2px solid #059669 !important;
        }
        
        .st-key-nav_links_row div.stButton > button[kind="primary"] {
            border-bottom: 2px solid #059669 !important;
        }

        .st-key-nav_links_row div.stButton > button[kind="primary"] p,
        .st-key-nav_links_row div.stButton > button[kind="primary"] span {
            color: #059669 !important;
        }

        /* Login Container Card */
        .st-key-login_card {
            background: #FFFFFF !important;
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08) !important;
            padding: 20px !important;
            margin-top: 15px;
            margin-bottom: 25px;
        }

        .st-key-hero_panel {
            background: #EAF6F1 !important;
            border-radius: 28px !important;
            padding: 40px 35px !important;
            margin-top: 15px;
        }

        .hero-tagline {
            font-family: 'Caveat', cursive;
            font-size: 2.3rem;
            color: #059669;
            font-weight: 700;
            margin: 0 0 6px 0;
        }

        .hero-headline {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            color: #0F172A !important;
            line-height: 1.15;
            margin: 0 0 16px 0;
        }

        .hero-copy {
            font-size: 1.05rem;
            color: #475569 !important;
            font-weight: 500;
        }

        .hero-blob-img {
            width: 100%;
            max-width: 480px;
            height: 380px;
            object-fit: cover;
            border-radius: 50% 50% 45% 55% / 60% 40% 60% 40%;
            box-shadow: 0 15px 30px rgba(15, 23, 42, 0.15);
            border: 5px solid #FFFFFF;
        }

        .destination-card-title {
            font-weight: 800;
            font-size: 1.05rem;
            color: #0F172A;
            margin: 12px 0 4px 0;
        }

        .destination-card-text {
            font-size: 0.9rem;
            color: #64748B;
            line-height: 1.4;
        }

        .badge-pill {
            display: inline-block;
            font-size: 0.75rem;
            padding: 4px 12px;
            border-radius: 50px;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }
        .badge-guest { background: #FEF3C7; color: #D97706 !important; border: 1px solid #F59E0B; }
        .badge-admin { background: #FEE2E2; color: #DC2626 !important; border: 1px solid #DC2626; }
        .badge-user { background: #D1FAE5; color: #059669 !important; border: 1px solid #10B981; }

        /* Province Map Banner */
        .province-map-banner {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #FFFFFF;
            border-radius: 16px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            padding: 20px;
            margin-bottom: 28px;
        }
        .province-map-banner img {
            width: 100%;
            max-height: 420px;
            object-fit: contain;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# RECOMMENDATION RESULT CARDS
# =========================================================
def render_recommendation_cards(results_df):
    if results_df is None or results_df.empty or "error" in getattr(results_df, "columns", []):
        st.warning("No matching destinations found. Try adjusting your search or filters.")
        return

    cols_per_row = 3
    rows = results_df.to_dict("records")
    for i in range(0, len(rows), cols_per_row):
        row_items = rows[i:i + cols_per_row]
        cols = st.columns(len(row_items))
        for col, item in zip(cols, row_items):
            with col:
                st.markdown(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E2E8F0;
                                border-radius:14px; padding:16px 18px; margin-bottom:14px;
                                box-shadow:0 4px 12px rgba(0,0,0,0.05);">
                        <div class="destination-card-title">📍 {item['pName']}</div>
                        <div class="destination-card-text">
                            <b>Tags:</b> {item['tags']}<br>
                            <b>Province:</b> {item['province']} &nbsp;|&nbsp;
                            <b>Best months:</b> {item['best_months']}<br>
                            <b>Duration:</b> {item['travel_days']} days &nbsp;|&nbsp;
                            <b>Cost/person:</b> Rs. {item['cost_per_person']}<br>
                            <b>Match score:</b> {round(item['similarity_score'] * 100, 1)}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# TOP NAV BUTTONS
# =========================================================
def render_nav_buttons():
    nav_items = [
        ("HOME", "Home"),
        ("PROVINCE", "Province"),
        ("WORLD HERITAGE", "World Heritage"),
        ("MOUNTAIN", "Mountain"),
        ("ADVENTURE", "Adventure"),
        ("FESTIVAL", "Festival"),
    ]

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    with st.container(key="nav_links_row"):
        nav_cols = st.columns(len(nav_items))
        for col, (label, page_name) in zip(nav_cols, nav_items):
            with col:
                btn_key = "nav_btn_" + page_name.lower().replace(" ", "_")
                is_active = st.session_state.current_page == page_name
                if st.button(
                    label,
                    key=btn_key,
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_name
                    st.rerun()


# =========================================================
# GENERIC CONTENT-PAGE LAYOUT
# =========================================================
def render_info_page(page_title, tagline, intro_text, items):
    st.markdown(f"<h1 style='margin-top:0;'>{page_title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-tagline' style='font-size:1.4rem;'>{tagline}</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#475569; font-size:1.05rem; max-width:900px;'>{intro_text}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    cols_per_row = 3
    for i in range(0, len(items), cols_per_row):
        row_items = items[i:i + cols_per_row]
        cols = st.columns(len(row_items))
        for col, item in zip(cols, row_items):
            with col:
                st.image(item["image"], use_container_width=True)
                st.markdown(
                    f'<div class="destination-card-title">{item["name"]}</div>'
                    f'<div class="destination-card-text">{item["desc"]}</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# PROVINCE PAGE
# =========================================================
def render_province_page():
    st.markdown(
        """
        <div class="province-map-banner">
            <img src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjCJnL1zOJKE2HcOIeRgFB2Gip3wNhouMCgtlWr-_8NcPq9fMn0uF2vOYtmNgflNhKdbdP9iX5XwQZFsSYPwqp4RAXdp35UAqA3w1EVpctN7shwq7x4CF2A7P5A39NIy2J78EDJN_WOcbL1fgDQaa6OP0sStPq3VP_clW2NhGWstxfUPYnB7MGyq8cMyQ/s718/nepal-provincial-map.webp"
                 alt="Map of Nepal showing its 7 provinces">
        </div>
        """,
        unsafe_allow_html=True,
    )

    items = [
        {
            "name": "Koshi Province",
            "desc": "Eastern Nepal's tea gardens, Kanchenjunga views, and the wetlands of Koshi Tappu.",
            "image": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/07/f4/75/59/ilam-nepal.jpg?w=500&h=-1&s=1",
        },
        {
            "name": "Madhesh Province",
            "desc": "The fertile southern plains, famed for the Janaki Temple and vibrant Terai culture.",
            "image": "https://admin.buddhaair.com/upload/blog/mainimage/1574326731_0y9PQ_1570963880-smgrp-janaki-temple.webp",
        },
        {
            "name": "Bagmati Province",
            "desc": "Home to Kathmandu Valley - the political, cultural, and heritage heart of Nepal.",
            "image": "https://production-origin-cdn.couchsurfing.com/ag6boBMEKEfQaeHMG6sripbGXAA=/900x500/filters:quality(90)/cms-content/kathmandu_bagmati_province_nepal_ss_1_50d19ab3fc/kathmandu_bagmati_province_nepal_ss_1_50d19ab3fc.jpg",
        },
        {
            "name": "Gandaki Province",
            "desc": "Lake city Pokhara, the Annapurna range, and some of Nepal's best trekking routes.",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRUR1Po4tBjwdGyAitReHkpJrR8LoswQCz1U-sBYwaGcA&s=10",
        },
        {
            "name": "Lumbini Province",
            "desc": "Birthplace of Lord Buddha and a gateway to Nepal's sacred pilgrimage sites.",
            "image": "https://images.unsplash.com/photo-1662441646729-77e1a3f90bd0?w=900&auto=format&fit=crop&q=60",
        },
        {
            "name": "Karnali Province",
            "desc": "Nepal's largest, most remote province - Rara Lake and untouched highland wilderness.",
            "image": "https://highcampadventure.com/uploads/fullbanner/biggest-lake-of-nepal-rara-lake.webp",
        },
        {
            "name": "Sudurpashchim Province",
            "desc": "The far-west - Khaptad National Park, Api Himal, and rich indigenous traditions.",
            "image": "https://cdn.getyourguide.com/img/tour/5b30c9b488a7dd17f1f2c909d6947d34f7f4415d727a2bfac6626fb3c2c82692.png/68.jpg",
        },
    ]
    render_info_page(
        page_title="Provinces of Nepal",
        tagline="7 Provinces, One Nation",
        intro_text="Nepal is divided into seven provinces, each with its own landscape, language, and culture.",
        items=items,
    )


# =========================================================
# WORLD HERITAGE PAGE
# =========================================================
def render_heritage_page():
    items = [
        {
            "name": "Kathmandu Durbar Square",
            "desc": "A UNESCO World Heritage Site showcasing centuries of Nepal palace architecture.",
            "image": "https://images.locationscout.net/2019/08/kathmandu-durbar-square-nepal.webp?h=1400&q=80",
        },
        {
            "name": "Pashupatinath Temple",
            "desc": "One of the holiest Hindu temples in the world, on the banks of the Bagmati River.",
            "image": "https://holidaynepal.com/pilgrim-site/images/pashupatinath.jpg",
        },
        {
            "name": "Swayambhunath (Monkey Temple)",
            "desc": "An ancient Buddhist stupa overlooking the Kathmandu Valley.",
            "image": "https://www.himalayanadventureintl.com/public/uploads/Swayambhunath%20Temple%20Tour.jpg",
        },
        {
            "name": "Boudhanath Stupa",
            "desc": "One of the largest spherical stupas in the world and a hub of Tibetan Buddhism.",
            "image": "https://boudhamandalahotel.com/wp-content/uploads/2026/01/1765369040001-li6eb03w3bd.jpg",
        },
        {
            "name": "Lumbini",
            "desc": "The birthplace of Lord Buddha, with sacred gardens and ancient monasteries.",
            "image": "https://images.unsplash.com/photo-1662441646729-77e1a3f90bd0?w=900&auto=format&fit=crop&q=60",
        },
        {
            "name": "Chitwan National Park",
            "desc": "A UNESCO natural heritage site, home to rhinos, tigers, and dense jungle.",
            "image": "https://images.unsplash.com/photo-1687725008439-d37fbe641329?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGNoaXR3YW4lMjBuYXRpb25hbCUyMHBhcmt8ZW58MHx8MHx8fDA%3D",
        },
        {
            "name": "Patan Durbar Square",
            "desc": "Renowned for its fine arts, architecture, and rich Newari tradition.",
            "image": "https://cms.altitudehimalaya.com/media/Blog/Travel-Stories/Patan-DS/Patan-Durbar-Square.png",
        },
        {
            "name": "Sagarmatha National Park",
            "desc": "Home to Mount Everest, unique Sherpa culture, and alpine biodiversity.",
            "image": "https://www.magicalnepal.com/wp-content/uploads/2025/07/image.png",
        },
        {
            "name": "Bhaktapur Durbar Square",
            "desc": "A preserved open-air museum of traditional art, pottery, and historic architecture.",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7ds5FODOUglKpeRhsxguqz0ZyGJsIVB4xHoSdSM9uaef95vCZTKscYwA&s=10",
        },
    ]
    render_info_page(
        page_title="World Heritage Sites of Nepal",
        tagline="UNESCO-Listed Treasures",
        intro_text="Nepal is home to iconic UNESCO World Heritage Sites, spanning ancient temples and protected wilderness.",
        items=items,
    )


# =========================================================
# MOUNTAIN PAGE
# =========================================================
def render_mountain_page():
    items = [
        {
            "name": "Mount Everest (8,849m)",
            "desc": "The tallest mountain on Earth, straddling the Nepal-China border.",
            "image": "https://cdn.britannica.com/39/76239-050-DE5FCF36/Climbers-side-Nepali-Mount-Everest.jpg",
        },
        {
            "name": "Kanchenjunga (8,586m)",
            "desc": "The world's third-highest peak, situated on the border of Nepal and India.",
            "image": "https://media.breezeadventure.com/uploads/fullbanner/kanchenjunga-expedition.webp",
        },
        {
            "name": "Lhotse (8,516m)",
            "desc": "Known as the world's fourth-highest mountain, connected to Mount Everest.",
            "image": "https://sevensummittreks.com/uploads/original/1649329007_lhotse-HuIFJQwvX2i9Z2klxItQXLo91kV5EUqNPlEPXCWL.jpg",
        },
        {
            "name": "Makalu (8,463m)",
            "desc": "Known as the world's fifth-highest mountain, with its distinctive pyramid-shaped peak.",
            "image": "https://images.squarespace-cdn.com/content/v1/55d729cfe4b00ab3960e7989/5ef5597c-6f98-4e32-bf58-a33d2b714297/2nEKh_eventfulldetailimage.jpg",
        },
        {
            "name": "Cho Oyu (8,201m)",
            "desc": "Known as the world's sixth-highest mountain, near the Nepal-Tibet border.",
            "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRrqkuub9bdsTRWLAlrAKSV3GWT0pmdgiaA-U3eFfT06ZVlsriRByIRL14b&s=10",
        },
        {
            "name": "Dhaulagiri (8,167m)",
            "desc": "Known as the White Mountain, the world's seventh-highest peak.",
            "image": "https://www.mountaintribes.com/wp-content/uploads/2019/03/dhaulagiri-trek-600x365.jpg",
        },
        {
            "name": "Manaslu (8,163m)",
            "desc": "Known as the 'Mountain of the Spirit', with a popular trekking circuit.",
            "image": "https://s3.amazonaws.com/www.explorersweb.com/wp-content/uploads/2022/08/25171629/Manaslu-jon-fore.jpeg",
        },
        {
            "name": "Annapurna I (8,091m)",
            "desc": "One of the world's most challenging peaks, centerpiece of the Annapurna Circuit.",
            "image": "https://bekkcjkhrsfqwznxidkg.supabase.co/storage/v1/object/public/blog-images/8108-bca30c6a-48b6-4d0e-ae2f-feda98407a75-a47cdca81a3181d48cd8f5cab47aee3d.jpg",
        },
        {
            "name": "Machapuchare (6,993m)",
            "desc": "The sacred 'Fishtail' peak above Pokhara - closed to climbing out of reverence.",
            "image": "https://c.stocksy.com/a/yhB000/z9/45010.jpg",
        },
    ]
    render_info_page(
        page_title="Mountains of Nepal",
        tagline="Roof of the World",
        intro_text="Nepal is home to eight of the world's fourteen 8,000m peaks, offering unmatched alpine beauty.",
        items=items,
    )


# =========================================================
# ADVENTURE PAGE
# =========================================================
def render_adventure_page():
    items = [
        {
            "name": "Everest Base Camp Trek",
            "desc": "A classic multi-day trek through Sherpa villages to the foot of Everest.",
            "image": "https://media.istockphoto.com/id/474395838/photo/tents-in-everest-base-camp-nepal-himalayas.webp?a=1&b=1&s=612x612&w=0&k=20&c=WeCF-ztfvjyNNKAYAQf7uwwJDhSV7eFwxSMhsLJ9mmM=",
        },
        {
            "name": "Paragliding in Pokhara",
            "desc": "Soar above Phewa Lake with the Annapurna mountain range in view.",
            "image": "https://thumbs.dreamstime.com/b/paragliding-over-pokhara-nepal-paragliders-float-s-fewa-lake-lakeside-tourist-area-130866203.jpg",
        },
        {
            "name": "White-Water Rafting",
            "desc": "Raft the Trishuli or Bhote Koshi rivers through scenic river gorges.",
            "image": "https://media.nepaltrekadventures.com/uploads/img/white-water-rafting-in-trishuli.webp",
        },
        {
            "name": "Bungee Jumping",
            "desc": "Experience heart-pumping leaps across deep Himalayan river valleys.",
            "image": "https://assets-excellenttrek.b-cdn.net/wp-content/uploads/2019/04/Bungee-in-Pokhara-350x254.gif",
        },
        {
            "name": "Jungle Safari, Chitwan",
            "desc": "Spot rhinos, wild elephants, and Bengal tigers on jeep safaris.",
            "image": "https://www.chitwanjungleguides.com/wp-content/uploads/2019/01/chitwan-jungle-jeep-safariwww.chitwanjungleguides.com_.png",
        },
        {
            "name": "Mountain Biking, Mustang",
            "desc": "Ride through the unique high-altitude landscapes of Upper Mustang.",
            "image": "https://theeverestholiday.com/_next/image?url=https%3A%2F%2Fapp.theeverestholiday.com%2Fuploads%2Fpackage%2Fmustang-mountain-bike-tour-450.webp&w=2048&q=75&dpl=dpl_3FbaZQ5v4LfEmKJNQYDBuNgat89f",
        },
    ]
    render_info_page(
        page_title="Adventure in Nepal",
        tagline="For the Thrill-Seekers",
        intro_text="From mountain biking and white-water rafting to high treks, Nepal offers endless outdoor adventure.",
        items=items,
    )


# =========================================================
# FESTIVAL PAGE
# =========================================================
def render_festival_page():
    items = [
        {
            "name": "Dashain",
            "desc": "Nepal's major festival celebrating the victory of good over evil with family gatherings.",
            "image": "https://peacefulnepal.com/wp-content/uploads/2026/07/dashain-festival-nepal.webp",
        },
        {
            "name": "Tihar (Festival of Lights)",
            "desc": "A vibrant five-day festival honoring animals, family bonds, and the goddess Laxmi.",
            "image": "https://republicaimg.nagariknewscdn.com/shared/web/uploads/media/tihar-deepawali.jpg",
        },
        {
            "name": "Holi",
            "desc": "The festival of colors, welcoming the spring season with music and joy.",
            "image": "https://backpacktonepal.com/wp-content/uploads/2026/04/Holi-celebration-at-Basantapur-Durbar-Square-1024x683.png",
        },
        {
            "name": "Bisket Jatra",
            "desc": "A traditional street festival in Bhaktapur featuring chariot processions.",
            "image": "https://namastenepaltrekking.com/wp-content/uploads/2025/04/Bisket-Jatra-Bhaktapur-scaled.webp",
        },
        {
            "name": "Buddha Jayanti",
            "desc": "Marks the birth of Lord Buddha, celebrated in Lumbini and stupas across Nepal.",
            "image": "https://www.nepalsanctuarytreks.com/wp-content/uploads/2018/09/budda-jayanti-bouddhanath.jpg",
        },
        {
            "name": "Chhath",
            "desc": "A holy festival dedicated to the Sun God, celebrated along river banks.",
            "image": "https://cdn.britannica.com/70/272970-050-A52A08D1/Hindu-Devotees-Gather-Near-The-Ganga-Ghats-To-Offer-Prayers-During-The-Chhath-Puja-Festival.jpg",
        },
        {
            "name": "Eid",
            "desc": "The beautiful celebration of compassion, gratitude, and togetherness, shared with family and friends across Nepal.",
            "image": "https://english.onlinekhabar.com/wp-content/uploads/2016/09/eid-photo-19.jpg",
        },
        {
            "name": "Christmas",
            "desc": "The magical celebration of Christmas, filling hearts with hope, peace, and happiness across Nepal.",
            "image": "https://assets-cdn.kathmandupost.com/uploads/source/news/2017/miscellaneous/Christmas-Celebrations--3--25122017082750.JPG",
        },
    ]
    render_info_page(
        page_title="Festivals of Nepal",
        tagline="A Land of Celebrations",
        intro_text="Nepal is a multi-religious country known for its cultural diversity and religious harmony. The major religions practiced are Hinduism, Buddhism, Kirat, Christianity.Nepal's calendar is full of vibrant celebrations, religious traditions, and cultural heritage.",
        items=items,
    )


# Inject Custom CSS Stylesheet
inject_custom_ui("images/nepal.jpg", is_logged_in=st.session_state.logged_in)

# =========================================================
# VIEW 1: AUTHENTICATION & VISITOR MODE (If NOT Logged In)
# =========================================================
if not st.session_state.logged_in:

    logo_uri = get_logo_data_uri()

    # Top Header Row
    title_col, profile_col = st.columns([3, 1])

    with title_col:
        st.markdown(
            f"""
            <div class="login-nav-logo-title">
                <img class="login-nav-logo-img" src="{logo_uri}" alt="Nepal Tourism Logo">
                <h2>🇳🇵 Nepal Tourism</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with profile_col:
        btn_label = (
            "❌ Close" if st.session_state.show_auth else "👤 Login / Register"
        )
        if st.button(
            btn_label, key="profile_toggle_btn", use_container_width=True
        ):
            st.session_state.show_auth = not st.session_state.show_auth
            st.rerun()

    # Category Bar
    render_nav_buttons()

    # Dynamic drawer for login/register when toggle is True
    if st.session_state.show_auth:
        auth_col1, auth_col2, auth_col3 = st.columns([1, 2.2, 1])

        with auth_col2:
            with st.container(border=True, key="login_card"):
                auth_tab1, auth_tab2 = st.tabs(
                    ["🔑 Login", "👤 User Register"]
                )

                with auth_tab1:
                    st.subheader("Account Login")
                    login_user_input = st.text_input("Username", key="login_u")
                    login_pass_input = st.text_input(
                        "Password", type="password", key="login_p"
                    )

                    login_role = st.selectbox(
                        "Login As", ["User", "Admin"], key="login_role"
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(
                        "Sign In",
                        key="btn_login_submit",
                        use_container_width=True,
                    ):
                        if login_user_input and login_pass_input:
                            user_record = None
                            if login_role.lower() == "admin":
                                user_record = login_admin(
                                    login_user_input, login_pass_input
                                )
                            else:
                                user_record = login_user(
                                    login_user_input, login_pass_input
                                )

                            if user_record:
                                st.session_state.logged_in = True
                                st.session_state.username = login_user_input
                                st.session_state.identity = login_role.lower()
                                st.session_state.show_auth = False
                                st.session_state.current_page = "Home"

                                # DIRECT ADMIN TO ADMIN DASHBOARD UPON LOGIN
                                if st.session_state.identity == "admin":
                                    try:
                                        st.switch_page("pages/admin.py")
                                    except Exception:
                                        st.switch_page("admin.py")
                                else:
                                    st.success(f"Welcome back, {login_user_input}!")
                                    st.rerun()
                            else:
                                st.error("Invalid username or password.")
                        else:
                            st.error(
                                "Please enter both Username and Password."
                            )

                with auth_tab2:
                    st.subheader("Create New User Account")
                    new_u = st.text_input("Choose Username", key="reg_u")
                    new_email = st.text_input("Email Address", key="reg_e")
                    new_p = st.text_input(
                        "Password", type="password", key="reg_p"
                    )
                    confirm_p = st.text_input(
                        "Confirm Password", type="password", key="reg_cp"
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(
                        "Register User Account",
                        key="btn_reg_user",
                        use_container_width=True,
                    ):
                        if not new_u or not new_p:
                            st.error("Please fill in all required fields.")
                        elif new_p != confirm_p:
                            st.error("Passwords do not match.")
                        else:
                            # Update to Database via auth.py
                            if register_user(new_u, new_email, new_p):
                                st.success(
                                    "Registration successful! Please go to the Login tab."
                                )
                            else:
                                st.error(
                                    "Registration failed. Username may already exist."
                                )

    # Page router for non-logged-in users
    if st.session_state.current_page == "Home":

        with st.container(key="hero_panel"):
            hero_text_col, hero_img_col = st.columns([1.1, 1], gap="large")

            with hero_text_col:
                st.markdown(
                    """
                    <div class="hero-tagline">Natural Beauty</div>
                    <div class="hero-headline">Unlock the Beauty<br>of Nepal with Us</div>
                    <p class="hero-copy">
                        Less planning, more exploring — handpicked treks,
                        heritage tours and mountain getaways across Nepal,
                        tailored to how you like to travel.
                    </p>
                    """,
                    unsafe_allow_html=True,
                )

            with hero_img_col:
                st.markdown(
                    """
                    <img class="hero-blob-img"
                         src="https://images.unsplash.com/photo-1544735716-392fe2489ffa?q=80&w=1200&auto=format&fit=crop"
                         alt="Himalayan mountain scenery">
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            "<h2 style='text-align:center; font-weight:800;'>Popular Destinations in Nepal</h2>"
            "<p style='text-align:center; color:#64748B; margin-bottom:20px;'>"
            "A few of the places travelers fall in love with first.</p>",
            unsafe_allow_html=True,
        )

        dest_c1, dest_c2, dest_c3 = st.columns(3)

        with dest_c1:
            st.image(
                "https://media.istockphoto.com/id/474395838/photo/tents-in-everest-base-camp-nepal-himalayas.webp?a=1&b=1&s=612x612&w=0&k=20&c=WeCF-ztfvjyNNKAYAQf7uwwJDhSV7eFwxSMhsLJ9mmM=",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Everest Base Camp</div>'
                '<div class="destination-card-text">Trek through Sherpa villages '
                "and glacial valleys to the foot of the world's highest peak.</div>",
                unsafe_allow_html=True,
            )

        with dest_c2:
            st.image(
                "https://images.unsplash.com/photo-1611516491426-03025e6043c8?w=800&auto=format&fit=crop",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Kathmandu Heritage</div>'
                '<div class="destination-card-text">Wander centuries-old durbar squares, '
                "temples and courtyards in the historic capital.</div>",
                unsafe_allow_html=True,
            )

        with dest_c3:
            st.image(
                "https://images.unsplash.com/photo-1662441646729-77e1a3f90bd0?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bHVtYmluaSUyMG5lcGFsfGVufDB8fDB8fHww",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Lumbini</div>'
                '<div class="destination-card-text">Walk peaceful sacred gardens where '
                "timeless stupas honor the historic birthplace of Buddha at dawn.</div>",
                unsafe_allow_html=True,
            )

    elif st.session_state.current_page == "Province":
        render_province_page()
    elif st.session_state.current_page == "World Heritage":
        render_heritage_page()
    elif st.session_state.current_page == "Mountain":
        render_mountain_page()
    elif st.session_state.current_page == "Adventure":
        render_adventure_page()
    elif st.session_state.current_page == "Festival":
        render_festival_page()

# =========================================================
# VIEW 2: DASHBOARD MODE (If Logged In)
# =========================================================
else:
    is_guest = st.session_state.identity == "guest"
    is_admin = st.session_state.identity == "admin"
    user_display = st.session_state.username

    badge_html = (
        '<span class="badge-pill badge-guest">Guest Mode</span>'
        if is_guest
        else (
            '<span class="badge-pill badge-admin">Admin</span>'
            if is_admin
            else '<span class="badge-pill badge-user">User</span>'
        )
    )

    title_col, contact_col = st.columns([2, 2])

    with title_col:
        st.markdown(
            f'<div class="login-nav-logo-title"><h2>🇳🇵 NEPAL Tourism </h2>{badge_html}</div>',
            unsafe_allow_html=True,
        )

    with contact_col:
        st.markdown(
            """
            <div class="nav-contact-info">
                <div class="nav-contact-item">📞 +061-123456 (Nepal)</div>
                <div class="nav-contact-item">✉️ info@nepaltourism.net</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_nav_buttons()

    if is_guest:
        st.info("💡 You are currently exploring in **Guest Mode**.")

    # Page router for logged-in users
    if st.session_state.current_page == "Home":
        st.subheader(f"Welcome back, {user_display}!")

        col_a, col_b = st.columns(2)
        with col_a:
            all_place_names = engine.get_all_place_names()
            search_query = st.selectbox(
                "Search Destinations",
                options=[""] + all_place_names,
                index=0,
                format_func=lambda x: "Type or pick a place (e.g., Pokhara...)" if x == "" else x,
                key="txt_search_destination",
            )

        with col_b:
            st.markdown(
                "<div style='margin-top: 28px;'></div>", unsafe_allow_html=True
            )
            if st.button(
                "⭐ Set Recommendations",
                key="btn_rec_main",
                use_container_width=True,
            ):
                st.session_state.show_quiz = not st.session_state.show_quiz

        # ---- Mode 1: Item-based recommendations ("More like this place") ----
        if search_query:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"🔎 Because you looked at: {search_query}")
            results = engine.recommend_similar(search_query, top_k=6)
            render_recommendation_cards(results)

        # ---- Mode 2: Preference-quiz based recommendations ----
        if st.session_state.show_quiz:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🎯 Tell us what you love")
            with st.form(key="preference_quiz_form"):
                q1, q2, q3, q4, q5 = st.columns(5)
                culture = q1.slider("Culture", 0, 5, 3)
                adventure = q2.slider("Adventure", 0, 5, 3)
                wildlife = q3.slider("Wildlife", 0, 5, 2)
                sightseeing = q4.slider("Sightseeing", 0, 5, 3)
                history = q5.slider("History", 0, 5, 2)

                f1, f2, f3, f4 = st.columns(4)
                province_choice = f1.selectbox(
                    "Province (optional)", options=["Any"] + engine.get_provinces()
                )
                budget = f2.number_input(
                    "Max budget (Rs.)", min_value=0, max_value=500000, value=20000, step=1000
                )
                days = f3.number_input(
                    "Trip length (days)", min_value=1, max_value=60, value=3, step=1
                )
                month = f4.selectbox(
                    "Travel month (optional)",
                    options=[
                        "Any", "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December",
                    ],
                )
                preferred_tags = st.text_input(
                    "Anything specific you're after? (optional, e.g. 'temple lake trekking')"
                )

                submitted = st.form_submit_button("Get My Recommendations")

            if submitted:
                filters = {}
                if province_choice != "Any":
                    filters["province"] = province_choice
                if budget:
                    filters["max_budget"] = budget
                if days:
                    filters["travel_days"] = days
                if month != "Any":
                    filters["month"] = month

                preferences = {
                    "culture": culture,
                    "adventure": adventure,
                    "wildlife": wildlife,
                    "sightseeing": sightseeing,
                    "history": history,
                }
                quiz_results = engine.recommend_from_preferences(
                    preferences, top_k=6, preferred_tags=preferred_tags, **filters
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("✨ Recommended for you")
                render_recommendation_cards(quiz_results)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📸 Popular Highlights")

        img_c1, img_c2, img_c3 = st.columns(3)
        with img_c1:
            st.image(
                "https://media.istockphoto.com/id/474395838/photo/tents-in-everest-base-camp-nepal-himalayas.webp?a=1&b=1&s=612x612&w=0&k=20&c=WeCF-ztfvjyNNKAYAQf7uwwJDhSV7eFwxSMhsLJ9mmM=",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Everest Base Camp</div>'
                '<div class="destination-card-text">Trek through Sherpa villages to the foot of Everest.</div>',
                unsafe_allow_html=True,
            )

        with img_c2:
            st.image(
                "https://images.unsplash.com/photo-1611516491426-03025e6043c8?w=800&auto=format&fit=crop",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Kathmandu Heritage</div>'
                '<div class="destination-card-text">Wander historic durbar squares and temples.</div>',
                unsafe_allow_html=True,
            )

        with img_c3:
            st.image(
                "https://images.unsplash.com/photo-1662441646729-77e1a3f90bd0?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bHVtYmluaSUyMG5lcGFsfGVufDB8fDB8fHww",
                use_container_width=True,
            )
            st.markdown(
                '<div class="destination-card-title">Lumbini</div>'
                '<div class="destination-card-text">Peaceful sacred gardens and historical stupas.</div>',
                unsafe_allow_html=True,
            )

    elif st.session_state.current_page == "Province":
        render_province_page()
    elif st.session_state.current_page == "World Heritage":
        render_heritage_page()
    elif st.session_state.current_page == "Mountain":
        render_mountain_page()
    elif st.session_state.current_page == "Adventure":
        render_adventure_page()
    elif st.session_state.current_page == "Festival":
        render_festival_page()

    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🚪 Logout Account", key="bottom_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.identity = ""
        st.session_state.current_page = "Home"
        st.rerun()