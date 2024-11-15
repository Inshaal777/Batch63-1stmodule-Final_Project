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
        self.deleted_ids = set()
        self.low_stock_threshold = low_stock_threshold
        self.load_from_file()

    def add_product(self):
        print("\nAdd Product Menu")
        while True:
            product_id = input("Enter product ID (leave blank for auto-assign, 'back' to cancel): ")
            if product_id.lower() == 'back':
                return
            if not product_id:
                product_id = self.get_next_available_id()

            if product_id in self.products:
                print(f"Error: Product ID {product_id} already exists.")
                return
            
            name = input("Enter product name (or 'back' to cancel): ")
            if name.lower() == 'back': return
            category = input("Enter product category (or 'back' to cancel): ")
            if category.lower() == 'back': return
            price = input("Enter product price (or 'back' to cancel): ")
            if price.lower() == 'back': return
            stock_quantity = input("Enter stock quantity (or 'back' to cancel): ")
            if stock_quantity.lower() == 'back': return

            try:
                price = float(price)
                stock_quantity = int(stock_quantity)
                product = Product(product_id, name, category, price, stock_quantity)
                self.add_product_to_inventory(product)
                break
            except ValueError:
                print("Invalid input. Please enter correct values.")

    def add_product_to_inventory(self, product):
        if product.product_id in self.products:
            print(f"Error: Product ID {product.product_id} already exists.")
            return
        self.products[product.product_id] = product
        print(f"Product added successfully! Details: {product}")
        self.resequence_product_ids()
        self.save_to_file()

    def update_product(self):
        print("\nUpdate Product Menu")
        while True:
            product_id = input("Enter product ID to update (or 'back' to cancel): ")
            if product_id.lower() == 'back':
                return

            if product_id not in self.products:
                print(f"Error: Product ID {product_id} not found in inventory.")
                return
            
            name = input("Enter new product name (leave blank to keep unchanged, 'back' to cancel): ") or None
            if name is None: continue
            category = input("Enter new product category (leave blank to keep unchanged, 'back' to cancel): ") or None
            if category is None: continue
            price = input("Enter new product price (leave blank to keep unchanged, 'back' to cancel): ")
            if price.lower() == 'back': return
            stock_quantity = input("Enter new stock quantity (leave blank to keep unchanged, 'back' to cancel): ")
            if stock_quantity.lower() == 'back': return

            try:
                price = float(price) if price else None
                stock_quantity = int(stock_quantity) if stock_quantity else None
                self.update_product_in_inventory(product_id, name, category, price, stock_quantity)
                break
            except ValueError:
                print("Invalid input. Please enter valid values.")
                
    def update_product_in_inventory(self, product_id, name, category, price, stock_quantity):
        product = self.products[product_id]
        if name is not None:
            product.name = name
        if category is not None:
            product.category = category
        if price is not None:
            product.price = price
        if stock_quantity is not None:
            product.stock_quantity += stock_quantity
        print("Product updated successfully.")
        self.resequence_product_ids()
        self.save_to_file()

    def delete_product(self):
        print("\nDelete Product Menu")
        while True:
            product_id = input("Enter product ID to delete (or 'back' to cancel): ")
            if product_id.lower() == 'back':
                return

            if product_id not in self.products:
                print(f"Error: Product ID {product_id} not found.")
                return
            
            self.delete_product_from_inventory(product_id)
            break

    def delete_product_from_inventory(self, product_id):
        self.deleted_ids.add(product_id)
        del self.products[product_id]
        print(f"Product ID {product_id} deleted successfully.")
        self.resequence_product_ids()
        self.save_to_file()

    def view_all_products(self):
        if not self.products:
            print("No products in inventory.")
            return
        for product in self.products.values():
            print(product)
            if product.stock_quantity < self.low_stock_threshold:
                print(f"*** Low stock alert for {product.name}! ***")

    def generate_next_product_id(self):
        existing_ids = sorted(self.products.keys())
        if not existing_ids:
            return '001'
        last_id = existing_ids[-1]
        next_id = int(last_id) + 1
        return f"{next_id:03d}"

    def resequence_product_ids(self):
        sorted_ids = sorted(self.products.keys())
        for i, product_id in enumerate(sorted_ids, 1):
            new_id = f"{i:03d}"
            self.products[product_id].product_id = new_id
        print("Product IDs have been re-sequenced.")
    
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

    def get_next_available_id(self):
        used_ids = set(self.products.keys()) - self.deleted_ids
        if not used_ids:
            return '001'
        all_ids = set([f"{i:03d}" for i in range(1, len(self.products) + 2)])
        available_ids = all_ids - used_ids
        return min(available_ids)


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
        while True:
            username = input("Enter username: ")
            password = input("Enter password: ")
            user = self.users.get(username)
            if user and user.password == password:
                self.logged_in_user = user
                print(f"Welcome, {username}!")
                break
            else:
                print("Invalid credentials. Try again.")

    def logout(self):
        self.logged_in_user = None
        print("Logged out successfully.")

    def show_main_menu(self):
        if self.logged_in_user.role == "Admin":
            self.admin_menu()
        elif self.logged_in_user.role == "User":
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

            if choice == '1':
                self.inventory.add_product()
            elif choice == '2':
                self.inventory.update_product()
            elif choice == '3':
                self.inventory.delete_product()
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

    def user_menu(self):
        while True:
            print("\nUser Menu")
            print("1. Place Order")
            print("2. View Orders")
            print("3. Remove Order")
            print("4. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.place_order()
            elif choice == '2':
                self.view_orders()
            elif choice == '3':
                self.remove_order()
            elif choice == '4':
                self.logout()
                break

    def place_order(self):
        print("\nPlace Order Menu")
        products_to_order = []
        while True:
            self.inventory.view_all_products()
            product_id = input("Enter product ID to order (or 'done' to finish, 'back' to cancel): ")
            if product_id.lower() == 'back':
                return

            if product_id.lower() == 'done':
                if not products_to_order:
                    print("You need to add at least one product to the order.")
                    continue
                print("Order finalized!")
                break

            quantity = input(f"Enter quantity for product {product_id}: ")
            if quantity.lower() == 'back':
                return
            try:
                quantity = int(quantity)
                if product_id in self.inventory.products and self.inventory.products[product_id].stock_quantity >= quantity:
                    products_to_order.append((product_id, quantity))
                    self.inventory.products[product_id].stock_quantity -= quantity
                    print(f"Added {quantity} of {product_id} to the order.")
                else:
                    print("Insufficient stock!")
            except ValueError:
                print("Invalid input for quantity.")
    
        if products_to_order:
            order_id = len(self.orders) + 1
            order = Order(order_id, self.logged_in_user.username, products_to_order)
            self.orders.append(order)
            print(f"Order placed successfully! {order}")

    def view_orders(self):
        if not self.orders:
            print("No orders placed.")
            return
        for order in self.orders:
            print(order)

    def remove_order(self):
        if not self.orders:
            print("No orders to remove.")
            return
        
        print("\nYour Orders:")
        for order in self.orders:
            print(order)

        order_id = int(input("Enter the order ID to remove: "))
        for order in self.orders:
            if order.order_id == order_id:
                print(f"Order {order_id} removed!")
                for product_id, quantity in order.products:
                    self.inventory.products[product_id].stock_quantity += quantity
                    print(f"Stock of {self.inventory.products[product_id].name} restored by {quantity}.")
                self.orders.remove(order)
                self.inventory.save_to_file()
                return

        print("Order ID not found.")

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

    def run(self):
        self.login()
        self.show_main_menu()


if __name__ == "__main__":
    ims = InventoryManagementSystem()
    ims.run()