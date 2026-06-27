from fpdf import FPDF
import os

class PDF(FPDF):
    def __init__(self, title="Automatically generated sales report"):
        super().__init__()
        self.title = title

    def header(self):
        # Header
        if hasattr(self, 'header_text') and self.header_text:
            self.set_font('Arial', 'I', 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, self.header_text, align='C')
        self.ln(10)

    def footer(self):
        # Footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)

        # Left side
        self.cell(0, 10, "Made by: Dinis Fragata", align='L')

        # Right side
        self.cell(0, 10, f"Page {self.page_no()}", align='R')


def generate_pdf(df, output_file='assets/sales_report.pdf', pdf_settings=None):
    pdf_settings = pdf_settings or {}
    title = pdf_settings.get("title", "Automatically generated sales report")
    header_text = pdf_settings.get("header_text", "")

    pdf = PDF(title=title)
    pdf.header_text = header_text

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, title, ln=True, align='L')
    pdf.ln(10)

    # Metrics
    total_quantity = df['Quantity'].sum()
    total_revenue = (df['Quantity'] * df['Price']).sum()
    unique_products = df['Product'].nunique()
    unique_sellers = df['Seller'].nunique()
    best_product = df.groupby("Product")['Quantity'].sum().idxmax()
    best_seller = df.groupby("Seller")['Quantity'].sum().idxmax()

    metrics = [
        ("Total Quantity Sold", str(total_quantity)),
        ("Total Revenue", f"${total_revenue:.2f}"),
        ("Number of Products", str(unique_products)),
        ("Number of Sellers", str(unique_sellers)),
        ("Best Selling Product", best_product),
        ("Top Seller", best_seller),
    ]

    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, 'Summary of Metrics:', ln=True)
    pdf.ln(5)

    # Table header
    pdf.set_font('Arial', 'B', 11)
    pdf.set_fill_color(200, 200, 200)
    pdf.cell(80, 8, "Metrics", border=1, fill=True, align='C')
    pdf.cell(100, 8, "Values", border=1, fill=True, align='C')
    pdf.ln()

    # Table rows
    pdf.set_font('Arial', '', 11)
    for metric, value in metrics:
        pdf.cell(80, 8, metric, border=1)
        pdf.cell(100, 8, value, border=1)
        pdf.ln()
    pdf.ln(10)

    # Analytical Explanations
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Sales Analysis:', ln=True)
    pdf.ln(2)

    pdf.set_font('Arial', '', 12)
    analysis_text = (
        f"The sales report shows a total of {total_quantity} units sold, generating "
        f"a revenue of ${total_revenue:.2f}. The most popular product was '{best_product}', "
        f"indicating a strong demand in this category. "
        f"The top performing seller was '{best_seller}', contributing significantly to total sales.\n\n"

        f"From the observed trends, we can identify the overall performance across products and sellers. "
        f"Consistently high sales for certain products may indicate market stability, while fluctuations "
        f"highlight possible seasonal or external influences."
    )
    pdf.multi_cell(0, 8, analysis_text)
    pdf.ln(10)

    # Charts with Explanations
    charts = [
        ("assets/total_quantity_per_product.png", "This chart shows the distribution of total sales quantity per product."),
        ("assets/total_revenue_per_product.png", "This chart illustrates the revenue per product, highlighting the most profitable items."),
        ("assets/total_quantity_per_seller.png", "This chart compares sellers, showing which sellers drove the most sales."),
        ("assets/quantity_trend_over_time.png", "This chart represents sales trends over time, helping identify stability or seasonal spikes."),
    ]

    for chart, explanation in charts:
        if os.path.exists(chart):
            pdf.image(chart, w=180)
            pdf.ln(5)
            pdf.set_font('Arial', 'I', 11)
            pdf.multi_cell(0, 8, explanation)
            pdf.ln(10)

    # Save PDF
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    pdf.output(output_file)