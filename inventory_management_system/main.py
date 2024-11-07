import json
import os

class Product:
    def __init__(self, product_id, name, category, price, stock_quantity):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.stock_quantity = stock_quantity

    def __str__(self):
        return (f"ID: {self.product_id}, Name: {self.name}, Category: {self.category}, "
                f"Price: ${self.price:.2f}, Stock: {self.stock_quantity}")
    
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock_quantity": self.stock_quantity
        }
    
    @staticmethod
    def from_dict(data):
        return Product(data['product_id'], data['name'], data['category'], data['price'], data['stock_quantity'])


class Inventory:
    def __init__(self, low_stock_threshold=5):
        self.products = {}
        self.low_stock_threshold = low_stock_threshold
        self.load_from_file()

    def add_product(self, product):
        if product.product_id in self.products:
            raise ValueError(f"Error: Product ID {product.product_id} already exists in the inventory.")
        self.products[product.product_id] = product
        print(f"Product added successfully! Details: {product}")
        self.save_to_file()

    def update_product(self, product_id, name=None, category=None, price=None, stock_quantity=None):
        if product_id not in self.products:
            raise ValueError("Product not found.")
        
        product = self.products[product_id]

        if stock_quantity is not None:
            if product.stock_quantity + stock_quantity < self.low_stock_threshold:
                print(f"Updating stock to {product.stock_quantity + stock_quantity} will bring stock below the threshold of {self.low_stock_threshold}.")
                confirm = input("Do you want to proceed with this update? (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Update canceled.")
                    return
                
            if name is not None:
                product.name = name
            if category is not None:
                product.category = category
            if price is not None:
                product.price = price
            if stock_quantity is not None:
                product.stock_quantity += stock_quantity

            print("Product updated successfully.")
            self.save_to_file()

    def delete_product(self, product_id):
        if product_id not in self.products:
            raise ValueError("Product not found.")
        del self.products[product_id]
        print("Product deleted successfully.")
        self.save_to_file()

    def view_all_products(self):
        if not self.products:
            print("No products in inventory.")
            return
        for product in self.products.values():
            print(product)
            if product.stock_quantity < self.low_stock_threshold:
                print(f"*** Low stock alert for {product.name}! ***")

    def check_low_stock(self, product_id, quantity):
        if product_id in self.products:
            remaining_stock = self.products[product_id].stock_quantity - quantity
            if remaining_stock < self.low_stock_threshold:
                print(f"Warning: Ordering {quantity} of {self.products[product_id].name} will lower stock below threshold!")

    def save_to_file(self):
        with open('inventory.json', 'w') as file:
            json.dump([product.to_dict() for product in self.products.values()], file)

    def load_from_file(self):
        if os.path.exists('inventory.json'):
            with open('inventory.json', 'r') as file:
                products_data = json.load(file)
                for product_data in products_data:
                    product = Product.from_dict(product_data)
                    self.products[product.product_id] = product
            print("Inventory loaded successfully.")


class Order:
    def __init__(self, order_id, username, products):
        self.order_id = order_id
        self.username = username
        self.products = products
        self.total_amount = self.calculate_total()

    def calculate_total(self):
        total = 0
        for product_id, quantity in self.products:
            if product_id in ims.inventory.products:
                total += ims.inventory.products[product_id].price * quantity
        return total
            
    def __str__(self):
        product_details = ', '.join([f"{product_id} (Qty: {quantity})" for product_id, quantity in self.products])
        return (f"Order ID: {self.order_id}, User: {self.username}, Products: {product_details}, "
                f"Total Amount: ${self.total_amount:.2f}")
    

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class InventoryManagementSystem:
    def __init__(self):
        self.users = {
            "admin": User("admin", "adminpass", "Admin"),
            "user": User("user", "userpass", "User")
        }
        self.inventory = Inventory()
        self.orders = []
        self.logged_in_user = None

    def login(self):
        username = input("Enter username: ")
        password = input("Enter password: ")
        user = self.users.get(username)
        if user and user.password == password:
            self.logged_in_user = user
            print(f"Logged in as {user.username} ({user.role})")
            return True
        else:
            print("Invalid username or password.")
            return False
        
    def logout(self):
        self.logged_in_user = None
        print("Logged out successfully.")

    def run(self):
        while True:
            if not self.logged_in_user:
                self.login()

            if self.logged_in_user:
                if self.logged_in_user.role == "Admin":
                    self.admin_menu()
                else:
                    self.user_menu()

    def admin_menu(self):
        while True:
            print("\nAdmin Menu")
            print("1. Add Product")
            print("2. Update Product")
            print("3. Delete Product")
            print("4. View All Products")
            print("5. View Orders")
            print("6. Confirm Order")
            print("7. Reject Order")
            print("8. Logout")
            choice = input("Select an option: ")
            try: 
                if choice == '1':
                    self.add_product()
                elif choice == '2':
                    self.update_product()
                elif choice == '3':
                    self.delete_product()
                elif choice == '4':
                    self.inventory.view_all_products()
                elif choice == '5':
                    self.view_orders()
                elif choice == '6':
                    self.confirm_order()
                elif choice == '7':
                    self.reject_order()
                elif choice == '8':
                    self.logout()
                    break
                else:
                    print("Invalid option.")
            except Exception as e:
                print(f"Error: {e}")

    def user_menu(self):
        while True:
            print("\nUser Menu")
            print("1. View All Products")
            print("2. Place Order")
            print("3. View Orders")
            print("4. Logout")
            choice = input("Select an option: ")
            if choice == '1':
                self.inventory.view_all_products()
            elif choice == '2':
                self.place_order()
            elif choice == '3':
                self.view_orders()
            elif choice == '4':
                self.logout()
                break
            else:
                print("Invalid option.")

    def add_product(self):
        try:
            product_id = input("Enter product ID: ")
            if product_id in self.inventory.products:
                existing_product = self.inventory.products[product_id]
                print(f"Error: Product ID {product_id} already exists in the inventory. Details: {existing_product}")
                return
            
            name = input("Enter product name: ")
            category = input("Enter product category: ")
            price = float(input("Enter product price: "))
            stock_quantity = int(input("Enter stock quantity: "))
            product = Product(product_id, name, category, price, stock_quantity)
            self.inventory.add_product(product)
        except ValueError as e:
            print(f"Error: {e}")

    def update_product(self):
        try:
            product_id = input("Enter product ID to update: ")
            name = input("Enter new product name (or leave blank): ") or None
            category = input("Enter new product category (or leave blank): ") or None
            price_input = input("Enter new product price (or leave blank): ")
            price = float(price_input) if price_input else None
            stock_quantity_input = input("Enter new stock quantity (or leave blank): ")
            stock_quantity = int(stock_quantity_input) if stock_quantity_input else None
            self.inventory.update_product(product_id, name, category, price, stock_quantity)
        except ValueError as e:
            print(f"Error: {e}")

    def delete_product(self):
        try:
            product_id = input("Enter product ID to delete: ")
            self.inventory.delete_product(product_id)
        except ValueError as e:
            print(f"Error: {e}")

    def place_order(self):
        if self.logged_in_user:
            print("Available Products:")
            self.inventory.view_all_products()
            products_to_order = []
            while True:
                product_id = input("Enter product ID to order (or 'done' to finish): ")
                if product_id.lower() == 'done':
                    break
                quantity = int(input("Enter quantity: "))
                products_to_order.append((product_id, quantity))

            for product_id, quantity in products_to_order:
                self.inventory.check_low_stock(product_id, quantity)

            order_id = len(self.orders) + 1
            order = Order(order_id, self.logged_in_user.username, products_to_order)
            self.orders.append(order)
            print(f"Order placed successfully! {order}")

            for product_id, quantity in products_to_order:
                if product_id in self.inventory.products:
                    self.inventory.products[product_id].stock_quantity -= quantity
            self.inventory.save_to_file()
        else:
            print("You must be logged in to place an order.")

    def view_orders(self):
        if not self.orders:
            print("No orders placed.")
            return
        for order in self.orders:
            print(order)
    
    def confirm_order(self):
        if not self.orders:
            print("No orders to confirm.")
            return
        
        print("\nPending Orders:")
        for order in self.orders:
            print(order)

        order_id = int(input("Enter the order ID to confirm: "))
        for order in self.orders:
            if order.order_id == order_id:
                print(f"Order {order_id} confirmed!")
                self.orders.remove(order)
                return
            
        print("Order ID not found.")

    def reject_order(self):
        if not self.orders:
            print("No orders to reject.")
            return
        
        print("\nPending Orders:")
        for order in self.orders:
            print(order)

        order_id = int(input("Enter the order ID to reject: "))
        for order in self.orders:
            if order.order_id == order_id:
                print(f"Order {order_id} rejected!")
                for product_id, quantity in order.products:
                    self.inventory.products[product_id].stock_quantity += quantity
                    print(f"Stock of {self.inventory.products[product_id].name} restored by {quantity}.")

                self.orders.remove(order)
                self.inventory.save_to_file()
                return
            
        print("Order ID not found.")

if __name__ == "__main__":
    ims = InventoryManagementSystem()
    ims.run()