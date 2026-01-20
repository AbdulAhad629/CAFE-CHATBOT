# WhatsApp Cafeteria Chatbot

Automated food ordering system for university cafeterias using WhatsApp Business API.

## 📋 Project Overview

This system allows students to:
- Browse the café menu via WhatsApp
- Place orders through a conversational interface
- Make secure online payments
- Receive real-time order status updates

Café staff can:
- View incoming orders in real-time
- Update order status
- Generate sales reports

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Supabase account
- WhatsApp Business API access
- Payment gateway account (optional for testing)

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
│   ├── __init__.py              # App factory
│   ├── routes/                  # API endpoints
│   │   ├── whatsapp_routes.py   # WhatsApp webhook
│   │   ├── menu_routes.py       # Menu management
│   │   ├── order_routes.py      # Order handling
│   │   ├── payment_routes.py    # Payment processing
│   │   └── staff_routes.py      # Staff dashboard
│   │
│   ├── services/                # Business logic
│   │   └── whatsapp_service.py  # WhatsApp API integration
│   │
│   ├── models/                  # Data models (future)
│   ├── utils/                   # Utilities
│   │   └── supabase_client.py   # Database connection
│   │
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # HTML templates
│
├── config/
│   └── config.py                # Configuration settings
│
├── tests/                       # Test files
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore file
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## 🔧 Configuration

### WhatsApp Cloud API Setup

1. Create a Meta Developer account
2. Create a WhatsApp Business App
3. Get your Phone Number ID and Access Token
4. Set up webhook URL: `https://your-domain.com/webhook/whatsapp`
5. Subscribe to webhook events: `messages`

### Supabase Setup

1. Create a new Supabase project
2. Copy your project URL and anon key
3. Create the database tables using the SQL provided above
4. Enable Row Level Security (RLS) policies as needed

## 📚 API Endpoints

### WhatsApp Webhook
- `GET /webhook/whatsapp` - Verify webhook
- `POST /webhook/whatsapp` - Receive messages

### Menu Management
- `GET /api/menu/` - Get all menu items
- `GET /api/menu/<id>` - Get specific item
- `GET /api/menu/category/<category>` - Get items by category

### Orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/<id>` - Get order details
- `PATCH /api/orders/<id>/status` - Update order status

### Payments
- `POST /api/payment/initiate` - Initiate payment
- `GET /api/payment/<id>` - Get payment status
- `POST /api/payment/callback` - Payment gateway callback

### Staff Dashboard
- `GET /staff/dashboard` - Dashboard page
- `GET /staff/orders/pending` - Get pending orders
- `GET /staff/orders/history` - Get order history
- `GET /staff/reports/sales` - Get sales report

## 🧪 Testing

```bash
pytest tests/
```

## 📝 Next Steps

1. Implement chatbot conversation flow
2. Add payment gateway integration
3. Create staff dashboard UI
4. Implement order notifications
5. Add authentication for staff
6. Create admin panel for menu management

## 👥 Team

- Merub Nadeem (2022-BS-CS-137) - Chatbot development & Frontend
- Tehreem Rashid (2022-BS-CS-219) - Documentation & Testing
- Mahnoor (2022-BS-CS-228) - Database & Backend

**Supervisor:** Ma'am Saima Kanwal

## 📄 License

This project is developed as part of the Bachelor of Science in Computer Science program at The University of Faisalabad.
