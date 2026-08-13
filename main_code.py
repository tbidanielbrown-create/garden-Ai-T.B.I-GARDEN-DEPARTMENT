import streamlit as st
import cv2
import numpy as np
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io

# Define valid credentials (3 username slots, only 1 filled)
CREDENTIALS = {
    "Freddie1": "G1FrA",
    "username2": "password2",
    "username3": "password3"
}

# Email configuration
SENDER_EMAIL = "t.b.i.system.true@gmail.com"
SENDER_PASSWORD = "rqbc mziw smvp nlsc"
RECIPIENT_EMAIL = "t.b.i.daniel.brown@gmail.com"

def send_completion_email(username, before_image=None):
    """Send email notification when job is completed"""
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = f"Garden Makeover Job Completed - User: {username}"
        
        body = f"A garden makeover job has been completed by user: {username}"
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def analyze_garden(image):
    """Analyze garden image and identify problem areas"""
    img_array = np.array(image)
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
    
    # Detect brown/dead grass areas (lower saturation, value)
    lower_brown = np.array([10, 20, 20])
    upper_brown = np.array([30, 200, 200])
    mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    # Find contours for problem areas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create output image with circles around problem areas
    output_img = img_array.copy()
    problem_areas = []
    
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small noise
            (x, y), radius = cv2.minEnclosingCircle(contour)
            cv2.circle(output_img, (int(x), int(y)), int(radius), (0, 0, 255), 3)
            problem_areas.append((x, y, radius))
    
    return output_img, problem_areas

def estimate_makeover_price(problem_areas, garden_size_sqft=1000):
    """Estimate garden makeover price based on problem areas"""
    base_price = 500
    area_price_per_sqft = 5
    problem_area_multiplier = len(problem_areas) * 200
    
    total_price = base_price + (garden_size_sqft * area_price_per_sqft) + problem_area_multiplier
    return total_price

def get_tool_recommendations():
    """Provide tool recommendations for garden makeover"""
    recommendations = {
        "Essential Tools": [
            "Garden Spade",
            "Garden Fork",
            "Pruning Shears",
            "Garden Rake",
            "Wheelbarrow"
        ],
        "Soil & Plants": [
            "Quality Topsoil",
            "Compost",
            "Fertilizer",
            "Grass Seeds or Sod"
        ],
        "Equipment": [
            "Lawn Mower",
            "Garden Hose",
            "Sprinkler System",
            "Edging Tools"
        ]
    }
    return recommendations

def check_garden_completion(before_image, after_image):
    """AI evaluation of whether garden makeover is complete"""
    before_array = np.array(before_image)
    after_array = np.array(after_image)
    
    before_hsv = cv2.cvtColor(before_array, cv2.COLOR_RGB2HSV)
    after_hsv = cv2.cvtColor(after_array, cv2.COLOR_RGB2HSV)
    
    # Count problem areas in both images
    lower_brown = np.array([10, 20, 20])
    upper_brown = np.array([30, 200, 200])
    before_mask = cv2.inRange(before_hsv, lower_brown, upper_brown)
    after_mask = cv2.inRange(after_hsv, lower_brown, upper_brown)
    
    before_problems = cv2.countNonZero(before_mask)
    after_problems = cv2.countNonZero(after_mask)
    
    improvement_ratio = 1 - (after_problems / (before_problems + 1))
    
    if improvement_ratio > 0.7:
        return True, improvement_ratio
    else:
        return False, improvement_ratio

def login_page():
    """Handle user login"""
    st.set_page_config(page_title="Garden AI - Mobile Only", layout="centered")
    
    with st.container():
        st.markdown("# 🌱 Garden AI Makeover")
        st.warning("⚠️ WARNING: This application is optimized for MOBILE DEVICES ONLY. Please access via a mobile phone or tablet for the best experience.")
        
        st.subheader("Login")
        username = st.text_input("Username:", placeholder="Enter username")
        password = st.text_input("Password:", type="password", placeholder="Enter password")
        
        if st.button("Sign In"):
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

def main_app():
    """Main application after login"""
    st.set_page_config(page_title="Garden AI - Mobile Only", layout="centered")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🌱 Garden AI Makeover")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    tab1, tab2 = st.tabs(["Analyze Garden", "Complete Job"])
    
    with tab1:
        st.subheader("📸 Upload Garden Photo")
        uploaded_file = st.file_uploader("Take or upload a picture of your garden:", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            garden_image = Image.open(uploaded_file)
            st.image(garden_image, caption="Original Garden", use_container_width=True)
            
            if st.button("Analyze Garden"):
                analyzed_img, problem_areas = analyze_garden(garden_image)
                
                st.image(analyzed_img, caption="Analysis - Red circles show problem areas", use_container_width=True)
                
                st.subheader("📊 Analysis Results")
                st.write(f"**Problem Areas Found:** {len(problem_areas)}")
                
                garden_size = st.slider("Garden size (sq ft):", 100, 5000, 1000)
                estimated_price = estimate_makeover_price(problem_areas, garden_size)
                
                st.metric("Estimated Makeover Price", f"${estimated_price:,.2f}")
                
                st.subheader("🔧 Recommended Tools & Materials")
                recommendations = get_tool_recommendations()
                for category, items in recommendations.items():
                    st.write(f"**{category}:**")
                    for item in items:
                        st.write(f"  • {item}")
                
                st.session_state.before_image = garden_image
                st.session_state.garden_analyzed = True
    
    with tab2:
        st.subheader("✅ Upload Finished Garden Photo")
        
        if "garden_analyzed" not in st.session_state or not st.session_state.garden_analyzed:
            st.info("Please analyze a garden first in the 'Analyze Garden' tab.")
        else:
            finished_file = st.file_uploader("Upload photo of finished garden:", type=["jpg", "jpeg", "png"], key="finished")
            
            if finished_file:
                finished_image = Image.open(finished_file)
                st.image(finished_image, caption="Finished Garden", use_container_width=True)
                
                if st.button("Submit for Approval"):
                    with st.spinner("Evaluating garden completion..."):
                        is_complete, improvement = check_garden_completion(
                            st.session_state.before_image, 
                            finished_image
                        )
                        
                        st.write(f"**Improvement Score:** {improvement*100:.1f}%")
                        
                        if is_complete:
                            st.success("✅ Garden makeover APPROVED!")
                            st.write("Sending completion email...")
                            if send_completion_email(st.session_state.username):
                                st.success(f"Email sent to {RECIPIENT_EMAIL}")
                                st.session_state.garden_analyzed = False
                        else:
                            st.warning("⏳ More work needed. Keep improving!")

# Main execution
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
