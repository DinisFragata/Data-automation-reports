# Automated Sales Report System

A business automation system that transforms raw spreadsheet data into visual PDF reports and automatically delivers them via email.

Built to reduce repetitive reporting tasks and improve business decision-making.

---

### Key Features
- Import data from Excel or Google Sheets
- Automatic data cleaning and validation
- Generate sales insights and performance metrics
- Create visual charts automatically
- Export professional PDF reports
- Send reports directly via Gmail
- Schedule recurring reports (daily, weekly, monthly)

## Screenshots

### Raw data spreadsheet

<img width="1536" height="688" alt="image" src="https://github.com/user-attachments/assets/d5c44559-1483-41dd-a67d-264c66e1162b" />


### PDF output

<img width="451" height="637" alt="image" src="https://github.com/user-attachments/assets/8bf953ae-8b05-4344-abaa-e41fe8e7029c" />

<img width="447" height="633" alt="image" src="https://github.com/user-attachments/assets/bad34cea-bdbd-4d8e-8e00-9b933b42cdaf" />

_Page 1 & 2_

<img width="446" height="635" alt="image" src="https://github.com/user-attachments/assets/a503a433-3495-4295-a945-62fa853fd798" />

_Page 3_

## Sample output

[PDF report](assets/examples/Example_sales_report.pdf)

## Project Vision

I started this project as a way to explore automation systems.

The idea was to build a reusable reporting workflow capable of transforming raw data into structured reports automatically. 

Because in my internship I saw that many businesses still spend significant time manually collecting spreadsheet data and transforming it. So my goal with this project was to automate the entire workflow.

By integrating Excel files or Google Sheets as data sources, the system can automatically:

- Process raw data
- Generate insights
- Create charts
- Build PDF reports
- Deliver reports via email
- Run automatically on scheduled intervals

This creates a reusable workflow for recurring business reporting, reducing manual effort and improving consistency.

## Real-World Use Cases

I think that this project has many usefull applications, for example, it can be adapted for:

- Weekly sales reports
- Inventory tracking reports
- Marketing campaign reports
- Financial summaries
- Hotel occupancy reports
- Client performance reports

Basically this automation workflow can be customized for any business that relies on spreadsheets and recurring reporting.

---

## Architecture

Data Source (Excel / Google Sheets)

↓

Data Cleaning & Processing

↓

Chart Generation

↓

PDF Report Creation

↓

Email Delivery

↓

Scheduled Automation

---

## Tech Stack

- Python
- Pandas
- Matplotlib
- ReportLab
- Google Sheets API
- Gmail API
- Cron Jobs
- OpenPyXL
