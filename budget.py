import time
from tabulate import tabulate

leftover = 0

expense_data = []
tax_bracket = {
    9875: 0.10,
    40125: 0.12,
    85525: 0.22,
    163300: 0.24,
    207350: 0.32,
    518400: 0.35,
    518401: 0.37
}

def calculate_tax(income):
    tax = 0
    previous_bracket = 0
    
    for bracket, rate in tax_bracket.items():
        if income > bracket:
            taxable_in_bracket = bracket - previous_bracket
            tax += taxable_in_bracket * rate
            previous_bracket = bracket
        else:
            taxable_in_bracket = income - previous_bracket
            tax += taxable_in_bracket * rate
            return tax
    return tax

def run_budget_calc():
    try:
        yearly_income = float(input("Enter total yearly income: $"))
        total_tax = calculate_tax(yearly_income)
        net_income = yearly_income - total_tax
        monthly_net = net_income / 12

        print(f"\nMonthly Take-Home after Tax: ${monthly_net:,.2f}")
        expense_data.clear()
        adding = True
        while adding:
            name = input("Enter expense name (or 'done' to finish): ")
            if name.lower() == 'done':
                adding = False
            else:
                cost = float(input(f"Enter monthly cost for {name}: $"))
                expense_data.append([name, cost])
        
        total_spent = 0
        for item in expense_data:
            total_spent += item[1]
            
        return monthly_net - total_spent

    except ValueError:
        print("Error: Please enter numeric values only.")
        return 0

def main():
    global leftover 
    while True:
        print("\n===== PERSONAL FINANCE TRACKER =====")
        print("1. Calculate Monthly Budget")
        print("2. View Current Budget Summary")
        print("3. Future Investment Projection")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")

        if choice == "1":
            leftover = run_budget_calc()
            print(f"\nSuccess! Monthly Leftover: ${leftover:,.2f}")

        elif choice == "2":
            if not expense_data and leftover == 0:
                print("\n[!] No budget data found. Please run Option 1 first.")
            else:
                print("\n--- Monthly Budget Overview ---")
                display_list = []
                for item in expense_data:
                    display_list.append([item[0], f"${item[1]:,.2f}"])
                
                display_list.append(["---", "---"])
                display_list.append(["LEFTOVER", f"${leftover:,.2f}"])
                print(tabulate(display_list, headers=["Category", "Amount"], tablefmt="simple"))

        elif choice == "3":
            if leftover <= 0:
                print("\n[!] You need a positive leftover balance to simulate investments.")
                continue
                
            try:
                monthly_inv = float(input(f"Monthly investment (Max ${leftover:,.2f}): $"))
                if monthly_inv > leftover:
                    print("Warning: That exceeds your monthly leftover!")
                    continue
                
                rate = float(input("Expected annual return % (e.g., 7): ")) / 100
                years = int(input("Years to grow: "))
                
                m_rate = rate / 12
                months = years * 12
                fv = monthly_inv * (((1 + m_rate)**months - 1) / m_rate)
                
                print(f"\nIn {years} years, your contributions could grow to: ${fv:,.2f}")
            except ValueError:
                print("Invalid input.")

        elif choice == "4":
            print("Goodbye!")
            break
        time.sleep(2)

if __name__ == "__main__":
    main()