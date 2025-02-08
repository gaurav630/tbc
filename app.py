import streamlit as st
from src.auth import login_required, has_permission
from src.models import User
from ui.styles import load_css
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="User Management System",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

def show_login_sidebar():
    """Display sidebar for non-authenticated users"""
    with st.sidebar:
        st.title("Welcome")
        menu_options = {
            "Login": "login",
            "Register": "register"
        }
        
        selected = st.radio("Choose an option", list(menu_options.keys()))
        st.session_state.page = menu_options[selected]

def show_authenticated_sidebar():
    """Display sidebar for authenticated users"""
    with st.sidebar:
        st.title("Navigation")
        user = User.get_by_id(st.session_state.user_id)
        st.write(f"Welcome, {user.username}")
        st.write(f"Role: {user.role}")
        
        menu_options = {
            "Dashboard": "dashboard",
            "Profile": "profile",
        }
        
        # Add admin options if user has permissions
        if user.has_permission("VIEW_USERS"):
            menu_options["Users"] = "users"
        if user.has_permission("VIEW_LOGS"):
            menu_options["Audit Log"] = "audit"
            
        menu_options["Settings"] = "settings"
        
        selected = st.radio("Menu", list(menu_options.keys()))
        st.session_state.page = menu_options[selected]
        
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def show_login_page():
    """Display the login page"""
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                success, user_id = User.authenticate(username, password)
                if success:
                    st.session_state.user_id = user_id
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                st.error("An error occurred during login")

def show_register_page():
    """Display the registration page"""
    st.title("Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            try:
                success, message = User.create(username, email, password, "User")
                if success:
                    st.success("Registration successful! Please login.")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                st.error("An error occurred during registration")

@login_required
def show_dashboard():
    """Display the dashboard"""
    st.title("Dashboard")
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
                <div class="stat-card">
                    <h3>Active Users</h3>
                    <p>150</p>
                    <small>+10% from last week</small>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
                <div class="stat-card">
                    <h3>New Users</h3>
                    <p>15</p>
                    <small>Today</small>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
                <div class="stat-card">
                    <h3>Total Sessions</h3>
                    <p>1,234</p>
                    <small>This week</small>
                </div>
            """, unsafe_allow_html=True)
    
    # Recent Activity
    st.subheader("Recent Activity")
    activity_data = [
        {"time": "2 minutes ago", "action": "New user registration"},
        {"time": "5 minutes ago", "action": "Password reset request"},
        {"time": "10 minutes ago", "action": "User role updated"}
    ]
    
    for activity in activity_data:
        st.markdown(f"""
            <div class="user-card">
                <strong>{activity['action']}</strong><br>
                <small>{activity['time']}</small>
            </div>
        """, unsafe_allow_html=True)

@login_required
def show_profile_page():
    """Display the user profile page"""
    st.title("My Profile")
    user = User.get_by_id(st.session_state.user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="user-card">
                <h3>Profile Information</h3>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Role:</strong> {user.role}</p>
                <p><strong>Member Since:</strong> {user.created_at.strftime('%B %d, %Y')}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with st.form("update_profile"):
            st.subheader("Update Profile")
            new_email = st.text_input("New Email", value=user.email)
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Profile"):
                try:
                    if new_password:
                        if new_password != confirm_password:
                            st.error("New passwords do not match")
                            return
                        if not user.verify_password(current_password):
                            st.error("Current password is incorrect")
                            return
                        user.update_password(new_password)
                    
                    if new_email != user.email:
                        user.update_email(new_email)
                    
                    st.success("Profile updated successfully")
                except Exception as e:
                    logger.error(f"Profile update error: {str(e)}")
                    st.error("An error occurred while updating your profile")

@login_required
@has_permission("VIEW_USERS")
def show_users_page():
    """Display the users management page"""
    st.title("User Management")
    
    # Add new user section
    if st.session_state.get('show_add_user', False):
        with st.form("add_user_form"):
            st.subheader("Add New User")
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["User", "Manager", "Admin"])
            
            if st.form_submit_button("Add User"):
                try:
                    success, message = User.create(new_username, new_email, new_password, new_role)
                    if success:
                        st.success(message)
                        st.session_state.show_add_user = False
                        st.rerun()
                    else:
                        st.error(message)
                except Exception as e:
                    logger.error(f"Add user error: {str(e)}")
                    st.error("An error occurred while adding the user")
    
    # Toggle add user form
    if st.button("Add New User" if not st.session_state.get('show_add_user', False) else "Cancel"):
        st.session_state.show_add_user = not st.session_state.get('show_add_user', False)
        st.rerun()
    
    # Users list
    st.subheader("Users List")
    users = User.get_all()
    
    for user in users:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"""
                    <div class="user-card">
                        <h4>{user.username}</h4>
                        <p>{user.email}</p>
                        <small>Role: {user.role}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write(f"Last Login: {user.last_login or 'Never'}")
                st.write(f"Status: {'Active' if user.is_active else 'Inactive'}")
            
            with col3:
                if st.button("Edit", key=f"edit_{user.id}"):
                    st.session_state.editing_user = user.id
                    st.rerun()

def main():
    """Main application entry point"""
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

    # Sidebar navigation
    if 'user_id' in st.session_state:
        show_authenticated_sidebar()
    else:
        show_login_sidebar()

    # Page routing
    if st.session_state.page == 'login':
        show_login_page()
    elif st.session_state.page == 'register':
        show_register_page()
    elif st.session_state.page == 'dashboard':
        show_dashboard()
    elif st.session_state.page == 'users':
        show_users_page()
    elif st.session_state.page == 'profile':
        show_profile_page()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")