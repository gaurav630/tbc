def load_css():
    return """
        <style>
            /* Add your CSS styles here */
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .user-card {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stat-card {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                text-align: center;
            }
            
            .stat-card h3 {
                margin: 0;
                color: #333;
            }
            
            .stat-card p {
                margin: 5px 0 0 0;
                color: #666;
            }
        </style>
    """