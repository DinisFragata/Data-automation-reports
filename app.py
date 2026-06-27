import os
import uuid
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from data_processing import clean_data
from pdf_generator import generate_pdf
from report import generate_charts
from zoho_sender import send_email_zoho


app = FastAPI(title="Automated Sales Report API")


FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://data-automation-reports.vercel.app",
)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    FRONTEND_URL,
]

allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_DIR = Path("uploads")
ASSETS_DIR = Path("assets")

UPLOAD_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)


REQUIRED_COLUMNS = ["Date", "Product", "Quantity", "Price", "Seller"]


DEFAULT_EMAIL_SUBJECT = "Automated Sales Report"

DEFAULT_EMAIL_BODY = (
    "Hello,\n\n"
    "Attached is your automated sales report with charts, metrics and analysis.\n\n"
    "Best regards,\n"
    "Automated Sales Report System"
)


@app.get("/")
def root():
    return {
        "message": "Automated Sales Report API is running",
        "email_provider": "zoho",
        "endpoints": {
            "health": "/health",
            "generate_report": "/generate-report",
            "download_report": "/download-report/{filename}",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


def _is_excel_file(filename: str) -> bool:
    return filename.lower().endswith((".xlsx", ".xls"))


def _validate_dataframe_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )


def _safe_filename(filename: str) -> str:
    return Path(filename).name


def _create_report_from_excel(upload_path: Path, pdf_path: Path) -> None:
    df = pd.read_excel(upload_path)

    _validate_dataframe_columns(df)

    df = df[REQUIRED_COLUMNS]
    df = clean_data(df)

    if df.empty:
        raise ValueError("The uploaded file has no valid rows after cleaning.")

    generate_charts(df)

    generate_pdf(
        df,
        output_file=str(pdf_path),
        pdf_settings={
            "title": "Sales Report",
            "header_text": "Automated Sales Report",
        },
    )


@app.post("/generate-report")
async def generate_report(
    file: UploadFile = File(...),
    send_email: bool = Form(False),
    recipients: str = Form(""),
    email_subject: str = Form(DEFAULT_EMAIL_SUBJECT),
    email_body: str = Form(DEFAULT_EMAIL_BODY),
):
    if not file.filename:
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload a file."},
        )

    original_filename = _safe_filename(file.filename)

    if not _is_excel_file(original_filename):
        return JSONResponse(
            status_code=400,
            content={"error": "Please upload an Excel file (.xlsx or .xls)."},
        )

    file_id = str(uuid.uuid4())

    upload_path = UPLOAD_DIR / f"{file_id}_{original_filename}"
    pdf_filename = f"sales_report_{file_id}.pdf"
    pdf_path = ASSETS_DIR / pdf_filename

    try:
        file_content = await file.read()

        with upload_path.open("wb") as uploaded_file:
            uploaded_file.write(file_content)

        _create_report_from_excel(upload_path, pdf_path)

        email_result = None

        if send_email:
            if not recipients.strip():
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Please provide at least one recipient email.",
                        "download_url": f"/download-report/{pdf_filename}",
                    },
                )

            try:
                email_result = send_email_zoho(
                    recipients=recipients,
                    subject=email_subject,
                    body=email_body,
                    attachment_path=str(pdf_path),
                )

            except Exception as email_error:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": f"Report generated, but Zoho email failed: {str(email_error)}",
                        "download_url": f"/download-report/{pdf_filename}",
                    },
                )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": (
                    "Report generated and sent by email successfully."
                    if send_email
                    else "Report generated successfully."
                ),
                "email_provider": "zoho",
                "email_sent": bool(send_email),
                "email_result": email_result,
                "download_url": f"/download-report/{pdf_filename}",
            },
        )

    except ValueError as validation_error:
        return JSONResponse(
            status_code=400,
            content={"error": str(validation_error)},
        )

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"error": f"Something went wrong: {str(error)}"},
        )

    finally:
        if upload_path.exists():
            upload_path.unlink()


@app.get("/download-report/{filename}")
def download_report(filename: str):
    safe_name = Path(filename).name

    if not safe_name.startswith("sales_report_") or not safe_name.endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid report filename."},
        )

    pdf_path = ASSETS_DIR / safe_name

    if not pdf_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Report not found."},
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename="sales_report.pdf",
    )