# 🤖 Smart & Budget AI

**Advanced AI-Powered Shopping Experience with Intelligent Budget Management**

## 🌟 Features

### 🛍️ Smart Shopping
- **🔎 Intelligent Search**: AI-powered product discovery with budget filtering
- **🔥 Trending Products**: Real-time best-sellers and trending items
- **❤️ Smart Wishlist**: Save and manage your favorite products
- **⚖️ Product Comparison**: Compare up to 3 products side-by-side
- **🛒 Smart Checkout**: Seamless checkout with budget validation

### 🤖 AI Assistant
- **💬 Conversational AI**: Get personalized shopping advice
- **🎨 Fashion Recommendations**: Style suggestions based on preferences
- **💰 Budget Optimization**: Smart spending recommendations
- **📊 Trend Analysis**: Fashion trend predictions and insights

### 📊 Dashboard & Analytics
- **👤 User Profile**: Comprehensive shopping statistics
- **📈 Real-time Metrics**: Track spending, searches, and preferences
- **🔍 Search History**: Complete search history with timestamps
- **🔔 Smart Alerts**: Budget warnings and deal notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart_and_budget_ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the backend**
```bash
cd backend
python main.py
```

4. **Start the frontend**
```bash
cd frontend
streamlit run app.py
```

5. **Access the application**
- Frontend: http://localhost:8517
- Backend API: http://localhost:8000

## 📁 Project Structure

```
smart_and_budget_ai/
├── backend/
│   ├── main.py              # FastAPI backend server
│   ├── database.py          # Database configuration
│   └── models.py            # Database models
├── frontend/
│   └── app.py               # Streamlit frontend application
├── scripts/
│   └── ingest_data.py       # Data ingestion script
├── data/
│   ├── flipkart_fashion_products_dataset.json
│   └── output.xlsx
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database for user data and sales
- **Qdrant**: Vector database for product search
- **Sentence Transformers**: Text embeddings
- **CLIP**: Image-text model for visual search

### Frontend
- **Streamlit**: Interactive web application framework
- **Requests**: HTTP client for API communication
- **Pickle**: Local data persistence
- **Custom CSS**: Animated and responsive design

## 🎯 Key Features

### Smart Search
- **Text-based Search**: Find products by keywords
- **Budget Filtering**: Filter results by maximum price
- **AI Recommendations**: Get personalized product suggestions
- **Real-time Results**: Instant product discovery

### Budget Management
- **Smart Budget**: Set and track shopping budget
- **Spending Analytics**: Monitor your shopping habits
- **Deal Alerts**: Get notified about price drops
- **Wishlist Value**: Track total value of saved items

### AI Assistant
- **Natural Conversations**: Chat with AI shopping assistant
- **Fashion Advice**: Get style recommendations
- **Product Insights**: Learn about products and trends
- **Shopping Tips**: Smart shopping strategies

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DATABASE_URL=sqlite:///./snap_budget.db

# API Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8517

# Vector Database
QDRANT_URL=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>

# AI Models
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
CLIP_MODEL=openai/clip-vit-base-patch32
```

## 📊 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /health` - Health check

### Products
- `POST /search_text` - Text-based product search
- `GET /bestsellers` - Get trending products
- `POST /record_sale` - Record a purchase

### User Data
- `GET /history/{user_id}` - Get user search history
- `GET /stats/{user_id}` - Get user statistics

## 🎨 UI/UX Features

### Responsive Design
- **Mobile-friendly**: Works on all devices
- **Animated Interface**: Smooth transitions and effects
- **Dark/Light Mode**: Comfortable viewing experience
- **Accessibility**: WCAG compliant design

### Interactive Elements
- **Hover Effects**: Product cards with animations
- **Real-time Updates**: Live data synchronization
- **Progress Indicators**: Loading states and feedback
- **Error Handling**: User-friendly error messages

## 🔒 Security Features

- **Data Encryption**: Secure data transmission
- **Input Validation**: Prevent injection attacks
- **Session Management**: Secure user sessions
- **Rate Limiting**: API abuse prevention

## 📈 Performance

- **Fast Search**: Sub-second product discovery
- **Caching**: Optimized data retrieval
- **Lazy Loading**: Efficient resource management
- **Scalable Architecture**: Handles growing user base

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the FAQ section

## 🚀 Future Enhancements

- **Image Search**: Visual product discovery
- **Voice Search**: Hands-free shopping
- **Mobile App**: Native mobile applications
- **Social Features**: Share and discover with friends
- **AR Integration**: Virtual try-on features

---

**🤖 Smart & Budget AI - Revolutionizing Your Shopping Experience**
