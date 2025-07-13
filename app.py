import streamlit as st
import os

from app_retailer import show_retailer_dashboard

st.set_page_config(page_title="Return and Earn Portal", layout="centered")

# Session state for admin
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ⬛ Sidebar navigation (with Admin Login inside it)
page = st.sidebar.selectbox("Navigate", ["Home", "Profile", "🔒 Admin Login"])

# ---------------------
# 🛠️ Admin Section
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
# 🛠️ Retailer Dashboard if already logged in
# ---------------------
elif st.session_state.admin_mode:
    st.title("🛠️ Retailer Dashboard")
    show_retailer_dashboard()
    st.stop()

# ---------------------
# 👤 Home Page (Customer)
# ---------------------
elif page == "Home":
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: flex-end; margin-bottom: 20px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='40' style='margin-right: 10px; border-radius: 50%;'>
        <span style='font-size: 18px; font-weight: bold;'>Hello, John Doe</span>
    </div>
    """, unsafe_allow_html=True)

    st.title("♻️ Return and Earn Portal")
    st.write("Return your used products and get rewards! Let's recycle smartly.")

    st.header("📦 Product Information")
    product_name = st.text_input("Product Name")
    category = st.selectbox("Category", ["Electronics", "Clothing", "Plastic", "Others"])
    reason = st.text_area("Reason for Return")
    condition = st.selectbox("Product Condition", ["Like New", "Slightly Used", "Damaged", "Not Working"])

    st.header("🖼️ Upload Product Image")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    if st.button("🚀 Submit"):
        if product_name and uploaded_file:
            image_path = os.path.join("uploads", uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Return for '{product_name}' submitted successfully!")
            st.balloons()
        else:
            st.warning("Please fill in all fields and upload an image.")

# ---------------------
# 👤 Profile Page
# ---------------------
elif page == "Profile":
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 20px; margin-bottom: 20px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/3135/3135715.png' width='80' style='border-radius: 50%;'>
        <div>
            <h2 style='margin: 0;'>Profile</h2>
            <p style='margin: 0; color: gray;'>Manage your details and view credits</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📝 Edit Your Info")
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Name", "John Doe")
        with col2:
            email = st.text_input("📧 Email", "john@example.com")
        address = st.text_area("🏠 Address", "123 Green Avenue, EcoCity")
        submitted = st.form_submit_button("💾 Save Changes")

        if submitted:
            st.success("✅ Profile updated successfully!")

    st.markdown("---")
    st.subheader("🎉 Credits Earned")
    credits = 120
    st.markdown(f"""
    <div style='
        padding: 10px;
        background-color: #e3f2fd; 
        border-left: 4px solid #2196F3;
        border-radius: 5px;
        margin-top: 10px;
    '>
        <h4 style='margin: 0; color: #1565c0;'>{credits} GreenPoints</h4>
        <p style='margin: 0; font-size: 14px; color: #0d47a1;'>You've earned credits by returning recyclable items!</p>
    </div>
    """, unsafe_allow_html=True)

