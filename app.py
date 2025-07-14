import streamlit as st
import pandas as pd
import joblib
import os
import datetime
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from app_retailer import show_retailer_dashboard
import hashlib

st.set_page_config(page_title="Return and Earn Portal", layout="centered")

# --- Dark Mode Toggle ---
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"  # Default is now Dark

theme_choice = st.sidebar.selectbox(
    "Theme", ["Light", "Dark"], 
    index=1 if st.session_state.theme_mode == "Dark" else 0
)
st.session_state.theme_mode = theme_choice

# Inject CSS for dark mode and light mode
if st.session_state.theme_mode == "Dark":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #181818 !important;
            color: #f1f1f1 !important;
        }
        .stButton>button, .stTextInput>div>input, .stSelectbox>div>div>div>input, .stNumberInput>div>input {
            background-color: #222 !important;
            color: #f1f1f1 !important;
            border: 1px solid #444 !important;
        }
        .stDataFrame, .stTable, .stMarkdown, .stTextArea>div>textarea {
            background-color: #222 !important;
            color: #f1f1f1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
elif st.session_state.theme_mode == "Light":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #f8f9fa !important;
            color: #111 !important;
        }
        .stButton>button, .stTextInput>div>input, .stSelectbox>div>div>div>input, .stNumberInput>div>input {
            background-color: #fff !important;
            color: #111 !important;
            border: 1px solid #ccc !important;
        }
        .stDataFrame, .stTable, .stMarkdown, .stTextArea>div>textarea {
            background-color: #fff !important;
            color: #111 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Load ML model and encoder
model = joblib.load("random_forest_model.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# Set default multiplier in session
if "credit_multiplier" not in st.session_state:
    st.session_state.credit_multiplier = 0.5  # default

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load user data
def load_users():
    if os.path.exists("users.csv"):
        return pd.read_csv("users.csv")
    else:
        return pd.DataFrame(columns=["username", "password"])

# Save new user
def save_user(username, password):
    users = load_users()
    new_user = pd.DataFrame([{"username": username, "password": hash_password(password)}])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)

# Check user credentials
def check_user(username, password):
    users = load_users()
    return ((users["username"] == username) & (users["password"] == hash_password(password))).any()

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Profile", "🔒 Admin Login"])

# Add logout button if logged in
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# ---------------------
# 🔐 Admin Login Page
# ---------------------
if page == "🔒 Admin Login":
    st.title("🔐 Admin Login")
    passcode = st.text_input("Enter Admin Passcode", type="password")
    if st.button("Login as Admin"):
        if passcode == "admin123":
            st.session_state.admin_mode = True
            st.success("✅ Access Granted")
            show_retailer_dashboard()
            st.stop()
        else:
            st.error("❌ Incorrect Passcode")

# ---------------------
# 🛠️ Retailer Dashboard (Already Logged In)
# ---------------------
elif st.session_state.admin_mode:
    st.title("🛠️ Retailer Dashboard")
    show_retailer_dashboard()
    st.stop()

# ---------------------
# 👤 Home Page (Customer Side)
# ---------------------
elif page == "Home":
    st.title("♻️ Return and Earn Portal")
    st.write("Return your used products and get rewards! Let's recycle smartly.")

    st.header("📦 Product Return Form")

    item_name = st.text_input("Item Name")
    condition = st.selectbox("Condition", ["New", "Good", "Fair", "Poor"])
    days_used = st.number_input("Days Used", min_value=0, step=1)

    # Pickup scheduling fields
    pickup_date = st.date_input("Preferred Pickup Date", min_value=datetime.date.today())
    pickup_time = st.time_input("Preferred Pickup Time")

    # --- Authentication ---
    if not st.session_state.logged_in:
        st.sidebar.title("🔑 Login / Register")
        auth_mode = st.sidebar.radio("Choose", ["Login", "Register"])
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if auth_mode == "Register":
            if st.sidebar.button("Register"):
                users = load_users()
                if username in users["username"].values:
                    st.sidebar.error("Username already exists.")
                elif username and password:
                    save_user(username, password)
                    st.sidebar.success("Registered! Please login.")
                else:
                    st.sidebar.warning("Enter username and password.")
            st.stop()
        else:
            if st.sidebar.button("Login"):
                if check_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.sidebar.success("Logged in!")
                else:
                    st.sidebar.error("Invalid credentials.")
            st.stop()

    if st.button("🚀 Submit Return"):
        if item_name and condition:
            try:
                # Encode condition
                condition_encoded = label_encoder.transform([condition])[0]
                input_df = pd.DataFrame([[condition_encoded, days_used]], columns=["condition_encoded", "days_used"])

                # Predict score and convert to credit (score is internal only)
                score = model.predict(input_df)[0]
                multiplier = st.session_state.get("credit_multiplier", 0.5)
                credit = round(score * multiplier)
                action = "RRR" if score <= 33 else "Repair" if score <= 66 else "Resell"

                # Save to return_logs.csv with timestamp
                log_data = pd.DataFrame([{
                    "Username": st.session_state.username,
                    "Product Name": item_name,
                    "Condition": condition,
                    "Days Used": days_used,
                    "Score": round(score, 2),
                    "Credit Earned": credit,
                    "action": action,
                    "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Pickup Date": str(pickup_date),
                    "Pickup Time": str(pickup_time)
                }])

                if os.path.exists("return_logs.csv"):
                    log_data.to_csv("return_logs.csv", mode='a', header=False, index=False)
                else:
                    log_data.to_csv("return_logs.csv", index=False)

                # Show credit only
                st.success(f"✅ Return submitted for '{item_name}'!")
                st.info(f"💸 Credit Earned: {credit} GreenPoints")
                st.balloons()

            except Exception as e:
                st.error(f"Something went wrong: {e}")
        else:
            st.warning("Please enter item name and select condition.")

# ---------------------
# 👤 Profile Page
# ---------------------
elif page == "Profile":
    st.title("👤 Your Profile")
    st.subheader("📝 Edit Details")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", "John Doe")
        with col2:
            email = st.text_input("Email", "john@example.com")
        address = st.text_area("Address", "123 Green Avenue, EcoCity")
        submitted = st.form_submit_button("💾 Save Changes")
        if submitted:
            st.success("✅ Profile updated!")

    st.markdown("---")
    st.subheader("📦 Your Return History")
    try:
        df = pd.read_csv("return_logs.csv")
        df = df[df["Username"] == st.session_state.username]
        st.dataframe(
            df[
                [
                    "Product Name", "Condition", "Days Used", "Score", "Credit Earned",
                    "action", "Pickup Date", "Pickup Time", "Time"
                ]
            ].sort_values("Time", ascending=False),
            use_container_width=True
        )
    except Exception:
        st.info("No return history yet.")

    # Leaderboard: show top users by credits
    st.markdown("---")
    st.subheader("🏆 Top Recyclers Leaderboard")
    try:
        df = pd.read_csv("return_logs.csv")
        leaderboard = df.groupby("Username")["Credit Earned"].sum().reset_index().sort_values("Credit Earned", ascending=False).head(10)
        leaderboard.columns = ["Username", "Total Credits"]
        st.table(leaderboard)
    except Exception:
        st.info("Leaderboard not available yet.")

    # Show only the logged-in user's profit (credits)
    st.subheader("🎉 Your Credits Earned")
    try:
        df = pd.read_csv("return_logs.csv")
        user_credits = df[df["Username"] == st.session_state.username]["Credit Earned"].sum()
        st.success(f"🌿 You have earned {user_credits} GreenPoints so far!")
    except:
        st.info("No returns submitted yet.")
        
    try:
        data = pd.read_csv("gdataset_100.csv")
        # Classify outcome
        def classify(score):
            if score <= 33:
                return "Recycle"
            elif score <= 66:
                return "Repair"
            else:
                return "Resell"
        data["Outcome"] = data["score"].apply(classify)
        outcome_counts = data["Outcome"].value_counts().reset_index()
        outcome_counts.columns = ["Outcome", "Count"]

        # Pie chart
        fig = px.pie(outcome_counts, names="Outcome", values="Count", title="Distribution of Item Outcomes")
        st.plotly_chart(fig)
        # Add open browser link for Streamlit app
        st.markdown(
            "[🌐 Open this app in your browser](http://localhost:8501)",
            unsafe_allow_html=True
        )
    except Exception as e:
        st.info(f"Could not load outcome distribution: {e}")