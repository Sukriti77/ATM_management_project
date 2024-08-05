import sqlite3
import getpass
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests


class User:
    daily_withdrawal_limit = 40000
    total_daily_withdrawal = 0
    last_withdrawal_date = None
    def __init__(self, name, passkey, saving_balance, current_balance, unlock_id, card_number, saving_lock, current_lock):
        self.name = name
        self.passkey = passkey
        self.saving_balance = saving_balance
        self.current_balance = current_balance 
        self.unlock_id = unlock_id
        self.card_number = card_number 
        self.saving_lock = saving_lock
        self.current_lock = current_lock
        # new attribute to handle one day withdrawl limit
        self.user_daily_withdrawal_total = 0
        self.user_last_withdrawal_date = None


class Admin:
    def __init__(self, name, passkey, card_number):
        self.name = name
        self.passkey = passkey
        self.card_number = card_number

class Receipt:
    @staticmethod
    def generate_receipt(user, transaction_type, amount):
        # Customize the receipt format based on your requirements
        receipt_text = f"""
        Receipt
        -------------------------
        Date: {datetime.now()}
        User: {user.name}
        Transaction Type: {transaction_type}
        Amount: {amount} INR
        -------------------------
        Thank you for using our ATM!
        """
        return receipt_text

    @staticmethod
    def print_receipt(receipt_text):
        print(receipt_text)

class ATM:
    complaint_categories = ['Service Issue', 'Transaction Problem', 'Card Issue', 'Other']
    def __init__(self):
        self.conn = sqlite3.connect('atm_database.db')
        self.cursor = self.conn.cursor()
        self.users = []
        self.admin = None
        self.load_users()
        self.load_admin()
        self.load_atm_balance()

    def load_users(self):
        self.cursor.execute('SELECT * FROM users')
        rows = self.cursor.fetchall()
        for row in rows:
            user = User(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            self.users.append(user)

    def load_admin(self):
        self.cursor.execute('SELECT * FROM admin')
        row = self.cursor.fetchone()
        if row:
            self.admin = Admin(row[1], row[2], row[3])
    
    def load_atm_balance(self):
        self.cursor.execute('SELECT amount FROM atm_amount')
        row = self.cursor.fetchone()
        if row:
            ATM.amount= row[0]
    
    def user_login(self):
        user_card=input("Please enter your card number:")
        for user in self.users:
            if user.card_number==user_card:
                print()
                print("Logging into your account...")
                for i in range(10):
                    h=self.user_operations(user)
                    print("\n")
                    if i==8:
                        print("Session about to time out...")
                    if h==-1:
                        break
                print("Session timed out...")
                break
        else:
            print("User not found...")
            print("Please check your card number...")
    
    def admin_login(self):
        admin_card=input("Please enter your admin card number:")
        if self.admin and self.admin.card_number==admin_card:
            self.admin_operations()
        else:
            print("Admin not found...")
            print("Check your admin card number...")
    
    def ATM_Operations(self):
        print("                     .......Welcome to the ATM.......                           ")
        print("Choose from the following options:")
        print("1. Login into User account")
        print("2. Login into Admin account")
        print("3. Search for nearby ATMs")
        c=input("Enter your choice:")
        if c=='1':
            self.user_login()
        elif c=='2':
            self.admin_login()
        elif c=='3':
            location = '32.70265,74.9242 '  

            atms = self.get_nearby_atms(location)

            if atms:
                print("Nearby ATMs (under 5000 meters):")
                self.display_atm_info(atms)
            else:
                print("No ATMs found nearby.")

    def get_nearby_atms(self,location, radius=5000):
        overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Constructing an Overpass QL query to find ATMs within the specified radius
        overpass_query = f"""
            [out:json];
            (
                node["amenity"="atm"](around:{radius},{location});
                way["amenity"="atm"](around:{radius},{location});
                relation["amenity"="atm"](around:{radius},{location});
            );
            out;
        """

        params = {
            'data': overpass_query
        }

        response = requests.get(overpass_url, params=params)
        data = response.json()

        # Extracting relevant information from the response
        atms = []
        for element in data.get('elements', []):
            atm_info = {
                'name': element.get('tags', {}).get('name', 'N/A'),
                'lat': element.get('lat'),
                'lon': element.get('lon'),
            }
            atms.append(atm_info)

        return atms
    
    def display_atm_info(self,atms):
        for index, atm in enumerate(atms, start=1):
            print(f"{index}. {atm['name']}")
            print(f"   Location: Latitude {atm['lat']}, Longitude {atm['lon']}")
            print("------------------------")


    def admin_operations(self):
        print("WELCOME")
        print("Choose from the following options:")
        print("1. To deposit cash into the atm")
        print("2. To check the ATM balance")
        print("3. Change the PIN")
        print("4. Unlock an account")
        print("5. To view customer complaints")
        print()
        c=input("Enter your choice:")
        if c=='1':
            self.deposit_ATM_cash()
        elif c=='2':
            self.check_ATM_balance()
        elif c=='3':
            self.change_admin_pin()
        elif c=='4':
            self.unlock_account()
        elif c=='5':
            self.analyze_complaints()
    
    
    def check_admin_pin(self):
        for i in range(3):
            admin_pin = getpass.getpass(prompt="Enter admin PIN: ")
            if admin_pin == self.admin.passkey:
                print("Admin PIN accepted successfully.")
                return True
            else:
                print("Incorrect admin PIN. You can try again.")
    
        print("Too many incorrect attempts.")
        return False

    def deposit_ATM_cash(self):
        if self.check_admin_pin():
            print("Enter the amount you want to deposit in the ATM:")
            amount = int(input())
            if amount > 0:
                print("Processing your request...")
                self.update_atm_balance(amount)
                print("TRANSACTION SUCCESSFULL.")
            else:
                print("Invalid amount. Please enter a positive value for deposit.")
        else:
            print("Invalid admin PIN. Transaction cannot be processed.")

    def check_ATM_balance(self):
        if self.check_admin_pin():
            print(f"The ATM currently has an amount of {ATM.amount} INR")
        else:
            print("The request cannot be processed.")
    
    def change_admin_pin(self):
        if self.check_admin_pin():
            for i in range(5):
                new_pin = getpass.getpass("Enter your new pin: ")
                if new_pin == self.admin.passkey:
                    print("The pin is the same as the old pin. Enter a different pin.")
                else:
                    new_pin2 = getpass.getpass("Confirm your pin once more: ")
                    if new_pin2 == new_pin:
                        self.admin.passkey = new_pin  # Update the admin's pin
                        self.update_admin_pin(self.admin)
                        print("The admin pin has been updated successfully.")
                        break
                    else:
                        print("Pin confirmation failed. You may try again.")
            else:
                print("You have exceeded the trials. The pin could not be changed.")
        else:
            print("The request cannot be processed.")

    def update_admin_pin(self, admin):
        self.cursor.execute('''
            UPDATE admin
            SET passkey = ?
            WHERE card_number = ?
        ''', (admin.passkey, admin.card_number))
        self.conn.commit()

    def unlock_account(self):
        if self.check_admin_pin():
            print("Enter the card number of the account to unlock:")
            number = input()
            for user in self.users:
                if user.card_number == number:
                    if user.saving_lock == 1 or user.current_lock == 1:
                        user.saving_lock = 0
                        user.current_lock = 0
                        self.cursor.execute('''
                            UPDATE users
                            SET saving_lock = 0, current_lock = 0
                            WHERE card_number = ?
                        ''', (user.card_number,))
                        self.conn.commit()
                        print(f"User's account with card number {user.card_number} has been unlocked successfully.")
                    else:
                        print("User's account is not locked.")
                    break
            else:
                print("User not found.")
        else:
            print("The request cannot be processed.")


    def user_operations(self,user):
        print("Please choose from the following options:")
        print("1. To check balance")
        print("2. To withdraw cash")
        print("3. To deposit cash")
        print("4. To change pin")
        print("5. To submit a complaint")
        print("Or enter 0 to logout from your account...")
        print()
        c=input("Enter your choice:")
        if c=='1':
            self.check_balance(user)
            
        elif c=='2':
            self.withdraw_cash(user)
            
        elif c=='3':
            self.deposit_cash(user)
            
        elif c=='4':
            self.change_pin(user)

        elif c=='5':
            self.submit_complaint(user)

        elif c=='0':
            return -1
    
    def check_balance(self,user):
        account=self.account_selection()
        if account==1:
            print(f"The saving account currently has {user.saving_balance} INR")
        elif account==0:
            print(f"The current account has {user.current_balance} INR")
    
    def account_selection(self):
        print()
        print("Choose from the following:")
        print("1. Saving Account")
        print("2. Current Account")
        c=input("Choose your account:")
        if c=='1':
            return 1
        elif c=='2':
            return 0
    
    def withdraw_cash(self, user):
        account_type = self.account_selection()
        
        if account_type == 1:  # Saving account withdrawal
            d=self.check_savings_locked_account(user)
            if d==0: # account is unlocked
                if self.check_user_pin(user,account_type):
                    self.withdraw_savings(user,account_type)
                else:
                    print("Cannot proceed with the transaction.")
            else:
                print("Cannot proceed with the transaction. Saving account is locked.")
            
        elif account_type == 0:  # Current account withdrawal
            d= self.check_current_locked_account(user)
            if d==0: # account is unlocked
                if self.check_user_pin(user,account_type):
                    self.withdraw_current(user,account_type)
                else:
                    print("Cannot proceed with the transaction.")
            else:
                print("Cannot proceed with the transaction. Current account is locked.")
            
    def check_user_pin(self, user,account_type):
        for i in range(3):
            print("Please enter your PIN under the password section below")
            pin = getpass.getpass()
            if pin == user.passkey:
                print("PIN accepted successfully.")
                return True
            else:
                print("Incorrect PIN. You can try again.")
    
        print("Your account has been locked. Contact the admin to resolve this issue.")
        self.lock_account(user,account_type)
        return False

    def lock_account(self, user,account_type):
        if account_type == 1:
            user.saving_lock = 1
            self.update_user_lock_status(user,account_type)
        else:
            user.current_lock = 1
            self.update_user_lock_status(user,account_type)

    def update_user_lock_status(self, user,account_type):
        if account_type == 1:
            self.cursor.execute('''
                UPDATE users
                SET saving_lock = 1
                WHERE card_number = ?
            ''', (user.card_number,))
        else:
            self.cursor.execute('''
                UPDATE users
                SET current_lock = 1
                WHERE card_number = ?
            ''', (user.card_number,))
        self.conn.commit()

    def check_savings_locked_account(self, user):
        if user.saving_lock == 1:
            return 1
        return 0

    def check_current_locked_account(self, user):
        if user.current_lock == 1:
            return 1
        return 0

    # Inside the withdraw_savings method
    def withdraw_savings(self, user, account_type):
        amount = int(input("Enter the amount to withdraw from savings account: "))

    # Check if the withdrawal amount exceeds the daily limit
        if amount > User.daily_withdrawal_limit:
            print("The withdrawal amount exceeds the daily limit. Transaction cannot be processed.")
            return

    # Check if the user has reached the daily withdrawal limit
        today = datetime.now().date()
        if User.last_withdrawal_date != today:
            User.total_daily_withdrawal = 0  # Reset the daily withdrawal total if it's a new day

    # Check if the total withdrawal amount for the day will exceed the limit
        if User.total_daily_withdrawal + amount > User.daily_withdrawal_limit:
            print("The withdrawal exceeds the daily limit. Transaction cannot be processed.")
            return

    # Continue with the existing logic...
        if amount > 20000:
            print("The amount exceeds the withdrawal limits.")
            print("The transaction cannot be processed.")
        elif user.saving_balance < amount:
            print("Insufficient funds in the saving account.")
        elif user.saving_balance - amount <= 5000:
            print("The process is being terminated due to insufficient funds.")
        else:
            print("Your transaction is processed.")
            c = input("Enter 0 to cancel this transaction or 1 to continue: ")
            if c == '0':
                print("Terminating the process.")
            else:
            # Update the total daily withdrawal and last withdrawal date
                User.total_daily_withdrawal += amount
                User.last_withdrawal_date = today

            # Update user-specific daily withdrawal total and last withdrawal date
                user.user_daily_withdrawal_total += amount
                user.user_last_withdrawal_date = today

                user.saving_balance -= amount
                self.update_user_balance(user, account_type)
                self.update_atm_balance(-amount)
                print(f"Withdrawal of {amount} INR from savings account successful.")
            # Generate receipt and prompt user
                receipt_text = Receipt.generate_receipt(user, "Withdrawal (Savings)", amount)
                print(receipt_text)
                


    def withdraw_current(self, user,account_type):
        amount = int(input("Enter the amount to withdraw from current account: "))
        if user.current_balance >= amount:
            c=input("Enter o to cancel this transaction or 1 to continue:")
            if c == '0':
                print("Terminating the process.")
            else:
                user.current_balance -= amount
                self.update_user_balance(user,account_type)
                self.update_atm_balance(-amount)
                print(f"Withdrawal of {amount} INR from current account successful.")
                 # Generate receipt and prompt user
                receipt_text = Receipt.generate_receipt(user, "Withdrawal (Current)", amount)
                print(receipt_text)

        else:
            print("Insufficient funds in the current account.")

    def update_user_balance(self, user,account_type):
        if account_type == 1:
            self.cursor.execute('''
            UPDATE users
            SET saving_balance = ?
            WHERE card_number = ?
            ''', (user.saving_balance, user.card_number))
        else:
            self.cursor.execute('''
            UPDATE users
            SET current_balance = ?
            WHERE card_number = ?
            ''', (user.current_balance, user.card_number))
        self.conn.commit()

    def update_atm_balance(self, amount):
        
        query = '''
                UPDATE atm_amount
                SET amount = amount + ?
            '''
        self.cursor.execute(query, (amount,))
        self.conn.commit()
            
        

    
    def deposit_cash(self, user):
        c = self.account_selection()
    
        if c == 0:
            d=self.check_current_locked_account(user)
            if d==0: #the account is unlocked
                self.deposit_to_current(user,c)
            else:
                print("Cannot proceed with the transaction. Current account is locked.")
            
        elif c == 1:
            d=self.check_savings_locked_account(user)
            if d==0: #the account is unlocked
                self.deposit_to_savings(user,c)
            else:
                print("Cannot proceed with the transaction. Savings account is locked.")
            
        else:
            print("Invalid account selection.")

    
    def deposit_to_savings(self, user,account_type):
        if self.check_user_pin(user,account_type):
            amount = int(input("Enter the amount to deposit to savings account: "))
            c=input("Enter 0 to cancel this transaction or 1 to continue:")
            if c=='1':
                print(f"Saving account balance before deposit: {user.saving_balance} INR")
                print(f"Depositing {amount} INR to saving account.")
                # depositing the amount
                user.saving_balance += amount
                print(f"Saving account balance after deposit: {user.saving_balance} INR")
                self.update_user_balance(user,account_type)
                self.update_atm_balance(amount)
                print("The transaction request has been processed successfully.")
                 # Generate receipt and prompt user
                receipt_text = Receipt.generate_receipt(user, "Deposit (Savings)", amount)
                print(receipt_text)

            elif c=='0':
                print("Cancelling this transaction")
        else:
            print("Cannot proceed with the transaction. Incorrect PIN entered.")

    def deposit_to_current(self, user,account_type):
        if self.check_user_pin(user,account_type):
            amount = int(input("Enter the amount to deposit to your current account: "))
            c=input("Enter 0 to cancel this transaction or 1 to continue:")
            if c=='1':
                print(f"Current account balance before deposit: {user.current_balance} INR")
                print(f"Depositing {amount} INR to current account.")
                user.current_balance += amount
                print(f"Current account balance after deposit: {user.current_balance} INR")
                self.update_user_balance(user,account_type)
                self.update_atm_balance(amount)
                print("The transaction request has been processed successfully.")
                 # Generate receipt and prompt user
                receipt_text = Receipt.generate_receipt(user, "Deposit (Current)", amount)
                print(receipt_text)

            elif c=='0':
                print("The transaction has been cancelled.")
        else:
                print("Cannot proceed with the transaction. Incorrect PIN entered.")

    def change_pin(self, user):
        if self.pin_input(user):
            print("Enter your new pin under the password section:")
            for i in range(5):
                new_pin = getpass.getpass()
                if new_pin != user.passkey:
                    print("Confirm your pin once again:")
                    new_pin2 = getpass.getpass()
                    if new_pin == new_pin2:
                        print("Your pin has been updated successfully.")
                        user.passkey = new_pin  # Update the user's pin
                        self.update_user_pin(user)
                        
                        break
                    else:
                        print("Pin confirmation failed.")
                        print("You may try again.")
                else:
                    print("The new pin is the same as the old pin. Enter a different pin.")
            else:
                print("You have exceeded the trials. The pin could not be changed.")
        else:
            print("Cannot proceed with the transaction. Incorrect PIN entered.")
    
    def pin_input(self, user):
        print("Enter the pin under the password section below")
        pin = getpass.getpass()
        if pin == user.passkey:
            return True
        else:
            return False
    
    
    def submit_complaint(self, user):
        # Get user input for complaint details
        card_number = user.card_number

        # Display complaint categories for the user to choose
        print("Choose a complaint category:")
        for i, category in enumerate(self.complaint_categories, 1):
            print(f"{i}. {category}")

        # Get user choice
        category_choice = int(input("Enter the number corresponding to the complaint category: "))
        if 1 <= category_choice <= len(self.complaint_categories):
            complaint_type = self.complaint_categories[category_choice - 1]
        else:
            print("Invalid choice. Defaulting to 'Other'.")
            complaint_type = 'Other'

        content = input("Enter the complaint content: ")

        # Load existing complaints from the Excel file if it exists
        try:
            df = pd.read_excel('complaints.xlsx')
        except FileNotFoundError:
            # If the file doesn't exist, create a new DataFrame
            df = pd.DataFrame(columns=['Card Number', 'Complaint Type', 'Content', 'Timestamp'])

        # Create a new row for the complaint
        new_complaint = pd.DataFrame([[card_number, complaint_type, content, datetime.now()]],
                                      columns=['Card Number', 'Complaint Type', 'Content', 'Timestamp'])

        # Concatenate only if the existing DataFrame is not empty
        if not df.empty:
            df = pd.concat([df, new_complaint], ignore_index=True)
        else:
            df = new_complaint

        # Save the DataFrame to the Excel file
        df.to_excel('complaints.xlsx', index=False)
        print("Complaint submitted successfully.")

    def analyze_complaints(self):
    # Load existing complaints from the Excel file if it exists
        try:
            df = pd.read_excel('complaints.xlsx')
        except FileNotFoundError:
            print("No complaints data found.")
            return

    # Filter complaints from the past seven days
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_complaints = df[df['Timestamp'] >= seven_days_ago]

        if recent_complaints.empty:
            print("No complaints recorded in the past seven days.")
        else:
            # Display recent complaints
            print("Complaints recorded in the past seven days:")
            print(recent_complaints)

        # Analyze and display the most frequent complaint type
            most_frequent_complaint = recent_complaints['Complaint Type'].mode().iloc[0]
            print(f"\nMost frequent complaint type: {most_frequent_complaint}")

        # Count complaint types
            complaint_type_counts = recent_complaints['Complaint Type'].value_counts()

        # Plot a bar chart of complaint types using Seaborn
            import seaborn as sns
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(x=complaint_type_counts.index, y=complaint_type_counts.values, hue=complaint_type_counts.index, palette="viridis", dodge=False)
            if ax.legend_:
                ax.legend_.remove()  # To remove the legend, as it's not necessary for this plot

            ax.set(xlabel='Complaint Type', ylabel='Count', title='Complaint Types')
            plt.xticks(rotation=45, ha='right')  # Adjust x-axis labels for better readability
            plt.tight_layout()  # Ensure all elements are visible
            plt.show()

    def update_user_pin(self, user):
        self.cursor.execute('UPDATE users SET passkey = ? WHERE card_number = ?', (user.passkey, user.card_number))
        self.conn.commit()

    def __del__(self):
        self.conn.close()  

# Calling the ATM:
while(True):
    atm_instance = ATM()
    print("\n\n\n\n\n\n")
    atm_instance.ATM_Operations()  
