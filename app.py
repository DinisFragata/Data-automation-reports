import os
import uuid
import pandas as pd

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from data_processing import clean_data
from report import generate_charts
from pdf_generator import generate_pdf


app = FastAPI(title="Automated Sales Report API")

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://data-automation-reports.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
ASSETS_DIR = "assets"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Automated Sales Report API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-report")
async def generate_report(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload an Excel file (.xlsx or .xls)."}
        )

    file_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    pdf_path = os.path.join(ASSETS_DIR, f"sales_report_{file_id}.pdf")

    try:
        file_content = await file.read()

        with open(upload_path, "wb") as f:
            f.write(file_content)

        df = pd.read_excel(upload_path)

        required_columns = ["Date", "Product", "Quantity", "Price", "Seller"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Missing required columns: {', '.join(missing_columns)}"
                }
            )

        df = df[required_columns]
        df = clean_data(df)

        if df.empty:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "The uploaded file has no valid rows after cleaning."
                }
            )

        generate_charts(df)

        generate_pdf(
            df,
            output_file=pdf_path,
            pdf_settings={
                "title": "Sales Report",
                "header_text": "Automated Sales Report"
            }
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename="sales_report.pdf"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Something went wrong: {str(e)}"}
        )

    finally:
        if os.path.exists(upload_path):
            os.remove(upload_path)