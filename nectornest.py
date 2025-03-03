import streamlit as st
import sqlite3

def create_tables():
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user TEXT, product_id INTEGER, quantity INTEGER, status TEXT, transaction_id TEXT, payment_proof TEXT)''')
    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, 'admin', 'Password', 'admin')")
    conn.commit()
    conn.close()

def register_user(username, password, role='user'):
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_product(name, price, stock):
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('INSERT INTO products (name, price, stock) VALUES (?, ?, ?)', (name, price, stock))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    return products

def place_order(user, product_id, quantity, transaction_id, payment_proof):
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('INSERT INTO orders (user, product_id, quantity, status, transaction_id, payment_proof) VALUES (?, ?, ?, ?, ?, ?)', 
              (user, product_id, quantity, 'Pending', transaction_id, payment_proof))
    conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect('nectarnest.db')
    c = conn.cursor()
    c.execute('SELECT * FROM orders')
    orders = c.fetchall()
    conn.close()
    return orders

def main():
    st.set_page_config(page_title="NectarNest", page_icon="🍯", layout="wide")
    
    st.title('🍯 NectarNest - The Purest Honey Store')
    menu = ['🏠 Home', '🛒 Shop', '📩 Queries', '🔑 Login / Sign Up', '📦 Admin Panel']
    choice = st.sidebar.radio('📌 Menu', menu)
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.role = None
    
    if choice == '🏠 Home':
        st.subheader('Welcome to NectarNest!')
        st.write('Buy the purest honey directly from the hive. Our honey is 100% organic and farm fresh.')
    
    elif choice == '🛒 Shop':
        if not st.session_state.logged_in:
            st.warning('⚠️ Please log in or sign up to shop.')
        else:
            st.subheader(f'🍯 Welcome, {st.session_state.user}! Here is our collection:')
            products = get_products()
            cart = []
            
            for product in products:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f'**{product[1]}** - ₹{product[2]} (Stock: {product[3]})')
                with col2:
                    if product[3] > 0:
                        quantity = st.number_input(f'Qty for {product[1]}', min_value=1, max_value=max(1, product[3]), step=1, key=f"qty_{product[0]}")
                        cart.append((product[0], product[1], product[2], quantity))
                    else:
                        st.error(f'🚫 {product[1]} is out of stock.')
            
            total_amount = sum(item[2] * item[3] for item in cart)
            st.subheader(f'💰 Total Amount: ₹{total_amount}')
            transaction_id = st.text_input('Transaction ID', key="transaction")
            payment_proof = st.file_uploader('Upload Payment Screenshot', type=['png', 'jpg', 'jpeg'], key="proof")
            
            if st.button('Checkout'):
                for item in cart:
                    place_order(st.session_state.user, item[0], item[3], transaction_id, payment_proof.name if payment_proof else '')
                st.success('✅ Your order has been placed successfully!')
    
    elif choice == '🔑 Login / Sign Up':
        st.subheader('🔑 User Login')
        username = st.text_input('👤 Username')
        password = st.text_input('🔑 Password', type='password')
        if st.button('Login'):
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.session_state.role = user[3]
                st.success(f'🎉 Welcome, {username}!')
            else:
                st.error('❌ Invalid credentials!')
        
        st.subheader('📝 Create an Account')
        new_username = st.text_input('👤 Choose a Username')
        new_password = st.text_input('🔑 Choose a Password', type='password')
        if st.button('Sign Up'):
            register_user(new_username, new_password)
            st.success('✅ Account Created! You can now log in.')
    
    elif choice == '📦 Admin Panel':
        if st.session_state.logged_in and st.session_state.role == 'admin':
            st.subheader('📦 Admin Dashboard')
            st.subheader('View All Orders')
            orders = get_orders()
            for order in orders:
                st.write(f'Order ID: {order[0]}, User: {order[1]}, Product ID: {order[2]}, Quantity: {order[3]}, Status: {order[4]}')
            st.subheader('Add a Product')
            name = st.text_input('Product Name')
            price = st.number_input('Price', min_value=0.0, step=0.1)
            stock = st.number_input('Stock', min_value=0, step=1)
            if st.button('Add Product'):
                add_product(name, price, stock)
                st.success('✅ Product Added!')
        else:
            st.warning('⚠️ Admins only!')
    
if __name__ == '__main__':
    create_tables()
    main()
