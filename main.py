import gspread
import schedule
import time
import os
import json
import pandas as pd
from datetime import datetime
from data_processing import load_data_from_google_sheets, clean_data
from gmail_auth import get_gmail_credentials
from report import generate_charts
from pdf_generator import generate_pdf
from gmail_sender import send_email_gmail

CONFIG_FILE = "config.json"

# Main job (Menu 6)
def job(config):
    print("\n📊 Running scheduled job...")

    df = load_data(config)
    if df is None:
        print("No data loaded. Exiting job.")
        return

    df = clean_data(df)
    generate_charts(df)

    # Generate PDF
    pdf_path = "assets/sales_report.pdf"
    generate_pdf(df, output_file=pdf_path, pdf_settings=config.get("pdf_settings", {}))
    print(f"✅ PDF generated at '{pdf_path}'.")

    # Ask if user wants to send email now
    send_now = input("Do you want to send the report by email now? (yes/no): ").strip().lower()
    if send_now in ("yes", "y"):
        creds = get_gmail_credentials()
        if not creds:
            print(f"✅ PDF generation completed, check '{pdf_path}'. Email sending skipped by user.\n")
            return

        while True:
            recipients = config.get("recipients", [])
            valid_recipients = [email.strip() for email in recipients if email.strip()]
            if valid_recipients:
                break
            print("⚠️ No valid recipients found. Please enter at least one valid email.\n")
            change_recipients(config)

        send_email_gmail(
            valid_recipients,
            "Automated Sales Report",
            config.get("email_body", "Hello, attached is your automated sales report."),
            pdf_path
        )
        print("✅ Report sent successfully.\n")
    else:
        print(f"✅ PDF generation completed, check '{pdf_path}'. No email was sent.\n")

def load_data(config):
    if config.get("data_source") == "google_sheets":
        while True:
            sheet_name = config.get("sheet_name", "Spreadsheet")
            try:
                import gspread
                return load_data_from_google_sheets("service_account.json", sheet_name)
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"⚠️ Google Sheet '{sheet_name}' not found.")
                sheet_name = input("Please enter a valid Google Sheet name: ").strip()
                if sheet_name:
                    config["sheet_name"] = sheet_name
                    save_config(config)
                else:
                    print("Invalid input. Try again.")
    elif config.get("data_source") == "excel":
        excel_file = config.get("excel_file", "put_excel_files_here/Report.xlsx")
        os.makedirs(os.path.dirname(excel_file), exist_ok=True)
        try:
            return pd.read_excel(excel_file)
        except FileNotFoundError:
            print(f"⚠️ Excel file '{excel_file}' not found.")
            return None
        except Exception as e:
            print(f"⚠️ Error opening Excel file: {e}")
            return None
    else:
        print("⚠️ Invalid data source.")
        return None

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_config():
    default_config = {
        "data_source": "excel",
        "excel_file": "put_excel_files_here/Report.xlsx",
        "recipients": [],
        "schedule": {"type": "", "time": "", "end_date": ""},
        "pdf_settings": {"title": "Sales Report", "header_text": "Automated Monthly Sales Report"},
        "email_body": (
            "Hello,\n\n"
            "This is an automated email. Attached is the monthly sales report, summarizing key performance metrics and insights. "
            "Please review the figures and reach out if you have any questions or require further analysis.\n\n"
            "If you were not expecting this email, please disregard it.\n\n"
            "Best regards,\n"
            "_Dinis Fragata_"
        ),
        "sheet_name": "Spreadsheet"
    }

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)

    with open(CONFIG_FILE, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = {}

    # Fill defaults if missing
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                if sub_key not in config[key]:
                    config[key][sub_key] = sub_val
    return config

# Type of file (Local or Google Sheets)
def change_data_source(config):
    print("\nSelect data source:")
    print("1. Google Sheets")
    print("2. Local Excel file")
    choice = input("Choose 1 or 2: ").strip()
    if choice == "1":
        config["data_source"] = "google_sheets"
        change_sheet_name(config)
    elif choice == "2":
        config["data_source"] = "excel"
        file_name = input("Enter Excel file name (with or without .xlsx): ").strip()
        if not file_name:
            print("No file name entered, keeping previous Excel file.")
        else:
            if not file_name.lower().endswith(".xlsx"):
                file_name += ".xlsx"
            folder = "put_excel_files_here"
            os.makedirs(folder, exist_ok=True)
            config["excel_file"] = os.path.join(folder, file_name)
            print(f"✅ Excel file set to '{config['excel_file']}'.")
    else:
        print("Invalid choice, keeping previous data source.")

    save_config(config)

def change_sheet_name(config):
    sheet_name = input("Enter Google Sheets sheet name: ").strip()
    if sheet_name:
        config["sheet_name"] = sheet_name
        save_config(config)
        print(f"Sheet name updated to: {sheet_name}")
    else:
        print("Invalid sheet name. No changes made.")

def change_recipients(config):
    emails = input("Enter recipient emails (comma separated): ")
    config["recipients"] = [e.strip() for e in emails.split(",")]
    save_config(config)
    print("Recipients updated.")

def change_schedule(config):
    sched_type = input("Schedule type (daily/weekly/monthly/every_x_months): ").lower()
    sched = {"type": sched_type}

    if sched_type == "daily":
        sched["time"] = input("Enter time (HH:MM, 24h format): ")
    elif sched_type == "weekly":
        days = input("Enter days of week (comma separated, e.g., monday,wednesday): ")
        sched["days"] = [d.strip().lower() for d in days.split(",")]
        sched["time"] = input("Enter time (HH:MM, 24h format): ")
    elif sched_type == "monthly":
        sched["day"] = int(input("Enter day of month (1-31): "))
        sched["time"] = input("Enter time (HH:MM, 24h format): ")
    elif sched_type == "every_x_months":
        sched["day"] = int(input("Enter day of month (1-31): "))
        sched["interval"] = int(input("Enter interval in months: "))
        sched["time"] = input("Enter time (HH:MM, 24h format): ")
    else:
        print("Invalid type. Defaulting to daily at 08:00.")
        sched = {"type": "daily", "time": "08:00"}

    end_date = input("Enter end date (YYYY-MM-DD) or leave blank: ")
    sched["end_date"] = end_date.strip()
    config["schedule"] = sched
    save_config(config)
    print("Schedule updated.")

def change_email_body(config):
    body = input("Enter new email body: ")
    config["email_body"] = body
    save_config(config)
    print("Email body updated.")

def edit_pdf(config):
    title = input("Enter PDF title (leave blank to keep current): ")
    if title:
        config.setdefault("pdf_settings", {})["title"] = title
    header = input("Enter PDF header text (leave blank to keep current): ")
    if header:
        config.setdefault("pdf_settings", {})["header_text"] = header
    save_config(config)
    print("PDF settings updated.")

def reset_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    print("Configuration reset to default.")

# Menu
def show_menu():
    print("\n=== Automated Sales Report Menu ===")
    print("1. Change data source")
    print("2. Change recipients")
    print("3. Change schedule")
    print("4. Change email body")
    print("5. Edit PDF")
    print("6. Run scheduled job now")
    print("7. Reset all configuration")
    print("0. Exit")
    return input("Select an option: ")

def main_menu():
    while True:
        choice = show_menu()
        config = load_config()
        if choice == "1":
            change_data_source(config)
        elif choice == "2":
            change_recipients(config)
        elif choice == "3":
            change_schedule(config)
        elif choice == "4":
            change_email_body(config)
        elif choice == "5":
            edit_pdf(config)
        elif choice == "6":
            job(config)
        elif choice == "7":
            confirm = input("Are you sure you want to reset all configuration? (yes/no): ").strip().lower()
            if confirm in ("yes", "y"):
                reset_config()
            else:
                print("Reset canceled.")
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid option.")

# Scheduler setup
def start_scheduler():
    config = load_config()
    sched = config.get("schedule", {})
    if not sched:
        print("No schedule set. Use the menu to configure it first.")
        return

    if sched["type"] == "daily":
        schedule.every().day.at(sched["time"]).do(job, config)
    elif sched["type"] == "weekly":
        for day in sched.get("days", []):
            getattr(schedule.every(), day).at(sched["time"]).do(job, config)
    elif sched["type"] == "monthly":
        def monthly_job():
            if datetime.now().day == int(sched["day"]):
                job(config)
        schedule.every().day.at(sched["time"]).do(monthly_job)
    elif sched["type"] == "every_x_months":
        def x_months_job():
            today = datetime.now()
            if today.day == int(sched["day"]) and today.month % int(sched["interval"]) == 0:
                job(config)
        schedule.every().day.at(sched["time"]).do(x_months_job)

    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            if "end_date" in sched and sched["end_date"]:
                end_date = datetime.strptime(sched["end_date"], "%Y-%m-%d")
                if datetime.now() > end_date:
                    print("⏹ Scheduling ended.")
                    break
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")

# Main
if __name__ == "__main__":
    print("Welcome to Automated Sales Report System!")
    main_menu()