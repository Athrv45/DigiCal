"""
GUI for DigiCal Business Calculator
Tkinter-based interface optimized for Raspberry Pi display
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import config
from calculator import Calculator
from database import Database
from transaction_manager import TransactionManager
from history_manager import HistoryManager
from graph_generator import GraphGenerator
from handler_manager import HandlerManager

class DigiCalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_NAME)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.BG_COLOR)
        
        # Initialize components
        self.db = Database()
        self.calculator = Calculator()
        self.transaction_manager = TransactionManager(self.db)
        self.history_manager = HistoryManager(self.db)
        self.graph_generator = GraphGenerator(self.transaction_manager)
        self.handler_manager = HandlerManager(self.db)
        
        # Current mode
        self.current_mode = "calculator"  # calculator, sales, expense, history, graphs
        
        # Create UI
        self.create_widgets()
        self.show_calculator_mode()
    
    def create_widgets(self):
        """Create main UI components"""
        # Top bar with mode buttons and handler dropdown
        self.top_frame = tk.Frame(self.root, bg=config.BG_COLOR, height=50)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side: mode buttons
        mode_frame = tk.Frame(self.top_frame, bg=config.BG_COLOR)
        mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        mode_buttons = [
            ("Calculator", "calculator"),
            ("Sales", "sales"),
            ("Expense", "expense"),
            ("History", "history"),
            ("Graphs", "graphs")
        ]
        
        for text, mode in mode_buttons:
            btn = tk.Button(
                mode_frame,
                text=text,
                font=("Arial", 10),
                bg=config.MODE_BG,
                fg=config.BUTTON_FG,
                command=lambda m=mode: self.switch_mode(m),
                relief=tk.RAISED,
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Right side: handler dropdown
        handler_frame = tk.Frame(self.top_frame, bg=config.BG_COLOR)
        handler_frame.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(handler_frame, text="Handler:", font=("Arial", 10), bg=config.BG_COLOR, fg="white").pack(side=tk.LEFT, padx=5)
        
        self.handler_var = tk.StringVar()
        self.handler_dropdown = ttk.Combobox(
            handler_frame,
            textvariable=self.handler_var,
            font=("Arial", 10),
            width=15,
            state="readonly"
        )
        self.handler_dropdown.pack(side=tk.LEFT)
        self.handler_dropdown.bind('<<ComboboxSelected>>', self.on_handler_selected)
        self.update_handler_dropdown()
        
        # Display area
        self.display_frame = tk.Frame(self.root, bg=config.DISPLAY_BG, height=80)
        self.display_frame.pack(fill=tk.X, padx=10, pady=5)
        self.display_frame.pack_propagate(False)
        
        self.display = tk.Label(
            self.display_frame,
            text="0",
            font=config.DISPLAY_FONT,
            bg=config.DISPLAY_BG,
            fg=config.DISPLAY_FG,
            anchor=tk.E,
            padx=10
        )
        self.display.pack(fill=tk.BOTH, expand=True)
        
        # Content area (will change based on mode)
        self.content_frame = tk.Frame(self.root, bg=config.BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def clear_content_frame(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def switch_mode(self, mode):
        """Switch between different modes"""
        self.current_mode = mode
        self.clear_content_frame()
        
        if mode == "calculator":
            self.show_calculator_mode()
        elif mode == "sales":
            self.show_sales_mode()
        elif mode == "expense":
            self.show_expense_mode()
        elif mode == "history":
            self.show_history_mode()
        elif mode == "graphs":
            self.show_graphs_mode()
    
    def show_calculator_mode(self):
        """Show calculator interface"""
        self.update_display(self.calculator.get_expression())
        
        # Button layout
        buttons = [
            ['MC', 'MR', 'M+', 'M-'],
            ['7', '8', '9', '÷'],
            ['4', '5', '6', '×'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+'],
            ['C', 'CE', '%', '']
        ]
        
        for row_idx, row in enumerate(buttons):
            row_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
            row_frame.pack(fill=tk.X, pady=2)
            
            for btn_text in row:
                if btn_text == '':
                    continue
                
                # Determine button color
                if btn_text in ['÷', '×', '-', '+']:
                    bg_color = config.OPERATOR_BG
                elif btn_text == '=':
                    bg_color = config.EQUALS_BG
                elif btn_text in ['MC', 'MR', 'M+', 'M-', 'C', 'CE', '%']:
                    bg_color = config.MODE_BG
                else:
                    bg_color = config.BUTTON_BG
                
                btn = tk.Button(
                    row_frame,
                    text=btn_text,
                    font=config.BUTTON_FONT,
                    bg=bg_color,
                    fg=config.BUTTON_FG,
                    activebackground=config.BUTTON_ACTIVE,
                    command=lambda t=btn_text: self.calculator_button_click(t),
                    relief=tk.RAISED,
                    bd=3
                )
                btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2)
        
        # Bind keyboard
        self.root.bind('<Key>', self.on_key_press)
    
    def calculator_button_click(self, button):
        """Handle calculator button clicks"""
        if button in '0123456789.':
            self.calculator.add_digit(button)
            self.update_display(self.calculator.get_expression())
        elif button in '+-×÷':
            self.calculator.add_operator(button)
            self.update_display(self.calculator.get_expression())
        elif button == '=':
            expression = self.calculator.get_expression()
            result = self.calculator.evaluate()
            self.update_display(result)
            if not result.startswith("Error"):
                # Calculate handler incentive
                handler = self.handler_manager.get_current_handler()
                handler_id = handler['id'] if handler else None
                handler_incentive = self.handler_manager.calculate_incentive(result)
                
                # Save calculation with handler info
                self.db.add_calculation(expression, result, handler_id, handler_incentive)
                
                # Show transaction categorization dialog
                self.show_transaction_dialog(result)
        elif button == 'C':
            self.calculator.clear()
            self.update_display("0")
        elif button == 'CE':
            self.calculator.clear_entry()
            self.update_display(self.calculator.get_expression())
        elif button == '%':
            self.calculator.add_digit('%')
            self.update_display(self.calculator.get_expression())
        elif button == 'MC':
            self.calculator.clear_memory()
            messagebox.showinfo("Memory", "Memory cleared")
        elif button == 'MR':
            mem_value = self.calculator.recall_memory()
            self.calculator.set_expression(mem_value)
            self.update_display(mem_value)
        elif button == 'M+':
            try:
                value = float(self.display.cget("text"))
                self.calculator.add_to_memory(value)
                messagebox.showinfo("Memory", f"Added {value} to memory")
            except:
                pass
        elif button == 'M-':
            try:
                value = float(self.display.cget("text"))
                self.calculator.subtract_from_memory(value)
                messagebox.showinfo("Memory", f"Subtracted {value} from memory")
            except:
                pass
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        if self.current_mode != "calculator":
            return
        
        key = event.char
        if key in '0123456789.':
            self.calculator_button_click(key)
        elif key in '+-':
            self.calculator_button_click(key)
        elif key == '*':
            self.calculator_button_click('×')
        elif key == '/':
            self.calculator_button_click('÷')
        elif key in ['\r', '\n', '=']:
            self.calculator_button_click('=')
        elif event.keysym == 'BackSpace':
            self.calculator_button_click('CE')
        elif event.keysym == 'Escape':
            self.calculator_button_click('C')
    
    def show_sales_mode(self):
        """Show sales entry interface"""
        self.update_display("Add Sales Transaction")
        
        # Input form
        form_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Amount:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=0, column=0, sticky=tk.W, pady=5)
        amount_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        amount_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Category:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        categories = self.transaction_manager.get_sales_categories()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, values=categories, font=config.LABEL_FONT, width=18)
        category_combo.grid(row=1, column=1, pady=5, padx=10)
        # Set default to "Product Sales" if available
        if "Product Sales" in categories:
            category_var.set("Product Sales")
        elif categories:
            category_combo.current(0)
        
        tk.Label(form_frame, text="Description:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        desc_entry.grid(row=2, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Payment:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=3, column=0, sticky=tk.W, pady=5)
        payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(form_frame, textvariable=payment_var, values=config.PAYMENT_METHODS, font=config.LABEL_FONT, width=18, state="readonly")
        payment_combo.grid(row=3, column=1, pady=5, padx=10)
        
        def add_sale():
            try:
                amount = float(amount_entry.get())
                category = category_var.get()
                description = desc_entry.get()
                
                if not category:
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                payment_method = payment_var.get()
                # Get current handler ID
                handler_id = None
                current_handler = self.handler_manager.get_current_handler()
                if current_handler:
                    handler_id = current_handler['id']
                
                self.transaction_manager.add_sale(amount, category, description, payment_method, handler_id)
                messagebox.showinfo("Success", f"Sales transaction of ₹{amount:.2f} added")
                
                # Clear form
                amount_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                
                # Update summary
                self.show_transaction_summary('sales')
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        tk.Button(
            form_frame,
            text="Add Sale",
            font=config.BUTTON_FONT,
            bg=config.EQUALS_BG,
            fg=config.BUTTON_FG,
            command=add_sale,
            width=20,
            height=2
        ).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Summary
        self.show_transaction_summary('sales')
    
    def show_expense_mode(self):
        """Show expense entry interface"""
        self.update_display("Add Expense Transaction")
        
        # Input form
        form_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Amount:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=0, column=0, sticky=tk.W, pady=5)
        amount_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        amount_entry.grid(row=0, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Category:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        categories = self.transaction_manager.get_expense_categories()
        category_combo = ttk.Combobox(form_frame, textvariable=category_var, values=categories, font=config.LABEL_FONT, width=18)
        category_combo.grid(row=1, column=1, pady=5, padx=10)
        # Set default to "Supplies" if available
        if "Supplies" in categories:
            category_var.set("Supplies")
        elif categories:
            category_combo.current(0)
        
        tk.Label(form_frame, text="Description:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=2, column=0, sticky=tk.W, pady=5)
        desc_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        desc_entry.grid(row=2, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Payment:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=3, column=0, sticky=tk.W, pady=5)
        payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(form_frame, textvariable=payment_var, values=config.PAYMENT_METHODS, font=config.LABEL_FONT, width=18, state="readonly")
        payment_combo.grid(row=3, column=1, pady=5, padx=10)
        
        def add_expense():
            try:
                amount = float(amount_entry.get())
                category = category_var.get()
                description = desc_entry.get()
                
                if not category:
                    messagebox.showerror("Error", "Please select a category")
                    return
                
                payment_method = payment_var.get()
                # Get current handler ID
                handler_id = None
                current_handler = self.handler_manager.get_current_handler()
                if current_handler:
                    handler_id = current_handler['id']
                
                self.transaction_manager.add_expense(amount, category, description, payment_method, handler_id)
                messagebox.showinfo("Success", f"Expense transaction of ₹{amount:.2f} added")
                
                # Clear form
                amount_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                
                # Update summary
                self.show_transaction_summary('expense')
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        tk.Button(
            form_frame,
            text="Add Expense",
            font=config.BUTTON_FONT,
            bg=config.OPERATOR_BG,
            fg=config.BUTTON_FG,
            command=add_expense,
            width=20,
            height=2
        ).grid(row=4, column=0, columnspan=2, pady=20)
        
        # Summary
        self.show_transaction_summary('expense')
    
    def show_transaction_summary(self, trans_type):
        """Show transaction summary"""
        summary_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
        summary_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Get summaries
        daily = self.transaction_manager.get_daily_summary()
        weekly = self.transaction_manager.get_weekly_summary()
        monthly = self.transaction_manager.get_monthly_summary()
        
        if trans_type == 'sales':
            daily_val = daily['total_sales']
            weekly_val = weekly['total_sales']
            monthly_val = monthly['total_sales']
            title = "Sales Summary"
        else:
            daily_val = daily['total_expenses']
            weekly_val = weekly['total_expenses']
            monthly_val = monthly['total_expenses']
            title = "Expense Summary"
        
        tk.Label(
            summary_frame,
            text=title,
            font=("Arial", 14, "bold"),
            bg=config.BG_COLOR,
            fg="white"
        ).pack(pady=5)
        
        info_text = f"Today: ₹{daily_val:.2f}\nThis Week: ₹{weekly_val:.2f}\nThis Month: ₹{monthly_val:.2f}"
        tk.Label(
            summary_frame,
            text=info_text,
            font=config.LABEL_FONT,
            bg=config.BG_COLOR,
            fg="white",
            justify=tk.LEFT
        ).pack(pady=5)
    
    def show_history_mode(self):
        """Show history interface"""
        self.update_display("Transaction & Calculation History")
        
        # Tabs for different histories
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Calculation history tab
        calc_frame = tk.Frame(notebook, bg=config.BG_COLOR)
        notebook.add(calc_frame, text="Calculations")
        
        calc_list = tk.Listbox(calc_frame, font=("Arial", 10), bg=config.DISPLAY_BG, fg=config.DISPLAY_FG)
        calc_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        calc_history = self.history_manager.format_calculation_history()
        for item in calc_history:
            calc_list.insert(tk.END, item)
        
        # Transaction history tab
        trans_frame = tk.Frame(notebook, bg=config.BG_COLOR)
        notebook.add(trans_frame, text="Transactions")
        
        trans_list = tk.Listbox(trans_frame, font=("Arial", 10), bg=config.DISPLAY_BG, fg=config.DISPLAY_FG)
        trans_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        trans_history = self.history_manager.format_transaction_history()
        for item in trans_history:
            trans_list.insert(tk.END, item)
    
    def show_graphs_mode(self):
        """Show graphs interface"""
        self.update_display("Sales & Expense Analytics")
        
        # Graph selection buttons
        btn_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
        btn_frame.pack(pady=10)
        
        graph_buttons = [
            ("Weekly Chart", self.show_weekly_graph),
            ("Monthly Trend", self.show_monthly_graph),
            ("Sales Breakdown", lambda: self.show_category_pie('sales')),
            ("Expense Breakdown", lambda: self.show_category_pie('expense')),
            ("Profit Trend", self.show_profit_graph),
            ("Handler Performance", self.show_handler_performance)
        ]
        
        for text, command in graph_buttons:
            tk.Button(
                btn_frame,
                text=text,
                font=("Arial", 10),
                bg=config.MODE_BG,
                fg=config.BUTTON_FG,
                command=command,
                width=15
            ).pack(side=tk.LEFT, padx=5)
        
        # Graph display area
        self.graph_frame = tk.Frame(self.content_frame, bg=config.BG_COLOR)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Show weekly graph by default
        self.show_weekly_graph()
    
    def clear_graph_frame(self):
        """Clear graph display"""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
    
    def show_weekly_graph(self):
        """Display weekly graph"""
        self.clear_graph_frame()
        fig = self.graph_generator.create_weekly_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_monthly_graph(self):
        """Display monthly graph"""
        self.clear_graph_frame()
        fig = self.graph_generator.create_monthly_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_category_pie(self, trans_type):
        """Display category pie chart"""
        self.clear_graph_frame()
        fig = self.graph_generator.create_category_pie_chart(trans_type)
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_profit_graph(self):
        """Display profit trend graph"""
        self.clear_graph_frame()
        fig = self.graph_generator.create_profit_trend_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_display(self, text):
        """Update the display"""
        self.display.config(text=str(text))
    
    def show_transaction_dialog(self, amount):
        """Show dialog to categorize calculation as transaction"""
        try:
            amount_val = float(amount)
        except:
            return  # Invalid amount, skip dialog
        
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Save as Transaction?")
        dialog.geometry("400x300")
        dialog.configure(bg=config.BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(
            dialog,
            text=f"Amount: ₹{amount_val:.2f}",
            font=("Arial", 16, "bold"),
            bg=config.BG_COLOR,
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Save this as a transaction?",
            font=config.LABEL_FONT,
            bg=config.BG_COLOR,
            fg="white"
        ).pack(pady=5)
        
        # Payment method selection
        payment_frame = tk.Frame(dialog, bg=config.BG_COLOR)
        payment_frame.pack(pady=10)
        
        tk.Label(
            payment_frame,
            text="Payment Method:",
            font=config.LABEL_FONT,
            bg=config.BG_COLOR,
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        payment_var = tk.StringVar(value="Cash")
        payment_combo = ttk.Combobox(
            payment_frame,
            textvariable=payment_var,
            values=config.PAYMENT_METHODS,
            font=config.LABEL_FONT,
            width=10,
            state="readonly"
        )
        payment_combo.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=config.BG_COLOR)
        button_frame.pack(pady=20)
        
        def save_as_sale():
            payment_method = payment_var.get()
            categories = self.transaction_manager.get_sales_categories()
            # Default to "Product Sales" if available, otherwise first category
            category = "Product Sales" if "Product Sales" in categories else (categories[0] if categories else "Sales")
            
            # Get current handler ID
            handler_id = None
            current_handler = self.handler_manager.get_current_handler()
            if current_handler:
                handler_id = current_handler['id']
            
            self.transaction_manager.add_sale(amount_val, category, f"From calculation: {amount}", payment_method, handler_id)
            messagebox.showinfo("Success", f"Saved as Sales: ₹{amount_val:.2f} [{payment_method}]")
            dialog.destroy()
        
        def save_as_expense():
            payment_method = payment_var.get()
            categories = self.transaction_manager.get_expense_categories()
            # Default to "Supplies" if available, otherwise first category
            category = "Supplies" if "Supplies" in categories else (categories[0] if categories else "Expense")
            
            # Get current handler ID
            handler_id = None
            current_handler = self.handler_manager.get_current_handler()
            if current_handler:
                handler_id = current_handler['id']
            
            self.transaction_manager.add_expense(amount_val, category, f"From calculation: {amount}", payment_method, handler_id)
            messagebox.showinfo("Success", f"Saved as Expense: ₹{amount_val:.2f} [{payment_method}]")
            dialog.destroy()
        
        def discard():
            dialog.destroy()
        
        tk.Button(
            button_frame,
            text="Sales",
            font=config.BUTTON_FONT,
            bg=config.EQUALS_BG,
            fg=config.BUTTON_FG,
            command=save_as_sale,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Expense",
            font=config.BUTTON_FONT,
            bg=config.OPERATOR_BG,
            fg=config.BUTTON_FG,
            command=save_as_expense,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Discard",
            font=config.BUTTON_FONT,
            bg=config.MODE_BG,
            fg=config.BUTTON_FG,
            command=discard,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=5)
    
    def update_handler_dropdown(self):
        """Update handler dropdown with current handlers"""
        handlers = self.handler_manager.get_handler_list()
        handler_names = ["+ Create New Handler"] + [h[1] for h in handlers]
        self.handler_dropdown['values'] = handler_names
        
        # Set current handler
        current_handler = self.handler_manager.get_current_handler()
        if current_handler:
            self.handler_var.set(current_handler['name'])
        elif handler_names:
            self.handler_var.set(handler_names[0])
    
    def on_handler_selected(self, event=None):
        """Handle handler selection from dropdown"""
        selected = self.handler_var.get()
        
        if selected == "+ Create New Handler":
            self.show_create_handler_dialog()
        else:
            # Find and set the selected handler
            handlers = self.handler_manager.get_handler_list()
            for h_id, h_name, h_incentive, h_type in handlers:
                if h_name == selected:
                    self.handler_manager.set_current_handler(h_id)
                    break
    
    def show_create_handler_dialog(self):
        """Show dialog to create a new handler"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Handler")
        dialog.geometry("450x350")
        dialog.configure(bg=config.BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(
            dialog,
            text="Create New Handler",
            font=("Arial", 16, "bold"),
            bg=config.BG_COLOR,
            fg="white"
        ).pack(pady=15)
        
        # Form
        form_frame = tk.Frame(dialog, bg=config.BG_COLOR)
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Handler Name:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=0, column=0, sticky=tk.W, pady=10, padx=10)
        name_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Incentive Type Selection
        tk.Label(form_frame, text="Incentive Type:", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white").grid(row=1, column=0, sticky=tk.W, pady=10, padx=10)
        
        incentive_type_var = tk.StringVar(value="percentage")
        type_frame = tk.Frame(form_frame, bg=config.BG_COLOR)
        type_frame.grid(row=1, column=1, pady=10, padx=10, sticky=tk.W)
        
        tk.Radiobutton(
            type_frame,
            text="Percentage (%)",
            variable=incentive_type_var,
            value="percentage",
            font=config.LABEL_FONT,
            bg=config.BG_COLOR,
            fg="white",
            selectcolor=config.MODE_BG,
            activebackground=config.BG_COLOR,
            activeforeground="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            type_frame,
            text="Fixed Amount",
            variable=incentive_type_var,
            value="fixed",
            font=config.LABEL_FONT,
            bg=config.BG_COLOR,
            fg="white",
            selectcolor=config.MODE_BG,
            activebackground=config.BG_COLOR,
            activeforeground="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Incentive Value
        incentive_label = tk.Label(form_frame, text="Incentive (%):", font=config.LABEL_FONT, bg=config.BG_COLOR, fg="white")
        incentive_label.grid(row=2, column=0, sticky=tk.W, pady=10, padx=10)
        incentive_entry = tk.Entry(form_frame, font=config.LABEL_FONT, width=20)
        incentive_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Update label when incentive type changes
        def update_incentive_label(*args):
            if incentive_type_var.get() == "percentage":
                incentive_label.config(text="Incentive (%):")
            else:
                incentive_label.config(text="Incentive (Fixed):")
        
        incentive_type_var.trace('w', update_incentive_label)
        
        def create_handler():
            name = name_entry.get().strip()
            incentive_str = incentive_entry.get().strip()
            incentive_type = incentive_type_var.get()
            
            if not name:
                messagebox.showerror("Error", "Please enter a handler name")
                return
            
            try:
                incentive = float(incentive_str)
                if incentive < 0:
                    messagebox.showerror("Error", "Incentive must be a positive number")
                    return
                
                if incentive_type == "percentage" and incentive > 100:
                    messagebox.showerror("Error", "Incentive percentage must be between 0 and 100")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid incentive value")
                return
            
            success = self.handler_manager.create_handler(name, incentive, incentive_type)
            if success:
                if incentive_type == "percentage":
                    messagebox.showinfo("Success", f"Handler '{name}' created with {incentive}% incentive")
                else:
                    messagebox.showinfo("Success", f"Handler '{name}' created with fixed incentive of {incentive}")
                self.update_handler_dropdown()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Handler name already exists")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=config.BG_COLOR)
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Create",
            font=config.BUTTON_FONT,
            bg=config.EQUALS_BG,
            fg=config.BUTTON_FG,
            command=create_handler,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=config.BUTTON_FONT,
            bg=config.MODE_BG,
            fg=config.BUTTON_FG,
            command=dialog.destroy,
            width=10,
            height=2
        ).pack(side=tk.LEFT, padx=5)
    
    def show_handler_performance(self):
        """Display handler performance graph"""
        self.clear_graph_frame()
        handler_data = self.handler_manager.get_handler_performance()
        fig = self.graph_generator.create_handler_performance_graph(handler_data)
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
