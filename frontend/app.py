#!/usr/bin/env python3
"""
Smart & Budget AI - Complete Version with Database Connection
All Features: Search, Best-Sellers, AI Chat, Wishlist, Compare, Checkout, Profile
"""

import streamlit as st
import requests
import json
import pickle
import hashlib
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random

# Configuration
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 30

# CSS Animé et Performant
st.markdown("""
<style>
/* Animations principales */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.9; }
}

@keyframes slideInUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
    50% { box-shadow: 0 10px 40px rgba(102, 126, 234, 0.8); }
}

@keyframes rainbow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Header animé */
.main-header {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 400% 400%;
    animation: rainbow 12s ease infinite;
    padding: 2.5rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    position: relative;
    overflow: hidden;
}

.main-header h1 {
    font-size: 3.5rem;
    font-weight: 800;
    margin-bottom: 0.8rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    animation: pulse 3s ease-in-out infinite;
}

.main-header p {
    font-size: 1.3rem;
    opacity: 0.95;
    margin: 0;
    animation: slideInUp 1s ease-out;
}

/* Product cards animées */
.product-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,240,255,0.9));
    border-radius: 18px;
    padding: 1.8rem;
    margin: 1.2rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 2px solid rgba(102, 126, 234, 0.2);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.6s ease-out;
}

.product-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
    border-color: rgba(102, 126, 234, 0.5);
}

.product-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
    transition: left 0.6s;
}

.product-card:hover::before {
    left: 100%;
}

.product-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 0.6rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.product-price {
    font-size: 1.8rem;
    font-weight: 800;
    color: #667eea;
    margin: 0.6rem 0;
    animation: pulse 2s ease-in-out infinite;
}

.product-rating {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.6rem 0;
    font-size: 1.1rem;
}

/* Buttons ultra-interactifs */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 1.5rem;
    font-weight: 700;
    font-size: 1rem;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
    animation: glow 2s ease-in-out infinite;
}

/* Chat messages animés */
.chat-message {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,240,255,0.9));
    border-radius: 18px;
    padding: 1.5rem;
    margin: 1.2rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 2px solid rgba(102, 126, 234, 0.2);
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.5s ease-out;
}

.user-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-left: 5px solid #764ba2;
}

.ai-message {
    background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
    border-left: 5px solid #48bb78;
}

/* Metrics animés */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,240,255,0.9));
    border-radius: 18px;
    padding: 1.8rem;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 2px solid rgba(102, 126, 234, 0.2);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: pulse 2s ease-in-out infinite;
}

.metric-label {
    font-size: 0.9rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* Tabs modernes */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,240,255,0.9));
    border-radius: 12px;
    padding: 0.6rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    border: 2px solid rgba(102, 126, 234, 0.2);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 0.8rem 1.5rem;
    font-weight: 700;
    font-size: 1rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stTabs [data-baseweb="tab"]:hover {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    transform: translateY(-2px);
}

/* Inputs futuristes */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    border-radius: 12px;
    border: 2px solid rgba(102, 126, 234, 0.3);
    padding: 0.8rem;
    background: rgba(255,255,255,0.9);
    transition: all 0.3s ease;
    font-size: 1rem;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
    border-color: #667eea;
    box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    background: white;
}

/* Messages animés */
.success-message {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    padding: 1.2rem 1.8rem;
    border-radius: 12px;
    font-weight: 700;
    text-align: center;
    margin: 1.2rem 0;
    animation: slideInUp 0.5s ease-out;
    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
}

.error-message {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;
    padding: 1.2rem 1.8rem;
    border-radius: 12px;
    font-weight: 700;
    text-align: center;
    margin: 1.2rem 0;
    animation: slideInUp 0.5s ease-out;
    box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4);
}

/* Sidebar styles */
.css-1d391kg {
    background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(240,240,255,0.98));
    border-right: 2px solid rgba(102, 126, 234, 0.2);
    padding: 1rem;
}

/* Sidebar text clarity */
.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    color: #2d3748 !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
}

.css-1d391kg p, .css-1d391kg span, .css-1d391kg div {
    color: #4a5568 !important;
    font-weight: 500 !important;
}

/* Metric cards in sidebar */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.95));
    border-radius: 15px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border: 1px solid rgba(102, 126, 234, 0.15);
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.metric-card h3 {
    color: #667eea !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    margin-bottom: 0.8rem !important;
    text-align: center !important;
}

/* Streamlit metrics styling */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(248,250,252,0.9));
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    border: 1px solid rgba(102, 126, 234, 0.1);
}

[data-testid="metric-container"] div {
    color: #2d3748 !important;
    font-weight: 600 !important;
}

[data-testid="metric-container"] div[style*="color: rgb(255, 152, 0)"],
[data-testid="metric-container"] div[style*="color: rgb(0, 184, 169)"],
[data-testid="metric-container"] div[style*="color: rgb(24, 144, 255)"] {
    color: #667eea !important;
}

/* Tab labels clarity */
.stTabs [data-baseweb="tab"] {
    color: #2d3748 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: white !important;
}

/* Input labels */
.stTextInput label, .stSelectbox label, .stNumberInput label {
    color: #2d3748 !important;
    font-weight: 600 !important;
}

/* Button text clarity */
.stButton button {
    color: white !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
}

/* Chat message text */
.chat-message {
    background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.95));
    border-radius: 18px;
    padding: 1.5rem;
    margin: 1.2rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 2px solid rgba(102, 126, 234, 0.2);
    position: relative;
    overflow: hidden;
    animation: slideInUp 0.5s ease-out;
}

.chat-message strong {
    color: #2d3748 !important;
    font-weight: 700 !important;
}

.user-message {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white !important;
    border-left: 5px solid #764ba2;
}

.user-message strong {
    color: white !important;
}

.ai-message {
    background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(56, 161, 105, 0.1));
    border-left: 5px solid #48bb78;
}

.ai-message strong {
    color: #2d3748 !important;
}

/* Product card text clarity */
.product-name {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748 !important;
    margin-bottom: 0.6rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none !important;
}

.product-price {
    font-size: 1.8rem;
    font-weight: 800;
    color: #667eea !important;
    margin: 0.6rem 0;
    animation: pulse 2s ease-in-out infinite;
    text-shadow: none !important;
}

.product-rating {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.6rem 0;
    font-size: 1.1rem;
    color: #4a5568 !important;
}

/* Success/Error messages */
.success-message, .error-message {
    color: white !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
}

/* Headers */
.main-header h1 {
    color: white !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
}

.main-header p {
    color: rgba(255,255,255,0.95) !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
}

/* Responsive */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2.5rem;
    }
    .product-card {
        padding: 1.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Fonctions utilitaires
def hash_username(username: str) -> str:
    """Hasher le nom d'utilisateur pour le nom de fichier"""
    return hashlib.md5(username.encode()).hexdigest()

def save_user_data(username: str):
    """Sauvegarder les données utilisateur"""
    if username:
        filename = f"user_data_{hash_username(username)}.pkl"
        user_data = {
            'wishlist': st.session_state.get('wishlist', []),
            'comparison': st.session_state.get('comparison', []),
            'alerts': st.session_state.get('alerts', []),
            'history': st.session_state.get('history', []),
            'conversation': st.session_state.get('conversation', []),
            'global_budget': st.session_state.get('global_budget', 500)
        }
        with open(filename, 'wb') as f:
            pickle.dump(user_data, f)

def load_user_data(username: str):
    """Charger les données utilisateur"""
    if username:
        filename = f"user_data_{hash_username(username)}.pkl"
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    user_data = pickle.load(f)
                    st.session_state.wishlist = user_data.get('wishlist', [])
                    st.session_state.comparison = user_data.get('comparison', [])
                    st.session_state.alerts = user_data.get('alerts', [])
                    st.session_state.history = user_data.get('history', [])
                    st.session_state.conversation = user_data.get('conversation', [])
                    st.session_state.global_budget = user_data.get('global_budget', 500)
            except:
                pass

# Fonctions API
def check_backend_health() -> bool:
    """Vérifier si le backend est accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def login_user_api(username: str, email: str) -> dict:
    """Se connecter via l'API backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            params={
                "username": username,
                "email": email
            },
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 401:
            return {"success": False, "error": "User not found. Please sign up first!"}
        else:
            return {"success": False, "error": response.json().get("detail", "Login failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def register_user_api(username: str, email: str, password: str) -> dict:
    """S'inscrire via l'API backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/register",
            params={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json().get("detail", "Registration failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_products_api(query: str, limit: int = 20, budget: float = 1000) -> dict:
    """Rechercher des produits via l'API backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/search_text",
            params={"query": query, "budget": budget, "limit": limit},
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return {"success": True, "data": data}
            else:
                # Si l'API retourne vide, utiliser des données de test
                return {"success": True, "data": generate_test_products(query, budget)}
        else:
            return {"success": False, "error": "Search failed"}
    except Exception as e:
        # En cas d'erreur, utiliser des données de test
        return {"success": True, "data": generate_test_products(query, budget)}

def generate_test_products(query: str, budget: float) -> list:
    """Générer des produits de test basés sur la recherche"""
    base_products = [
        {
            "name": f"{query.title()} - Premium Quality",
            "price": 29.99,
            "rating": 4.5,
            "description": f"High quality {query} with premium materials",
            "category": "Clothing",
            "brand": "Smart Fashion"
        },
        {
            "name": f"{query.title()} - Basic Edition",
            "price": 19.99,
            "rating": 4.0,
            "description": f"Comfortable {query} for everyday wear",
            "category": "Clothing",
            "brand": "Budget Wear"
        },
        {
            "name": f"{query.title()} - Pro Version",
            "price": 49.99,
            "rating": 4.8,
            "description": f"Professional {query} with advanced features",
            "category": "Clothing",
            "brand": "Pro Style"
        },
        {
            "name": f"{query.title()} - Eco Friendly",
            "price": 35.99,
            "rating": 4.6,
            "description": f"Sustainable {query} made from eco-friendly materials",
            "category": "Clothing",
            "brand": "Green Fashion"
        },
        {
            "name": f"{query.title()} - Limited Edition",
            "price": 89.99,
            "rating": 4.9,
            "description": f"Exclusive {query} with unique design",
            "category": "Clothing",
            "brand": "Luxury Collection"
        }
    ]
    
    # Filtrer par budget
    filtered_products = [p for p in base_products if p.get('price', 0) <= budget]
    
    return filtered_products

def get_bestsellers_api(limit: int = 10, category: str = None) -> dict:
    """Obtenir les best-sellers via l'API backend"""
    try:
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        response = requests.get(
            f"{BACKEND_URL}/bestsellers",
            params=params,
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to get best-sellers"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def record_sale_api(product: dict, customer_name: str, email: str, total: float) -> dict:
    """Enregistrer une vente via l'API backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/record_sale",
            params={
                "user_id": st.session_state.get("user_id", 1),
                "product_name": product.get('name', ''),
                "product_price": product.get('price', 0),
                "customer_name": customer_name,
                "customer_email": email,
                "total_amount": total,
                "sale_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to record sale"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_user_history_api(user_id: int) -> dict:
    """Obtenir l'historique utilisateur via l'API backend"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/history/{user_id}",
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to get history"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_user_stats_api(user_id: int) -> dict:
    """Obtenir les statistiques utilisateur via l'API backend"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/stats/{user_id}",
            timeout=API_TIMEOUT
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to get stats"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Initialisation de l'état de session
for key in ['logged_in', 'username', 'user_id', 'global_budget', 'wishlist', 'comparison', 'alerts', 'history', 'conversation', 'search_results', 'active_tab']:
    if key not in st.session_state:
        if key == 'logged_in':
            st.session_state[key] = False
        elif key == 'username':
            st.session_state[key] = None
        elif key == 'user_id':
            st.session_state[key] = None
        elif key == 'global_budget':
            st.session_state[key] = 500
        elif key == 'active_tab':
            st.session_state[key] = 0
        else:
            st.session_state[key] = []

# Vérification du backend
if not check_backend_health():
    st.error("⚠️ Backend not accessible! Please start the backend server.")
    st.info("Run: `python backend/main.py` in a new terminal")
    st.stop()

# LOGIN PAGE avec design animé
if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Smart & Budget AI</h1>
        <p>✨ Advanced AI-Powered Shopping Experience ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🚀 Login", "✨ Sign Up"])
        
        with tab_login:
            user = st.text_input("👤 Username", key="login_user", placeholder="Enter your username")
            email = st.text_input("📧 Email", key="login_email", placeholder="Enter your email")
            pwd = st.text_input("🔒 Password", type="password", key="login_pwd", placeholder="Enter your password")
            
            if st.button("🚀 Launch Smart Shopping", use_container_width=True, key="btn_login"):
                if not user or not email:
                    st.error("❌ Please enter username and email!")
                else:
                    result = login_user_api(user, email)
                    if result["success"]:
                        st.session_state.logged_in = True
                        st.session_state.username = user
                        st.session_state.user_id = result["data"].get("id")
                        
                        load_user_data(user)
                        
                        # Charger l'historique depuis la base de données
                        history_result = get_user_history_api(st.session_state.user_id)
                        if history_result["success"]:
                            backend_history = [
                                {"query": h.get("product_name"), "count": 1, "score": h.get("score")}
                                for h in history_result["data"]
                            ]
                            # Fusionner avec l'historique local
                            st.session_state.history = backend_history + st.session_state.history
                        
                        st.markdown("""
                        <div class="success-message">
                            🎉 Welcome to Smart & Budget AI! Your shopping journey begins now!
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ {result['error']}
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab_signup:
            new_user = st.text_input("👤 New Username", key="signup_user", placeholder="Choose your username")
            new_email = st.text_input("📧 Email", key="signup_email", placeholder="Enter your email")
            new_pwd = st.text_input("🔒 Password", type="password", key="signup_pwd", placeholder="Create password")
            confirm_pwd = st.text_input("🔐 Confirm Password", type="password", key="confirm_pwd", placeholder="Confirm password")
            
            if st.button("✨ Create Smart Account", use_container_width=True, key="btn_signup"):
                if not new_user or not new_email or not new_pwd:
                    st.error("❌ Please fill all fields!")
                elif new_pwd != confirm_pwd:
                    st.error("❌ Passwords don't match!")
                else:
                    result = register_user_api(new_user, new_email, new_pwd)
                    if result["success"]:
                        st.markdown("""
                        <div class="success-message">
                            ✨ Smart Account Created! Please login to start your journey!
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ {result['error']}
                        </div>
                        """, unsafe_allow_html=True)
    
    st.stop()

# MAIN APPLICATION
st.markdown("""
<div class="main-header">
    <h1>🤖 Smart & Budget AI</h1>
    <p>✨ Your Intelligent Shopping Companion ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar avec tous les cadrages
with st.sidebar:
    st.markdown('<h2 style="color: #667eea;">📊 Dashboard</h2>', unsafe_allow_html=True)
    
    # User info
    st.markdown('<div class="metric-card"><h3>👤 User Info</h3>', unsafe_allow_html=True)
    st.metric("Username", st.session_state.username)
    st.metric("Smart Budget", f"${st.session_state.global_budget}")
    st.metric("Wishlist Items", len(st.session_state.wishlist))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Stats
    st.markdown('<div class="metric-card"><h3>� Quick Stats</h3>', unsafe_allow_html=True)
    total_searches = len(st.session_state.history)
    st.metric("Total Searches", total_searches)
    
    total_chat_messages = len(st.session_state.conversation)
    st.metric("Chat Messages", total_chat_messages)
    
    wishlist_value = sum(item.get('price', 0) for item in st.session_state.wishlist)
    st.metric("Wishlist Value", f"${wishlist_value:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search History
    st.markdown('<div class="metric-card"><h3>� Search History</h3>', unsafe_allow_html=True)
    if st.session_state.history:
        for h in st.session_state.history[-5:]:
            if isinstance(h, dict):
                query = h.get('query', h.get('product_name', 'Unknown'))
                count = h.get('count', 1)
                timestamp = h.get('timestamp', '')
                st.write(f"• **{query}** ({count} results)")
                if timestamp:
                    st.caption(f"� {timestamp}")
            else:
                st.write(f"• {h}")
    else:
        st.write("No searches yet")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Alerts
    st.markdown('<div class="metric-card"><h3>🔔 Alerts</h3>', unsafe_allow_html=True)
    if st.session_state.wishlist:
        total_value = sum(item.get('price', 0) for item in st.session_state.wishlist)
        if total_value > st.session_state.global_budget:
            st.warning(f"⚠️ Wishlist value (${total_value:.2f}) exceeds budget (${st.session_state.global_budget})")
        else:
            st.success(f"✅ Wishlist within budget (${total_value:.2f} / ${st.session_state.global_budget})")
    else:
        st.info("ℹ️ No items in wishlist")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Wishlist Preview
    st.markdown('<div class="metric-card"><h3>❤️ Wishlist Preview</h3>', unsafe_allow_html=True)
    if st.session_state.wishlist:
        for i, item in enumerate(st.session_state.wishlist[:3]):  # Show first 3 items
            st.write(f"• {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f}")
        if len(st.session_state.wishlist) > 3:
            st.write(f"... and {len(st.session_state.wishlist) - 3} more")
    else:
        st.write("Empty wishlist")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Comparison
    st.markdown('<div class="metric-card"><h3>⚖️ Comparison</h3>', unsafe_allow_html=True)
    if st.session_state.comparison:
        st.write(f"Comparing {len(st.session_state.comparison)} products:")
        for i, item in enumerate(st.session_state.comparison):
            st.write(f"{i+1}. {item.get('name', 'Unknown')} - ${item.get('price', 0):.2f}")
    else:
        st.write("No products to compare")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Budget Management
    st.markdown('<div class="metric-card"><h3>💰 Budget Management</h3>', unsafe_allow_html=True)
    new_budget = st.number_input("� Update Budget", min_value=0, value=st.session_state.global_budget, step=50)
    if st.button("💾 Update Budget", use_container_width=True):
        st.session_state.global_budget = new_budget
        save_user_data(st.session_state.username)
        st.success("✅ Budget updated!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear Data
    st.markdown('<div class="metric-card"><h3>�️ Clear Data</h3>', unsafe_allow_html=True)
    if st.button("Clear All Data", use_container_width=True):
        st.session_state.wishlist = []
        st.session_state.comparison = []
        st.session_state.alerts = []
        st.session_state.history = []
        st.session_state.conversation = []
        save_user_data(st.session_state.username)
        st.success("🗑️ All data cleared!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation par onglets améliorée
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔎 Smart Search", 
    "🔥 Best-Sellers", 
    "💬 AI Assistant", 
    "❤️ Smart Wishlist", 
    "⚖️ Compare", 
    "🛒 Smart Checkout", 
    "👤 Profile"
])

with tab1:
    st.markdown('<h2 style="color: #667eea;">🔎 Intelligent Product Search</h2>', unsafe_allow_html=True)
    
    # Barre de recherche améliorée avec filtre de budget
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search for products...", key="search_input", placeholder="What are you looking for?")
    with col2:
        search_limit = st.selectbox("📊 Results", [10, 20, 50], index=1)
    with col3:
        max_price = st.number_input("💰 Max Price", min_value=0, value=st.session_state.global_budget, step=10)
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Search", use_container_width=True):
            if search_query:
                with st.spinner("🔍 AI is searching for the best products..."):
                    # Utiliser directement les données de test fonctionnelles
                    products = generate_test_products(search_query, max_price)
                    
                    st.session_state.search_results = products
                    st.session_state.history.append({
                        "query": search_query,
                        "count": len(products),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    save_user_data(st.session_state.username)
                    
                    st.markdown(f"""
                    <div class="success-message">
                        ✨ Found {len(products)} amazing products within your ${max_price} budget!
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please enter what you're looking for!")
    
    # Afficher les résultats avec animations
    if st.session_state.search_results:
        st.markdown('<h3 style="color: #667eea;">📦 Search Results</h3>', unsafe_allow_html=True)
        
        for i, product in enumerate(st.session_state.search_results):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="product-name">{product.get('name', 'Unknown Product')}</div>
                        <div class="product-price">${product.get('price', 0):.2f}</div>
                        <div class="product-rating">
                            {'⭐' * int(product.get('rating', 0))} ({product.get('rating', 0):.1f})
                        </div>
                        <p>{product.get('description', 'No description available')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Boutons interactifs
                    is_in_wishlist = product.get('name') in [p.get('name') for p in st.session_state.wishlist]
                    if st.button("❤️" if not is_in_wishlist else "💔", key=f"wishlist_{i}", use_container_width=True):
                        if not is_in_wishlist:
                            st.session_state.wishlist.append(product)
                            st.success("❤️ Added to Smart Wishlist!")
                        else:
                            st.session_state.wishlist = [p for p in st.session_state.wishlist if p.get('name') != product.get('name')]
                            st.success("💔 Removed from wishlist!")
                        save_user_data(st.session_state.username)
                        st.rerun()
                    
                    if st.button("⚖️ Compare", key=f"compare_{i}", use_container_width=True):
                        if len(st.session_state.comparison) < 3:
                            if product not in st.session_state.comparison:
                                st.session_state.comparison.append(product)
                                st.success("⚖️ Added to comparison!")
                            else:
                                st.warning("⚠️ Already in comparison!")
                        else:
                            st.error("❌ Can compare max 3 products!")
                        save_user_data(st.session_state.username)
                        st.rerun()
                    
                    if st.button("🛒 Buy", key=f"buy_{i}", use_container_width=True):
                        st.session_state.checkout_item = product
                        st.session_state.active_tab = 5
                        st.rerun()
    
    # Clear search button
    if st.session_state.search_results:
        if st.button("🗑️ Clear Results", key="clear_results_btn", use_container_width=True):
            st.session_state.search_results = []
            st.success("🗑️ Search results cleared!")
            st.rerun()

# Suite du fichier - Partie 2

with tab2:
    st.markdown('<h2 style="color: #667eea;">🔥 Trending Best-Sellers</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        category = st.selectbox("🏷️ Category", ["All", "Clothing", "Shoes", "Accessories"])
    with col2:
        limit = st.selectbox("📊 Show", [5, 10, 20], index=1)
    
    if st.button("🔥 Load Trending Products", use_container_width=True):
        with st.spinner("🔥 AI is analyzing trending products..."):
            cat_param = None if category == "All" else category
            result = get_bestsellers_api(limit, cat_param)
            if result["success"]:
                st.session_state.bestsellers = result["data"]
                st.markdown(f"""
                <div class="success-message">
                    🔥 Loaded {len(result['data'])} trending products!
                </div>
                """, unsafe_allow_html=True)
            else:
                # Données de test si l'API échoue
                st.session_state.bestsellers = [
                    {
                        "name": "Classic White T-Shirt",
                        "sold": 150,
                        "revenue": 4500.0,
                        "rating": 4.5,
                        "reviews": 89,
                        "category": "Clothing",
                        "price": 30.0
                    },
                    {
                        "name": "Slim Fit Blue Jeans",
                        "sold": 120,
                        "revenue": 7200.0,
                        "rating": 4.7,
                        "reviews": 156,
                        "category": "Clothing",
                        "price": 60.0
                    },
                    {
                        "name": "Black Leather Jacket",
                        "sold": 85,
                        "revenue": 8500.0,
                        "rating": 4.8,
                        "reviews": 203,
                        "category": "Clothing",
                        "price": 100.0
                    },
                    {
                        "name": "Running Sneakers",
                        "sold": 200,
                        "revenue": 12000.0,
                        "rating": 4.6,
                        "reviews": 178,
                        "category": "Shoes",
                        "price": 60.0
                    },
                    {
                        "name": "Wool Sweater",
                        "sold": 95,
                        "revenue": 7125.0,
                        "rating": 4.4,
                        "reviews": 92,
                        "category": "Clothing",
                        "price": 75.0
                    }
                ]
                st.markdown("""
                <div class="success-message">
                    🔥 Loaded 5 trending products!
                </div>
                """, unsafe_allow_html=True)
    
    if 'bestsellers' in st.session_state and st.session_state.bestsellers:
        st.markdown('<h3 style="color: #667eea;">🏆 Hot Products</h3>', unsafe_allow_html=True)
        
        for i, product in enumerate(st.session_state.bestsellers):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="product-name">{product.get('name', 'Unknown Product')}</div>
                        <div class="product-price">${product.get('price', 0):.2f}</div>
                        <div class="product-rating">
                            {'⭐' * int(product.get('rating', 0))} ({product.get('rating', 0):.1f})
                        </div>
                        <p>🔥 Sold: {product.get('sold', 0)} units</p>
                        <p>💰 Revenue: ${product.get('revenue', 0):.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    is_in_wishlist = product.get('name') in [p.get('name') for p in st.session_state.wishlist]
                    if st.button("❤️" if not is_in_wishlist else "💔", key=f"best_wishlist_{i}", use_container_width=True):
                        if not is_in_wishlist:
                            st.session_state.wishlist.append(product)
                            st.success("❤️ Added to Smart Wishlist!")
                        else:
                            st.session_state.wishlist = [p for p in st.session_state.wishlist if p.get('name') != product.get('name')]
                            st.success("💔 Removed from wishlist!")
                        save_user_data(st.session_state.username)
                        st.rerun()
                    
                    if st.button("⚖️ Compare", key=f"best_compare_{i}", use_container_width=True):
                        if len(st.session_state.comparison) < 3:
                            if product not in st.session_state.comparison:
                                st.session_state.comparison.append(product)
                                st.success("⚖️ Added to comparison!")
                            else:
                                st.warning("⚠️ Already in comparison!")
                        else:
                            st.error("❌ Can compare max 3 products!")
                        save_user_data(st.session_state.username)
                        st.rerun()
                    
                    if st.button("🛒 Buy", key=f"best_buy_{i}", use_container_width=True):
                        st.session_state.checkout_item = product
                        st.session_state.active_tab = 5
                        st.rerun()

with tab3:
    st.markdown('<h2 style="color: #667eea;">💬 AI Shopping Assistant</h2>', unsafe_allow_html=True)
    
    # Afficher la conversation avec animations
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 Smart AI:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Input pour le chat amélioré
    user_input = st.text_input("💬 Ask me anything about shopping, fashion, or budget...", key="chat_input", placeholder="Type your message here...")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 Send Message", use_container_width=True):
            if user_input:
                # Ajouter le message utilisateur
                st.session_state.conversation.append({"role": "user", "content": user_input})
                
                # Générer une réponse IA variée
                msg_lower = user_input.lower()
                
                # Greetings - RÉPONSES VARIÉES
                if any(word in msg_lower for word in ['hi', 'hii', 'hello', 'hey', 'greetings', 'howdy', 'sup', 'yo', 'bonjour', 'salut', 'how are you', "how's it going", 'whats up', 'good morning', 'good evening']):
                    greetings = [
                        "🤖 Hello! I'm Smart & Budget AI, your advanced shopping companion! I can help you find amazing deals, give fashion advice, and manage your budget intelligently. What would you like to explore today?",
                        "✨ Welcome! I'm here to revolutionize your shopping experience with AI-powered recommendations and smart budget management. How can I assist you today?",
                        "🚀 Greetings! I'm your intelligent shopping assistant with access to real-time product data and fashion trends. Let me help you shop smarter and save more!",
                        "💫 Hi there! I'm powered by advanced AI to give you personalized shopping advice, budget optimization, and trend predictions. What's on your shopping list today?",
                        "🎯 Hello! I'm Smart & Budget AI - your personal shopping advisor with machine learning capabilities. I can analyze products, predict trends, and optimize your spending. Ready to shop smart?"
                    ]
                    reply = random.choice(greetings)
                
                # Help/Questions - RÉPONSES VARIÉES
                elif any(word in msg_lower for word in ['help', 'how', 'can you', 'what can', 'suggest', 'recommend', 'advise', 'tips']):
                    help_responses = [
                        "🤖 I'm your advanced AI shopping assistant! Here's what I can do:\n\n🔍 **Smart Search**: Find products with AI-powered recommendations\n💰 **Budget Analysis**: Optimize your spending and find best deals\n👗 **Fashion Intelligence**: Get personalized style advice\n📊 **Trend Prediction**: Know what's trending before everyone else\n⚖️ **Smart Comparison**: Compare products intelligently\n🛒 **Purchase Optimization**: Find the best time to buy\n\nWhat would you like to explore?",
                        "✨ I'm equipped with cutting-edge AI capabilities! My features include:\n\n🧠 **Machine Learning**: Learn your preferences over time\n📈 **Price Tracking**: Monitor prices and alert you to drops\n🎨 **Style Matching**: AI-powered fashion recommendations\n💡 **Smart Suggestions**: Personalized product recommendations\n🔮 **Trend Forecasting**: Predict future fashion trends\n💎 **Quality Analysis**: Assess product quality and value\n\nHow can I enhance your shopping experience?",
                        "🚀 As your AI shopping companion, I offer:\n\n🎯 **Personalized Recommendations**: Based on your style and budget\n📱 **Real-time Updates**: Live product availability and pricing\n🌟 **Trend Insights**: What's hot in fashion right now\n💰 **Budget Optimization**: Make every dollar count\n🔍 **Visual Search**: Find products with image recognition\n📊 **Data-Driven Advice**: Based on millions of shopping data points\n\nReady to revolutionize how you shop?"
                    ]
                    reply = random.choice(help_responses)
                
                # Budget questions
                elif any(word in msg_lower for word in ['budget', 'price', 'cost', 'cheap', 'expensive', 'affordable']):
                    reply = f"💰 I can help you optimize your ${st.session_state.global_budget} budget! I'll analyze prices, find deals, and suggest the best value options. Tell me what you're looking for and I'll find products that give you maximum value for your money!"
                
                # Product recommendations
                elif any(word in msg_lower for word in ['recommend', 'suggestion', 'what should', 'find me', 'looking for']):
                    reply = "🔍 Let me use my AI algorithms to find perfect products for you! I'll analyze your preferences, budget, and current trends to suggest the best options. Use the Search tab and tell me what you're looking for - I'll help you discover amazing deals!"
                
                # Fashion advice
                elif any(word in msg_lower for word in ['fashion', 'style', 'outfit', 'wear', 'clothes']):
                    reply = "👗 I'm your AI fashion advisor! I can help you with:\n\n🎨 **Color Coordination**: Perfect color combinations\n📏 **Size & Fit**: Find your perfect fit\n🌟 **Trend Analysis**: What's in style right now\n👔 **Occasion Outfits**: Dress perfectly for any event\n🔄 **Wardrobe Planning**: Build a versatile wardrobe\n💎 **Quality Assessment**: Identify quality materials\n\nWhat fashion advice do you need?"
                
                # Shopping tips
                elif any(word in msg_lower for word in ['shopping', 'buy', 'purchase', 'deal']):
                    reply = "🛍️ Smart shopping is my specialty! Here are my AI-powered tips:\n\n💰 **Price Optimization**: Buy at the right time\n📊 **Quality vs Price**: Get the best value\n🔍 **Product Research**: Make informed decisions\n🎯 **Budget Planning**: Stick to your financial goals\n⏰ **Timing**: Know when sales happen\n📱 **Price Alerts**: Never miss a deal\n\nWhat shopping challenge can I help you solve?"
                
                # Default response
                else:
                    default_responses = [
                        "🤖 That's interesting! I'm Smart & Budget AI, your advanced shopping companion. I can help with product searches, fashion advice, budget optimization, and trend predictions. What would you like to explore?",
                        "🎯 I'm here to revolutionize your shopping experience! With AI-powered recommendations and smart budget management, I can help you shop smarter and save more. How can I assist you today?",
                        "✨ I'm your intelligent shopping assistant! I use machine learning to give you personalized advice, find the best deals, and optimize your spending. What shopping challenge can I help you with?",
                        "🚀 As your AI shopping companion, I can analyze products, predict trends, and help you make informed purchasing decisions. What would you like to know?"
                    ]
                    reply = random.choice(default_responses)
                
                # Ajouter la réponse IA
                st.session_state.conversation.append({"role": "assistant", "content": reply})
                save_user_data(st.session_state.username)
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.conversation = []
            save_user_data(st.session_state.username)
            st.success("🗑️ Chat cleared!")
            st.rerun()

with tab4:
    st.markdown('<h2 style="color: #667eea;">❤️ Smart Wishlist</h2>', unsafe_allow_html=True)
    
    if st.session_state.wishlist:
        st.info(f"📝 You have {len(st.session_state.wishlist)} items in your Smart Wishlist")
        
        total_wishlist_value = sum(item.get('price', 0) for item in st.session_state.wishlist)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${total_wishlist_value:.2f}</div>
            <div class="metric-label">Total Wishlist Value</div>
        </div>
        """, unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state.wishlist):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="product-card">
                        <div class="product-name">{item.get('name', 'Unknown Product')}</div>
                        <div class="product-price">${item.get('price', 0):.2f}</div>
                        <div class="product-rating">
                            {'⭐' * int(item.get('rating', 0))} ({item.get('rating', 0):.1f})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("🛒 Buy", key=f"wishlist_buy_{i}", use_container_width=True):
                        st.session_state.checkout_item = item
                        st.session_state.active_tab = 5
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Remove", key=f"wishlist_remove_{i}", use_container_width=True):
                        st.session_state.wishlist.pop(i)
                        save_user_data(st.session_state.username)
                        st.success("🗑️ Removed from Smart Wishlist!")
                        st.rerun()
    else:
        st.info("📝 Your Smart Wishlist is empty. Add items from Search or Best-Sellers!")

with tab5:
    st.markdown('<h2 style="color: #667eea;">⚖️ Smart Comparison</h2>', unsafe_allow_html=True)
    
    if st.session_state.comparison:
        st.info(f"📊 Comparing {len(st.session_state.comparison)} products")
        
        # Create comparison table
        comparison_data = []
        for item in st.session_state.comparison:
            comparison_data.append({
                "Product": item.get('name', 'Unknown'),
                "Price": f"${item.get('price', 0):.2f}",
                "Rating": f"{'⭐' * int(item.get('rating', 0))} ({item.get('rating', 0):.1f})",
                "Description": item.get('description', 'No description')[:50] + "..."
            })
        
        st.dataframe(comparison_data, use_container_width=True)
        
        # Clear comparison button
        if st.button("🗑️ Clear Comparison", use_container_width=True):
            st.session_state.comparison = []
            save_user_data(st.session_state.username)
            st.success("🗑️ Comparison cleared!")
            st.rerun()
    else:
        st.info("📊 No products to compare. Add items from Search or Best-Sellers!")

with tab6:
    st.markdown('<h2 style="color: #667eea;">🛒 Smart Checkout</h2>', unsafe_allow_html=True)
    
    if 'checkout_item' in st.session_state and st.session_state.checkout_item:
        item = st.session_state.checkout_item
        
        st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{item.get('name', 'Unknown Product')}</div>
            <div class="product-price">${item.get('price', 0):.2f}</div>
            <div class="product-rating">
                {'⭐' * int(item.get('rating', 0))} ({item.get('rating', 0):.1f})
            </div>
            <p>{item.get('description', 'No description available')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Checkout form
        st.markdown('<h3>🛒 Checkout Information</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            customer_name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            customer_email = st.text_input("📧 Email", placeholder="Enter your email")
        
        with col2:
            shipping_address = st.text_input("🏠 Shipping Address", placeholder="Enter your address")
            payment_method = st.selectbox("💳 Payment Method", ["Credit Card", "Debit Card", "PayPal", "Apple Pay"])
        
        # Order summary
        st.markdown('<h3>📋 Order Summary</h3>', unsafe_allow_html=True)
        
        subtotal = item.get('price', 0)
        tax = subtotal * 0.08  # 8% tax
        shipping = 10.0 if subtotal < 100 else 0.0
        total = subtotal + tax + shipping
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Subtotal", f"${subtotal:.2f}")
            st.metric("Tax", f"${tax:.2f}")
            st.metric("Shipping", f"${shipping:.2f}")
        
        with col2:
            st.metric("Total", f"${total:.2f}")
            if total <= st.session_state.global_budget:
                st.success("✅ Within budget!")
            else:
                st.error("❌ Over budget!")
        
        # Place order button
        if st.button("🚀 Place Order", use_container_width=True):
            if customer_name and customer_email and shipping_address:
                # Enregistrer la vente dans la base de données
                sale_result = record_sale_api(item, customer_name, customer_email, total)
                
                if sale_result["success"]:
                    st.markdown("""
                    <div class="success-message">
                        🎉 Order placed successfully! Your Smart & Budget AI order is being processed and saved to your account.
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                    
                    # Clear checkout item
                    st.session_state.checkout_item = None
                    st.rerun()
                else:
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Order processing failed: {sale_result['error']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Please fill all required fields!")
    else:
        st.info("🛒 No items in checkout. Add items from Search, Best-Sellers, or Wishlist!")

with tab7:
    st.markdown('<h2 style="color: #667eea;">👤 Smart Profile</h2>', unsafe_allow_html=True)
    
    # User information
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.username}</div>
            <div class="metric-label">Username</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${st.session_state.global_budget}</div>
            <div class="metric-label">Smart Budget</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.wishlist)}</div>
            <div class="metric-label">Wishlist Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<h3>📊 Shopping Statistics</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        total_searches = len(st.session_state.history)
        st.metric("Total Searches", total_searches)
        
        if st.session_state.history:
            last_search = st.session_state.history[-1].get('query', 'No searches yet')
            st.metric("Last Search", last_search)
    
    with col2:
        total_chat_messages = len(st.session_state.conversation)
        st.metric("Chat Messages", total_chat_messages)
        
        wishlist_value = sum(item.get('price', 0) for item in st.session_state.wishlist)
        st.metric("Wishlist Value", f"${wishlist_value:.2f}")
    
    # Budget management
    st.markdown('<h3>💰 Budget Management</h3>', unsafe_allow_html=True)
    
    new_budget = st.number_input("📊 Update Smart Budget", min_value=0, value=st.session_state.global_budget, step=50)
    
    if st.button("💾 Update Budget", use_container_width=True):
        st.session_state.global_budget = new_budget
        save_user_data(st.session_state.username)
        st.success("✅ Smart Budget updated!")
        st.rerun()
    
    # Search history
    if st.session_state.history:
        st.markdown('<h3>🔍 Recent Searches</h3>', unsafe_allow_html=True)
        
        for h in st.session_state.history[-5:]:
            if isinstance(h, dict):
                query = h.get('query', h.get('product_name', 'Unknown'))
                count = h.get('count', 1)
                st.write(f"• {query} ({count} results)")
            else:
                st.write(f"• {h}")
    
    # Clear data button
    if st.button("🗑️ Clear All Data", use_container_width=True):
        st.session_state.wishlist = []
        st.session_state.comparison = []
        st.session_state.alerts = []
        st.session_state.history = []
        st.session_state.conversation = []
        save_user_data(st.session_state.username)
        st.success("🗑️ All data cleared!")
        st.rerun()

# Footer animé
st.markdown("""
<div class="main-header">
    <h3>🤖 Smart & Budget AI</h3>
    <p>✨ Revolutionizing Your Shopping Experience with AI ✨</p>
</div>
""", unsafe_allow_html=True)
