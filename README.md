# WhatsApp Cafeteria Bot

An intelligent automated food ordering system for university cafeterias with real-time WhatsApp integration, AI chatbot conversation, and secure payment processing.

**Developer:** Muhammad Naeem | FAST NUCES

---

## 📋 Project Overview

This comprehensive system enables seamless food ordering through WhatsApp with intelligent conversation handling, real-time order management, and payment integration.

### Student Features
- 💬 Natural language conversation with AI chatbot (Groq LLaMA 3.3)
- 📋 Browse complete café menu with categories
- 🛒 Smart shopping cart with add/modify/remove functionality
- 💳 Multiple payment methods (Cash, JazzCash, EasyPaisa, Card)
- 📍 Real-time order status tracking
- 🔔 WhatsApp notifications on order updates
- 🌍 Multi-language support (English & Roman Urdu)

### Staff Features
- 📊 Real-time staff dashboard with live order updates
- 📈 Order analytics and sales statistics
- ⚙️ Order status management (Pending → Confirm → Preparing → Ready → Complete)
- 📱 Mobile-friendly interface
- 💰 Revenue tracking and daily statistics

### System Features
- ✅ 36+ comprehensive test cases (all passing)
- 🤖 Groq AI integration for natural conversations
- 🗄️ Supabase PostgreSQL database with real-time sync
- 🔐 Secure payment processing with database persistence
- 📡 Twilio WhatsApp integration (with Meta Cloud API fallback)
- 🔄 Session management and state tracking
- ⚡ Automatic chatbot state reset for flexibility
- 📧 Automated order notifications

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Supabase account (PostgreSQL database)
- Twilio WhatsApp Business API credentials
- Groq API key (optional, for AI chatbot)
- Payment gateway account (optional for live testing)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd whatsapp-cafeteria-bot
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- Supabase URL and keys
- WhatsApp API credentials
- Payment gateway credentials

5. **Set up Supabase database**

Run the following SQL in your Supabase SQL editor:

```sql
-- Create students table
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    whatsapp_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create menu_items table
CREATE TABLE menu_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    image_url TEXT,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create orders table
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES students(id),
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create order_items table
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id BIGINT REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

-- Create payments table
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    transaction_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create staff table
CREATE TABLE staff (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

6. **Add sample menu data**

```sql
INSERT INTO menu_items (name, description, price, category, available) VALUES
('Burger', 'Classic beef burger with cheese', 250.00, 'Main Course', TRUE),
('Pizza Slice', 'Cheese pizza slice', 150.00, 'Main Course', TRUE),
('Fries', 'Crispy french fries', 100.00, 'Sides', TRUE),
('Soft Drink', 'Cold beverage', 50.00, 'Beverages', TRUE),
('Coffee', 'Hot coffee', 80.00, 'Beverages', TRUE);
```

### Running the Application

**Development mode:**
```bash
python run.py
```

The server will start at `http://localhost:5000`

**Production mode:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📁 Project Structure

```
whatsapp-cafeteria-bot/
│
├── app/
│   ├── __init__.py                      # Flask app factory & initialization
│   │
│   ├── routes/                          # API & Webhook endpoints
│   │   ├── __init__.py
│   │   ├── whatsapp_routes.py          # WhatsApp webhook (Twilio)
│   │   ├── twilio_routes.py            # Twilio integration
│   │   ├── menu_routes.py              # Menu management & retrieval
│   │   ├── order_routes.py             # Order creation & tracking
│   │   ├── payment_routes.py           # Payment processing
│   │   └── staff_routes.py             # Staff dashboard & management
│   │
│   ├── services/                        # Business logic & AI integration
│   │   ├── __init__.py
│   │   ├── chatbot_service.py          # Main chatbot orchestrator
│   │   │                               # - State management
│   │   │                               # - Message routing
│   │   │                               # - Natural language processing
│   │   ├── groq_service.py             # Groq API integration (LLaMA 3.3)
│   │   ├── whatsapp_service.py         # WhatsApp/Twilio service
│   │   ├── payment_service.py          # Payment creation & tracking
│   │   ├── notification_service.py     # Order notifications
│   │   └── transformer_service.py      # Urdu/English transformations
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── model_architecture.py       # Data models
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── supabase_client.py          # Supabase DB connection
│   │
│   ├── static/                          # Frontend assets
│   │   ├── css/                        # Stylesheets
│   │   ├── js/                         # JavaScript files
│   │   └── images/                     # Images & icons
│   │
│   └── templates/                       # HTML templates
│       └── staff/
│           └── dashboard.html          # Real-time staff dashboard
│
├── config/
│   ├── __init__.py
│   └── config.py                       # Configuration management
│
├── tests/
│   ├── test_complete_flow.py          # 36-case comprehensive test
│   └── [other test files]
│
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Python dependencies
├── run.py                              # Application entry point
├── PROJECT_STRUCTURE.txt               # Project structure documentation
├── PAYMENT_VERIFICATION_COMPLETE.md   # Payment system verification
└── README.md                           # This file
```

## 🗄️ Database Schema

### students
```sql
- id (BIGSERIAL PRIMARY KEY)
- whatsapp_number (VARCHAR UNIQUE) - Customer WhatsApp number
- name (VARCHAR)
- created_at (TIMESTAMP)
```

### menu_items
```sql
- id (BIGSERIAL PRIMARY KEY)
- name (VARCHAR) - Item name
- description (TEXT) - Item description
- price (DECIMAL) - Price in PKR
- category (VARCHAR) - Food category
- image_url (TEXT) - Item image
- available (BOOLEAN) - Availability status
- created_at (TIMESTAMP)
```

### orders
```sql
- id (BIGSERIAL PRIMARY KEY)
- student_id (BIGINT FK) - Customer reference
- total (DECIMAL) - Order total in PKR
- status (VARCHAR) - pending/confirmed/preparing/ready/completed
- payment_method (VARCHAR) - cash/jazzcash/easypaisa/card
- payment_id (VARCHAR FK) - Reference to payments table
- payment_status (VARCHAR) - Payment status tracking
- transaction_id (VARCHAR) - External transaction reference
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### order_items
```sql
- id (BIGSERIAL PRIMARY KEY)
- order_id (BIGINT FK) - Reference to orders
- menu_item_id (BIGINT FK) - Reference to menu_items
- quantity (INTEGER) - Item quantity
- subtotal (DECIMAL) - Item subtotal
```

### payments
```sql
- id (BIGSERIAL PRIMARY KEY) - Payment record ID
- order_id (BIGINT FK) - Reference to orders
- amount (DECIMAL) - Payment amount in PKR
- status (VARCHAR) - pending/completed/failed
- created_at (TIMESTAMP)
```

### user_sessions
```sql
- id (BIGSERIAL PRIMARY KEY)
- phone (VARCHAR) - WhatsApp phone number
- state (VARCHAR) - Conversation state
- cart (JSONB) - Shopping cart data
- current_category (VARCHAR) - Menu browsing state
- last_message (TIMESTAMP)
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# WhatsApp / Twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
WHATSAPP_VERIFY_TOKEN=your-verify-token

# Groq AI (Optional)
GROQ_API_KEY=your-groq-api-key

# Meta Cloud API (Fallback)
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-meta-token

# Payment Gateway (Future Integration)
PAYMENT_GATEWAY_KEY=your-payment-key

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
```

### Installation & Setup

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/whatsapp-cafeteria-bot.git
cd whatsapp-cafeteria-bot
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Database**

Run this SQL in Supabase SQL editor:

```sql
-- Students table
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    whatsapp_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Menu items table
CREATE TABLE menu_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    image_url TEXT,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES students(id),
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(20),
    payment_id VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id BIGINT REFERENCES menu_items(id),
    quantity INTEGER NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

-- Payments table
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(id),
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
    id BIGSERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    state VARCHAR(50) DEFAULT 'idle',
    cart JSONB DEFAULT '[]',
    current_category VARCHAR(50),
    last_message TIMESTAMP DEFAULT NOW()
);

-- Staff table
CREATE TABLE staff (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

5. **Add Sample Menu Data**

```sql
INSERT INTO menu_items (name, description, price, category, available) VALUES
('Biryani', 'Authentic chicken biryani with basmati rice', 350.00, 'Main Course', TRUE),
('Karahi Chicken', 'Spicy chicken karahi with fresh peppers', 400.00, 'Main Course', TRUE),
('Tikka Boti', 'Grilled chicken tikka with spices', 300.00, 'Main Course', TRUE),
('Nihari', 'Traditional nihari with bread', 320.00, 'Main Course', TRUE),
('French Fries', 'Crispy seasoned french fries', 120.00, 'Sides', TRUE),
('Naan Bread', 'Fresh tandoori naan', 80.00, 'Sides', TRUE),
('Soft Drink', 'Cold beverages (Coke, Sprite, etc)', 60.00, 'Beverages', TRUE),
('Lassi', 'Traditional yogurt-based drink', 80.00, 'Beverages', TRUE),
('Coffee', 'Hot brewed coffee', 100.00, 'Beverages', TRUE),
('Biryani Rice', 'Extra rice portion', 150.00, 'Sides', TRUE);
```

6. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ▶️ Running the Application

**Development Mode:**
```bash
python run.py
```

Access at: `http://localhost:5000`

**Production Mode:**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📡 API Endpoints

### WhatsApp Webhook
```
GET  /webhook/whatsapp           - Verify webhook
POST /webhook/whatsapp           - Receive messages
POST /webhook/test-message       - Test message endpoint
```

### Menu Management
```
GET  /api/menu/                  - Get all menu items
GET  /api/menu/<id>              - Get specific menu item
GET  /api/menu/category/<cat>    - Get items by category
```

### Order Management
```
POST /api/orders/create          - Create new order
GET  /api/orders/<id>            - Get order details
GET  /api/orders/track/<id>      - Track order status
GET  /api/orders/history/<phone> - Get order history
PATCH /api/orders/<id>/status    - Update order status
```

### Payment Processing
```
POST /api/payment/initiate       - Create payment
GET  /api/payment/<id>           - Get payment status
POST /api/payment/callback       - Payment gateway callback
```

### Staff Dashboard
```
GET  /staff/dashboard            - Dashboard page (HTML)
GET  /staff/orders/all           - Get all orders
GET  /staff/orders/pending       - Get pending orders
GET  /staff/orders/<id>/update   - Update order
GET  /staff/reports/sales        - Sales statistics
```

## 💬 Chatbot Conversation Flow

### States
- **idle** - Initial state
- **browsing_menu** - Viewing menu
- **viewing_category** - Category selected
- **adding_to_cart** - Adding items
- **viewing_cart** - Cart review
- **selecting_payment** - Payment method selection
- **confirming_order** - Final confirmation

### Supported Commands
```
menu          - Browse menu
1, 2, 3...    - Select category/item
<number>      - Item quantity
checkout      - Start checkout
payment       - Payment options
confirm       - Place order
track         - Track orders
clear         - Clear cart
```

## 🧪 Testing

### Run Test Suite
```bash
python test_complete_flow.py
```

### Test Coverage
- ✅ 36 comprehensive test cases
- ✅ Natural language processing (English & Urdu)
- ✅ Menu browsing and item selection
- ✅ Shopping cart operations
- ✅ Order creation and storage
- ✅ Payment integration
- ✅ Order tracking
- ✅ Dashboard functionality
- ✅ Multi-user concurrent orders
- ✅ Order status updates
- ✅ Notification system

All tests pass with 100% success rate.

## 🔗 Integration Points

### Groq AI Integration
- Model: LLaMA 3.3 70B
- Free tier limit: 30 requests/minute
- Fallback: Rule-based matching (always works)
- Features: Natural conversation, multi-language support

### Twilio WhatsApp Integration
- Primary messaging provider
- Free tier limit: 5 messages/day
- Automatic fallback to Meta Cloud API
- Webhook-based message handling

### Supabase Integration
- Real-time database sync
- Row Level Security (RLS) ready
- Automatic backups
- REST & Realtime API access

## 🚀 Features Implemented

### ✅ Chatbot Features
- [x] Natural language conversation with AI
- [x] English & Roman Urdu support
- [x] State-based conversation management
- [x] Auto-reset for non-state messages
- [x] Context-aware responses
- [x] Error handling & graceful fallbacks

### ✅ Menu System
- [x] Dynamic menu loading from database
- [x] Category-based browsing
- [x] Item description & pricing
- [x] Availability status
- [x] Search functionality

### ✅ Order Management
- [x] Shopping cart (add/modify/remove)
- [x] Quantity selection
- [x] Cart total calculation
- [x] Order creation & storage
- [x] Order tracking by ID
- [x] Order history per customer
- [x] Status updates (7 states)

### ✅ Payment System
- [x] Multiple payment methods
- [x] Payment creation & persistence
- [x] Order-payment linking
- [x] Payment status tracking
- [x] Database integration
- [x] Ready for gateway integration

### ✅ Staff Dashboard
- [x] Real-time order display
- [x] Order status management
- [x] Live statistics (pending, today's revenue)
- [x] Mobile-responsive design
- [x] Order history view
- [x] Sales tracking

### ✅ Notifications
- [x] Order confirmation via WhatsApp
- [x] Status update notifications
- [x] Formatted message templates
- [x] Automatic delivery

## 📊 Performance & Reliability

- **Test Coverage:** 36/36 tests passing (100%)
- **Database Connections:** Stable, optimized queries
- **Error Handling:** Comprehensive try-catch blocks
- **Logging:** Detailed console logs for debugging
- **Scalability:** Ready for production deployment

## 🔐 Security Considerations

- Environment variables for sensitive data
- Webhook verification tokens
- Input validation & sanitization
- Database foreign key constraints
- Session-based state management
- Phone number validation

## 📦 Dependencies

Key packages used:
- **Flask** - Web framework
- **Supabase** - Database client
- **Groq** - AI API integration
- **Twilio** - WhatsApp integration
- **Requests** - HTTP client
- **Python-dotenv** - Environment management

See `requirements.txt` for complete list with versions.

## 🐛 Known Issues & Limitations

1. **Twilio Free Tier:** Limited to 5 messages/day (upgrade for production)
2. **Groq Free Tier:** 30 API calls/minute (sufficient for testing)
3. **Payment Gateway:** Currently using mock implementation (ready for real gateway)

## 🚢 Deployment

### Pre-Deployment Checklist
- [ ] Set environment variables
- [ ] Configure Twilio webhook URL
- [ ] Configure Meta Cloud API (if using)
- [ ] Test with real WhatsApp message
- [ ] Verify Supabase connectivity
- [ ] Review payment gateway setup
- [ ] Enable production mode

### Recommended Hosting
- **Backend:** Heroku, Railway, Render
- **Database:** Supabase (PostgreSQL)
- **Webhook:** Public HTTPS URL required

## 📈 Future Enhancements

1. Real payment gateway integration (JazzCash/EasyPaisa)
2. Loyalty points system
3. Advanced analytics & reporting
4. Admin panel for menu management
5. Customer feedback & ratings
6. Multiple language support
7. Push notifications
8. Machine learning for recommendations

## 📞 Support & Contact

**Developer:** Muhammad Naeem  
**Institution:** FAST NUCES  
**Email:** [naeemubeen639@gmail.com]  

## 📄 License

Developed as part of academic project at FAST NUCES - Islamabad
