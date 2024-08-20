import customtkinter as ct
import tkinter
from tkinter import messagebox
import sqlite3
from tkcalendar import DateEntry
from fpdf import FPDF

# --------------------- UI Setup ---------------------
ct.set_appearance_mode("system")
root = ct.CTk()
root.title("Travel Agency")
root.geometry("1000x1000")
root.configure(fg_color="#126dbc")

# --------------------- Color and Font Configurations ---------------------
Primary = "#2D8A69"  
framefg = "white"
frame_clr = "#fcfbf7"
color1 = "#126dbc"

font1 = ("Roboto", 20)
font2 = ("Roboto", 16, "bold")
font3 = ("Poppins", 50, "bold")

# --------------------- Database Setup ---------------------
# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Create users table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        contact TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        dob TEXT NOT NULL,
        password TEXT NOT NULL,
        gender TEXT NOT NULL
    )
''')

# Create bookings table
c.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        departure TEXT NOT NULL,
        destination TEXT NOT NULL,
        departure_date TEXT NOT NULL,
        return_date TEXT NOT NULL,
        package TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')
conn.commit()

# --------------------- Utility Functions ---------------------
def toggle_password_visibility():
    """Toggle the visibility of the password fields."""
    if show_password_var.get():
        entry_password.configure(show="")
        entry_confirm_password.configure(show="")
    else:
        entry_password.configure(show="*")
        entry_confirm_password.configure(show="*")

# --------------------- User Authentication Functions ---------------------
def register_user():
    """Register a new user in the system."""
    firstname = entry_firstname.get()
    lastname = entry_lastname.get()
    contact = entry_contact.get()
    email = entry_email.get()
    dob = entry_dob.get()
    password = entry_password.get()
    confirm_password = entry_confirm_password.get()
    gender = gender_var.get()

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return

    if not firstname or not lastname or not contact or not email or not dob or not password or not gender:
        messagebox.showerror("Error", "All fields are required")
        return

    try:
        c.execute(
            "INSERT INTO users (firstname, lastname, contact, email, dob, password, gender) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (firstname, lastname, contact, email, dob, password, gender)
        )
        conn.commit()
        messagebox.showinfo("Success", "Registration successful")
        show_login()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email already registered")

def login_user():
    """Login a user into the system."""
    username = entry1.get()
    password = entry2.get()

    if not username or not password:
        messagebox.showerror("Error", "Both fields are required")
        return

    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (username, password))
    user = c.fetchone()

    if user:
        messagebox.showinfo("Success", f"Welcome {user[1]} {user[2]}")
        global current_user_id
        current_user_id = user[0]
        show_dashboard()
    else:
        messagebox.showerror("Error", "Invalid username or password")





# --------------------- Navigation Functions ---------------------
def show_register():
    """Display the registration page."""
    f1.place_forget()
    f2.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

def show_login():
    """Display the login page."""
    f2.place_forget()
    dashboard_frame.place_forget()
    book_trip_frame.place_forget()
    generate_report_frame.place_forget()
    f1.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

def show_dashboard():
    """Display the dashboard."""
    f1.place_forget()
    f2.place_forget()
    book_trip_frame.place_forget()
    generate_report_frame.place_forget()
    dashboard_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

    # f1.place_forget()
    # dashboard_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
   

def show_book_trip():
    """Display the book trip page."""
    dashboard_frame.place_forget()
    book_trip_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

def show_generate_report():
    """Display the generate report page."""
    dashboard_frame.place_forget()
    generate_report_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)



# --------------------- Booking Functions ---------------------
def submit_booking():
    """Submit a booking and save it to the database."""
    departure = departure_var.get()
    destination = destination_var.get()
    departure_date = departure_date_entry.get()
    return_date = return_date_entry.get()
    package = package_entry.get()

    if not departure or not destination or not departure_date or not return_date or not package:
        messagebox.showerror("Error", "All fields are required")
        return

    c.execute(
        "INSERT INTO bookings (user_id, departure, destination, departure_date, return_date, package) VALUES (?, ?, ?, ?, ?, ?)",
        (current_user_id, departure, destination, departure_date, return_date, package)
    )
    conn.commit()

    messagebox.showinfo("Success", "Booking successful")

    # Hide the book_trip_frame explicitly
    book_trip_frame.place_forget()
    show_generate_report()

# --------------------- Report Generation Functions ---------------------
def generate_pdf():
    """Generate a booking report as a PDF."""
    c.execute("SELECT * FROM bookings WHERE user_id = ?", (current_user_id,))
    booking = c.fetchone()

    # Fetch user details
    c.execute("SELECT * FROM users WHERE id = ?", (current_user_id,))
    user = c.fetchone()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Travel Booking Report", ln=True, align='C')
    pdf.ln(10)

    # Customer Details
    pdf.cell(200, 10, txt=f"Customer Name: {user[1]} {user[2]}", ln=True)
    pdf.cell(200, 10, txt=f"Contact: {user[3]}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {user[4]}", ln=True)
    pdf.ln(10)

    # Booking Details
    pdf.cell(200, 10, txt=f"Booking ID: {booking[0]}", ln=True)
    pdf.cell(200, 10, txt=f"Departure: {booking[2]}", ln=True)
    pdf.cell(200, 10, txt=f"Destination: {booking[3]}", ln=True)
    pdf.cell(200, 10, txt=f"Departure Date: {booking[4]}", ln=True)
    pdf.cell(200, 10, txt=f"Return Date: {booking[5]}", ln=True)
    pdf.cell(200, 10, txt=f"Package: {booking[6]}", ln=True)

    pdf.output("booking_report.pdf")
    messagebox.showinfo("Success", "PDF Report generated successfully!")

def generate_txt():
    """Generate a booking report as a TXT file."""
    c.execute("SELECT * FROM bookings WHERE user_id = ?", (current_user_id,))
    booking = c.fetchone()

    # Fetch user details
    c.execute("SELECT * FROM users WHERE id = ?", (current_user_id,))
    user = c.fetchone()

    with open("booking_report.txt", "w") as file:
        file.write("Travel Booking Report\n")
        file.write("\n")

        # Customer Details
        file.write(f"Customer Name: {user[1]} {user[2]}\n")
        file.write(f"Contact: {user[3]}\n")
        file.write(f"Email: {user[4]}\n")
        file.write("\n")

        # Booking Details
        file.write(f"Booking ID: {booking[0]}\n")
        file.write(f"Departure: {booking[2]}\n")
        file.write(f"Destination: {booking[3]}\n")
        file.write(f"Departure Date: {booking[4]}\n")
        file.write(f"Return Date: {booking[5]}\n")
        file.write(f"Package: {booking[6]}\n")

    messagebox.showinfo("Success", "TXT Report generated successfully!")

# --------------------- UI Elements ---------------------

# Login Frame
f1 = ct.CTkFrame(master=root, width=400, height=300, corner_radius=0, fg_color=frame_clr)
f1.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

l1 = ct.CTkLabel(master=f1, text="Log into your account", font=("Roboto", 24, "bold"), text_color=color1)
l1.place(relx=0.5, y=30, anchor=tkinter.CENTER)

entry1 = ct.CTkEntry(master=f1, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                     placeholder_text="Username", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry1.place(relx=0.5, y=100, anchor=tkinter.CENTER)

entry2 = ct.CTkEntry(master=f1, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                     placeholder_text="Password", font=("Roboto", 16, "bold"), placeholder_text_color="White", show="*")
entry2.place(relx=0.5, y=160, anchor=tkinter.CENTER)

submit_button = ct.CTkButton(master=f1, text="Login", width=100, height=40, fg_color="#00adef", text_color=framefg,
                             font=font2, command=login_user)
submit_button.place(relx=0.69, y=195)

register_button = ct.CTkButton(master=f1, text="Register", width=100, height=40, fg_color="#00adef", text_color=framefg,
                               font=font2, command=show_register)
register_button.place(relx=0.07, y=195)

# Registration Frame
f2 = ct.CTkFrame(master=root, width=500, height=650, corner_radius=10, fg_color=frame_clr)

l2 = ct.CTkLabel(master=f2, text="Register an account", font=("Roboto", 24, "bold"), text_color=color1)
l2.place(relx=0.5, y=30, anchor=tkinter.CENTER)

entry_firstname = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                              placeholder_text="First Name", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry_firstname.place(relx=0.5, y=80, anchor=tkinter.CENTER)

entry_lastname = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                             placeholder_text="Last Name", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry_lastname.place(relx=0.5, y=140, anchor=tkinter.CENTER)

entry_contact = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                            placeholder_text="Contact No", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry_contact.place(relx=0.5, y=200, anchor=tkinter.CENTER)

entry_email = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                          placeholder_text="Email", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry_email.place(relx=0.5, y=260, anchor=tkinter.CENTER)

entry_dob = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                        placeholder_text="Date of Birth (YEAR-MONTH-DAY)", font=("Roboto", 16, "bold"), placeholder_text_color="White")
entry_dob.place(relx=0.5, y=320, anchor=tkinter.CENTER)

entry_password = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                             placeholder_text="Password", font=("Roboto", 16, "bold"), placeholder_text_color="White",
                             show="*")
entry_password.place(relx=0.5, y=380, anchor=tkinter.CENTER)

entry_confirm_password = ct.CTkEntry(master=f2, width=350, height=40, text_color="white", corner_radius=10, fg_color="#a8afb5",
                                     placeholder_text="Confirm Password", font=("Roboto", 16, "bold"), placeholder_text_color="White",
                                     show="*")
entry_confirm_password.place(relx=0.5, y=440, anchor=tkinter.CENTER)

show_password_var = tkinter.BooleanVar()
show_password_checkbox = ct.CTkCheckBox(master=f2, text="Show Password", variable=show_password_var,
                                        command=toggle_password_visibility, fg_color=Primary, font=("Roboto", 14))
show_password_checkbox.place(relx=0.5, y=490, anchor=tkinter.CENTER)

gender_var = tkinter.StringVar(value="Male")
gender_label = ct.CTkLabel(master=f2, text="Gender:", font=("Roboto", 16, "bold"), text_color=color1)
gender_label.place(relx=0.3, y=530, anchor=tkinter.CENTER)

gender_male = ct.CTkRadioButton(master=f2, text="Male", variable=gender_var, value="Male", fg_color=Primary,
                                font=("Roboto", 14))
gender_male.place(relx=0.5, y=530, anchor=tkinter.W)

gender_female = ct.CTkRadioButton(master=f2, text="Female", variable=gender_var, value="Female", fg_color=Primary,
                                  font=("Roboto", 14))
gender_female.place(relx=0.5, y=530, anchor=tkinter.E)

submit_button_reg = ct.CTkButton(master=f2, text="Register", width=100, height=40, fg_color="#00adef", text_color=framefg,
                                 font=font2, command=register_user)
submit_button_reg.place(relx=0.69, y=580)

login_button_reg = ct.CTkButton(master=f2, text="Login", width=100, height=40, fg_color="#00adef", text_color=framefg,
                                font=font2, command=show_login)
login_button_reg.place(relx=0.07, y=580)


# Dashboard Frame
dashboard_frame = ct.CTkFrame(master=root, width=450, height=300, corner_radius=0, fg_color=frame_clr)

dashboard_label = ct.CTkLabel(master=dashboard_frame, text="Dashboard", font=("Roboto", 30, "bold"), text_color=color1)
dashboard_label.place(relx=0.5, y=40, anchor=tkinter.CENTER)

book_trip_button = ct.CTkButton(master=dashboard_frame, text="Book a Trip", width=200, height=50, fg_color="#00adef",
                                text_color=framefg, font=font2, command=show_book_trip)
book_trip_button.place(relx=0.5, y=120, anchor=tkinter.CENTER)

generate_report_button = ct.CTkButton(master=dashboard_frame, text="Generate Report", width=200, height=50,
                                      fg_color="#00adef", text_color=framefg, font=font2, command=show_generate_report)
generate_report_button.place(relx=0.5, y=180, anchor=tkinter.CENTER)

 # Add the Logout button
logout_button = ct.CTkButton(master=dashboard_frame, text="Logout", width=100, height=40, fg_color="#d9534f", text_color="white",
                                 font=font2, command=show_login)
logout_button.place(relx=0.77, y=15)  # Adjust the position as needed

# Book Trip Frame
book_trip_frame = ct.CTkFrame(master=root, width=600, height=500, corner_radius=10, fg_color=frame_clr)

book_trip_label = ct.CTkLabel(master=book_trip_frame, text="Book a Trip", font=("Roboto", 24, "bold"), text_color=color1)
book_trip_label.place(relx=0.5, y=30, anchor=tkinter.CENTER)

# Departure Label and Dropdown Menu
departure_label = ct.CTkLabel(master=book_trip_frame, text="Departure Place:", font=("Roboto", 16, "bold"), text_color=color1)
departure_label.place(relx=0.30, y=100, anchor=tkinter.E)

departure_var = tkinter.StringVar(value="Kathmandu")  # Default value
departure_menu = ct.CTkOptionMenu(master=book_trip_frame, values=["Kathmandu"], 
                                  width=250, height=40, fg_color="#a8afb5", text_color="white", 
                                  font=("Roboto", 16, "bold"), variable=departure_var)
departure_menu.place(relx=0.45, y=100, anchor=tkinter.W)

# Destination Label and Dropdown Menu
destination_label = ct.CTkLabel(master=book_trip_frame, text="Arriving Place:", font=("Roboto", 16, "bold"), text_color=color1)
destination_label.place(relx=0.30, y=150, anchor=tkinter.E)

destination_var = tkinter.StringVar()
destination_menu = ct.CTkOptionMenu(master=book_trip_frame, 
                                    values=["Pokhara", "Chitwan", "Lumbini", "Everest Base Camp", "Annapurna Base Camp", 
                                            "Nagarkot", "Dhulikhel", "Poon Hill", "Gosaikunda"], 
                                    width=250, height=40, fg_color="#a8afb5", text_color="white", 
                                    font=("Roboto", 16, "bold"), variable=destination_var)
destination_menu.place(relx=0.45, y=150, anchor=tkinter.W)

# Departure Date Label and Date Picker
departure_date_label = ct.CTkLabel(master=book_trip_frame, text="Departure Date:", font=("Roboto", 16, "bold"), text_color=color1)
departure_date_label.place(relx=0.30, y=200, anchor=tkinter.E)

departure_date_entry = DateEntry(master=book_trip_frame, width=18, background="#a8afb5", foreground="white",
                                 borderwidth=1, date_pattern='yyyy-mm-dd',
                                 font=("Roboto", 16, "bold"), bd=1, relief=tkinter.SOLID)
departure_date_entry.place(relx=0.45, y=250, anchor=tkinter.W)

# Return Date Label and Date Picker
return_date_label = ct.CTkLabel(master=book_trip_frame, text="Return Date:", font=("Roboto", 16, "bold"), text_color=color1)
return_date_label.place(relx=0.30, y=250, anchor=tkinter.E)

return_date_entry = DateEntry(master=book_trip_frame, width=18, background="#a8afb5", foreground="white",
                              borderwidth=1, date_pattern='yyyy-mm-dd',
                              font=("Roboto", 16, "bold"), bd=1, relief=tkinter.SOLID)
return_date_entry.place(relx=0.45, y=310, anchor=tkinter.W)

# Package Label and Option Menu
package_label = ct.CTkLabel(master=book_trip_frame, text="Package Type:", font=("Roboto", 16, "bold"), text_color=color1)
package_label.place(relx=0.30, y=300, anchor=tkinter.E)

package_entry = ct.CTkOptionMenu(master=book_trip_frame, values=["Budget", "Standard", "Premium"],
                                 width=250, height=40, fg_color="#a8afb5", text_color="white", font=("Roboto", 16, "bold"))
package_entry.place(relx=0.45, y=300, anchor=tkinter.W)

# SubmitBooking Button
submit_booking_button = ct.CTkButton(master=book_trip_frame, text="Submit Booking", width=150, height=40,
                                     fg_color="#00adef", text_color=framefg, font=font2, command=submit_booking)
submit_booking_button.place(relx=0.5, y=380, anchor=tkinter.CENTER)

# Add the Back button
back_button = ct.CTkButton(master=book_trip_frame, text="Back", width=100, height=40, fg_color=Primary, text_color="white",
                           font=font2, command=show_dashboard)  # Corrected command
back_button.place(relx=0.040, y=420) # Adjust the position as needed

# Generate Report Frame
generate_report_frame = ct.CTkFrame(master=root, width=450, height=300, corner_radius=0, fg_color=frame_clr)

generate_report_label = ct.CTkLabel(master=generate_report_frame, text="Generate Report", font=("Roboto", 30, "bold"),
                                    text_color=color1)
generate_report_label.place(relx=0.5, y=40, anchor=tkinter.CENTER)

generate_pdf_button = ct.CTkButton(master=generate_report_frame, text="Generate PDF", width=200, height=50,
                                   fg_color="#00adef", text_color=framefg, font=font2, command=generate_pdf)
generate_pdf_button.place(relx=0.5, y=120, anchor=tkinter.CENTER)

generate_excel_button = ct.CTkButton(master=generate_report_frame, text="Generate Txt", width=200, height=50,
                                     fg_color="#00adef", text_color=framefg, font=font2, command=generate_txt)
generate_excel_button.place(relx=0.5, y=180, anchor=tkinter.CENTER)

back_button = ct.CTkButton(master=generate_report_frame, text="Back", width=100, height=40, fg_color=Primary, text_color="white",
                               font=font2, command=show_dashboard)
back_button.place(relx=0.10, y=230) 

root.mainloop()

