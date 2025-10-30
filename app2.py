import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Flask API base URL (assuming Flask is running on localhost:5000)
API_BASE_URL = "http://localhost:5000/api"

def login_user():
    st.title("Inventory Management System - Login (API Version)")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Simple client-side check (in real app, use proper auth)
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.session_state.user_id = 1
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def get_items():
    try:
        response = requests.get(f"{API_BASE_URL}/items")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch items: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def add_item(item_data):
    try:
        response = requests.post(f"{API_BASE_URL}/items", json=item_data)
        return response.status_code == 201
    except Exception as e:
        st.error(f"Error adding item: {e}")
        return False

def update_item(item_id, item_data):
    try:
        response = requests.put(f"{API_BASE_URL}/items/{item_id}", json=item_data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error updating item: {e}")
        return False

def delete_item(item_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/items/{item_id}")
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error deleting item: {e}")
        return False

def main_app():
    st.title("Inventory Management System (API-Based UI)")

    # Sidebar with filters and actions
    st.sidebar.header("Filters & Actions")

    # Search and filter
    search_term = st.sidebar.text_input("Search by Product Name or SKU")
    category_filter = st.sidebar.selectbox("Filter by Category", ["All"] + list(set([item.get('category', '') for item in get_items() if item.get('category')])))

    # Export option
    if st.sidebar.button("Export to CSV"):
        items = get_items()
        if items:
            df = pd.DataFrame(items)
            csv = df.to_csv(index=False)
            st.sidebar.download_button("Download CSV", csv, "inventory_export.csv", "text/csv")
        else:
            st.sidebar.warning("No items to export")

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Inventory", "Add Item", "Edit Item", "Delete Item"])

    with tab1:
        st.header("Dashboard")
        items = get_items()
        if items:
            df = pd.DataFrame(items)

            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", len(df))
            with col2:
                st.metric("Total Value", f"${df['price'].sum():.2f}")
            with col3:
                low_stock = len(df[df['quantity'] < 10])
                st.metric("Low Stock Items", low_stock)

            # Category distribution
            if 'category' in df.columns:
                st.subheader("Items by Category")
                category_counts = df['category'].value_counts()
                st.bar_chart(category_counts)

            # Price distribution
            st.subheader("Price Distribution")
            # Create a simple histogram using matplotlib
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.hist(df['price'], bins=10, edgecolor='black')
            ax.set_xlabel('Price')
            ax.set_ylabel('Frequency')
            ax.set_title('Price Distribution')
            st.pyplot(fig)
        else:
            st.info("No items in inventory")

    with tab2:
        st.header("Inventory Items")
        items = get_items()

        # Apply filters
        if items:
            df = pd.DataFrame(items)
            if search_term:
                df = df[df['product_name'].str.contains(search_term, case=False, na=False) |
                        df['sku'].str.contains(search_term, case=False, na=False)]
            if category_filter != "All":
                df = df[df['category'] == category_filter]

            st.dataframe(df, use_container_width=True)

            # Show low stock alerts
            low_stock = df[df['quantity'] < 10]
            if not low_stock.empty:
                st.warning("Low Stock Alert:")
                st.dataframe(low_stock[['product_name', 'sku', 'quantity']], use_container_width=True)
        else:
            st.info("No items in inventory")

    with tab3:
        st.header("Add New Item")
        with st.form("add_item_api"):
            product_name = st.text_input("Product Name")
            sku = st.text_input("SKU")
            category = st.text_input("Category")
            quantity = st.number_input("Quantity", min_value=0, value=0)
            supplier = st.text_input("Supplier")
            price = st.number_input("Price", min_value=0.0, value=0.0)
            location = st.text_input("Location")

            submitted = st.form_submit_button("Add Item")
            if submitted:
                if not sku:
                    st.error("SKU is required")
                else:
                    item_data = {
                        "product_name": product_name,
                        "sku": sku,
                        "category": category,
                        "quantity": quantity,
                        "supplier": supplier,
                        "price": price,
                        "location": location
                    }
                    if add_item(item_data):
                        st.success("Item added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add item")

    with tab4:
        st.header("Edit Item")
        items = get_items()
        if items:
            item_options = {f"{item['id']}: {item['product_name']} ({item['sku']})": item for item in items}
            selected_item_key = st.selectbox("Select Item to Edit", list(item_options.keys()))
            selected_item = item_options[selected_item_key]

            with st.form("edit_item_api"):
                product_name = st.text_input("Product Name", value=selected_item.get('product_name', ''))
                sku = st.text_input("SKU", value=selected_item.get('sku', ''))
                category = st.text_input("Category", value=selected_item.get('category', ''))
                quantity = st.number_input("Quantity", min_value=0, value=selected_item.get('quantity', 0))
                supplier = st.text_input("Supplier", value=selected_item.get('supplier', ''))
                price = st.number_input("Price", min_value=0.0, value=selected_item.get('price', 0.0))
                location = st.text_input("Location", value=selected_item.get('location', ''))

                submitted = st.form_submit_button("Update Item")
                if submitted:
                    item_data = {
                        "product_name": product_name,
                        "sku": sku,
                        "category": category,
                        "quantity": quantity,
                        "supplier": supplier,
                        "price": price,
                        "location": location
                    }
                    if update_item(selected_item['id'], item_data):
                        st.success("Item updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update item")
        else:
            st.info("No items to edit")

    with tab5:
        st.header("Delete Item")
        items = get_items()
        if items:
            item_options = {f"{item['id']}: {item['product_name']} ({item['sku']})": item for item in items}
            selected_item_key = st.selectbox("Select Item to Delete", list(item_options.keys()))
            selected_item = item_options[selected_item_key]

            st.write(f"**Product:** {selected_item['product_name']}")
            st.write(f"**SKU:** {selected_item['sku']}")
            st.write(f"**Quantity:** {selected_item['quantity']}")

            if st.button("Delete Item", type="primary"):
                if delete_item(selected_item['id']):
                    st.success("Item deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete item")
        else:
            st.info("No items to delete")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def main():
    st.set_page_config(page_title="Inventory Management (API)", page_icon="📦", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        login_user()

if __name__ == "__main__":
    main()
