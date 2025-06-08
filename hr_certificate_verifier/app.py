import re
from fastapi import FastAPI, UploadFile, File, Query, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import pytesseract
from PIL import Image
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv
load_dotenv()

# QR/Barcode extraction
import cv2
import numpy as np
from preprocess_for_ocr import preprocess_for_ocr
from extract_with_gpt import extract_fields_with_gpt

# Load spaCy English model for NER
import spacy
spacy_model = spacy.load('en_core_web_sm')
from rapidfuzz import fuzz, process

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to HR Certificate Verifier API. Visit /docs for documentation."}

# Database & Auth setup
import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta

# Pydantic models for auth
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hr_certificate_verifier.db")
engine = sqlalchemy.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="standard")
    verifications = relationship("VerificationRequest", back_populates="user")

class VerificationRequest(Base):
    __tablename__ = "verification_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    to_email = Column(String)
    employee_name = Column(String)
    id_no = Column(String)
    department = Column(String)
    status = Column(String)
    extraction_error = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    hr_reply = Column(Text, nullable=True)
    user = relationship("User", back_populates="verifications")

class AuditTrail(Base):
    __tablename__ = "audit_trail"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String)
    action = Column(String)
    document_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def log_audit(db, user_email, action, document_id=None, details=None):
    entry = AuditTrail(user_email=user_email, action=action, document_id=document_id, details=details)
    db.add(entry)
    db.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
def hash_password(pw):
    return pwd_context.hash(pw)
def create_access_token(data: dict, expires: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires if expires else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class TokenData(BaseModel):
    email: str = None
    role: str = None

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cred_exc = HTTPException(401, "Could not validate credentials", headers={"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if not email:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise cred_exc
    return user

def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(403, "Admin privileges required")
    return current_user

@app.post("/signup", response_model=Token)
def signup(user: UserCreate = Body(...), db: Session = Depends(get_db)):
    hashed = hash_password(user.password)
    usr = User(email=user.email, hashed_password=hashed)
    db.add(usr); db.commit(); db.refresh(usr)
    log_audit(db, user.email, "signup", details="User signed up")
    access = create_access_token({"sub": usr.email, "role": usr.role})
    return {"access_token": access, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect credentials")
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/audit_trail")
def get_audit_trail(db: Session = Depends(get_db)):
    logs = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    return [{
        "id": log.id,
        "user_email": log.user_email,
        "action": log.action,
        "document_id": log.document_id,
        "details": log.details,
        "timestamp": log.timestamp.isoformat()
    } for log in logs]

@app.get("/audit_trail/export/csv")
def export_audit_csv(db: Session = Depends(get_db)):
    logs = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "User Email", "Action", "Document ID", "Details", "Timestamp"])
    for log in logs:
        writer.writerow([log.id, log.user_email, log.action, log.document_id, log.details, log.timestamp.isoformat()])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_trail.csv"})

@app.get("/audit_trail/export/excel")
def export_audit_excel(db: Session = Depends(get_db)):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "User Email", "Action", "Document ID", "Details", "Timestamp"])
    logs = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    for log in logs:
        ws.append([log.id, log.user_email, log.action, log.document_id, log.details, log.timestamp.isoformat()])
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=audit_trail.xlsx"})

@app.post("/get_company_contacts")
def get_company_contacts(payload: dict = Body(...), db: Session = Depends(get_db)):
    website = payload.get("website")
    if not website:
        return {"error": "No website provided."}
    contacts = set()
    phones = set()
    urls_to_check = [website]
    
# Try /contact page as well
    if website.endswith('/'):
        urls_to_check.append(website + 'contact')
    else:
        urls_to_check.append(website + '/contact')
    for url in urls_to_check:
        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(resp.text, 'html.parser')
            
# Find emails
            for mail in set(re.findall(r'[\w\.-]+@[\w\.-]+', resp.text)):
                contacts.add(mail)
            
# Find phone numbers (simple regex)
            for phone in set(re.findall(r'\+?\d[\d\s\-()]{7,}\d', resp.text)):
                phones.add(phone)
        except Exception as e:
            continue
    return {"emails": list(contacts), "phones": list(phones)}

@app.post("/send_verification_email")
def send_verification_email(payload: dict = Body(...), db: Session = Depends(get_db)):
    to_email = payload.get("to_email")
    cert_fields = payload.get("fields", {})
    reply_to = payload.get("reply_to")
    if not to_email:
        return {"error": "Recipient email required."}
    
# SMTP config from environment variables (set these in your system or .env file)
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    from_email = os.environ.get("FROM_EMAIL", smtp_user)
    if not all([smtp_host, smtp_user, smtp_pass, from_email]):
        return {"error": "SMTP configuration is incomplete. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, and FROM_EMAIL as environment variables."}
    
# Compose email
    subject = "Certificate Verification Request"
    
# Prepare custom email content using HTML template
    company_name = "Caritas Hospital and Institute of Health Sciences, Thellakom"
    employee_name = cert_fields.get('employee_name', '').strip()
    department = cert_fields.get('department', '').strip()
    designation = cert_fields.get('designation', '').strip()
    id_no = cert_fields.get('id_no', '').strip()
    employment_period = cert_fields.get('employment_period', '').strip()
    html_body = f"""
    <p>Dear Sir/ Madam,</p>
    <p>I am <b>Mr. Cirosh Joseph</b>, CHRO at <b>{company_name}</b>, Kottayam, Kerala, India.</p>
    <p>Ms. <b>{employee_name}</b> has joined our organization as <b>{designation}</b>. She has produced a certificate stating that she was employed at your esteemed organization. Please find the attached certificate provided by the candidate for your kind perusal.</p>
    <p>{company_name} is interested in verifying the genuineness of the said certificate and receiving additional information about her.</p>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <tr><th colspan="2" style="background:
#f0f0f0;">Details provided by Candidate</th></tr>
      <tr><td><b>Name</b></td><td>{employee_name}</td></tr>
      <tr><td><b>Employee ID</b></td><td>{id_no if id_no else '-'}</td></tr>
      <tr><td><b>Designation</b></td><td>{designation}</td></tr>
      <tr><td><b>Period of Employment</b></td><td>{employment_period if employment_period else '-'}</td></tr>
      <tr><td><b>Department Worked</b></td><td>{department}</td></tr>
    </table>
    <br />
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <tr><th colspan="2" style="background:
#f0f0f0;">Details as per your records</th></tr>
      <tr><td><b>Reason for Leaving</b></td><td></td></tr>
      <tr><td><b>Eligible for rehire? (If No Kindly Specify the reason)</b></td><td></td></tr>
      <tr><td><b>Status of Exit Formalities (Complete/Pending - details if pending)</b></td><td></td></tr>
      <tr><td><b>Are the Attached Documents Genuine?  - Yes/No (If No, kindly Specify the reason)</b></td><td></td></tr>
      <tr><td><b>Additional Comments</b></td><td></td></tr>
    </table>
    <br />
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
      <tr><th colspan="2" style="background:
#f0f0f0;">Verifying Authority Details</th></tr>
      <tr><td><b>Name of the Organisation</b></td><td></td></tr>
      <tr><td><b>Name of the Verifying Authority</b></td><td></td></tr>
      <tr><td><b>Designation</b></td><td></td></tr>
      <tr><td><b>Signature & Date</b></td><td></td></tr>
    </table>
    <br />
    <p>Kindly note that your inputs and feedback given would play a significant role and therefore we await your response for the same at the earliest.</p>
    <p>We look forward to your kind cooperation and thank you in anticipation.</p>
    <p>Thanking You<br />With all good wishes<br /><b>Mr. Cirosh Joseph</b><br />Chief Human Resources Officer</p>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.attach(MIMEText(html_body, "html"))
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, [to_email], msg.as_string())
        
# Log verification request to SQLite
        verification_request = VerificationRequest(user_id=current_user.id, to_email=to_email, employee_name=employee_name, id_no=id_no, department=department, status="sent", sent_at=datetime.utcnow())
        db.add(verification_request); db.commit(); db.refresh(verification_request)
        log_audit(db, current_user.email, "send_verification_email", document_id=verification_request.id, details=f"Verification email sent to {to_email}")
        return {"success": True, "message": f"Verification email sent to {to_email}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Endpoint to list all verification requests
@app.get("/verifications")
def list_verifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        items = db.query(VerificationRequest).order_by(VerificationRequest.sent_at.desc()).all()
    else:
        items = db.query(VerificationRequest).filter(VerificationRequest.user_id == current_user.id).all()
    return [{"id": v.id, "to_email": v.to_email, "employee_name": v.employee_name, "id_no": v.id_no, "department": v.department, "status": v.status, "sent_at": v.sent_at, "hr_reply": v.hr_reply} for v in items]

# Endpoint to update verification status
@app.post("/update_verification_status")
def update_verification_status(payload: dict = Body(...), db: Session = Depends(get_db)):
    verification_id = payload.get('id')
    status = payload.get('status')
    hr_reply = payload.get('hr_reply')
    if not verification_id or not status:
        return {"error": "id and status are required"}
    verification_request = db.query(VerificationRequest).filter(VerificationRequest.id == verification_id).first()
    if not verification_request:
        return {"error": "Verification request not found"}
    verification_request.status = status
    verification_request.hr_reply = hr_reply
    db.commit()
    return {"success": True}

@app.post("/upload", response_class=JSONResponse)
def upload_certificate(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = file.file.read()
    
# Convert bytes to numpy array for OpenCV
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    
# Try QR code extraction with OpenCV
    detector = cv2.QRCodeDetector()
    qr_data, bbox, _ = detector.detectAndDecode(img)
    if qr_data:
        text = None  
# No need for OCR if QR found
    else:
        
# Fallback to OCR using pytesseract
        image = Image.open(io.BytesIO(contents))
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        preprocessed = preprocess_for_ocr(img_cv)
        text = pytesseract.image_to_string(preprocessed)
        qr_data = None
    print("\n===== OCR OUTPUT START =====\n", text, "\n===== OCR OUTPUT END =====\n")
    # Only use fallback extraction (LLM disabled or unavailable)
    print("[DEBUG] Using advanced fallback extraction logic")
    result = extract_certificate_fields(text if text else '', qr_data=qr_data)
    if result is None:
        print("extract_certificate_fields returned None!")
        result = {}  # Defensive fallback
    print("Extracted fields result:", result)
    # Add OCR quality warning if text is garbled
    ocr_warning = None
    if len(text) > 0 and sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) > 0.2:
        ocr_warning = "OCR output appears garbled. Please upload a clearer image or a direct scan for best results."
    # Add warning to result
    result['ocr_warning'] = ocr_warning
    # Suspicious feature detection
    suspicious_features = []

    # 1. Missing fields
    for field in ["company_name", "signatory", "employment_period", "designation", "date_of_issuance"]:
        if not result.get(field):
            suspicious_features.append(f"Missing field: {field.replace('_', ' ').title()}")

    # 2. Invalid dates or short employment duration
    import datetime
    from dateutil import parser as date_parser
    employment_period = result.get("employment_period")
    if employment_period and 'to' in employment_period:
        try:
            parts = employment_period.split('to')
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            start_date = date_parser.parse(start_str, fuzzy=True, dayfirst=True)
            end_date = date_parser.parse(end_str, fuzzy=True, dayfirst=True)
            if start_date > end_date:
                suspicious_features.append("Employment start date is after end date")
            elif (end_date - start_date).days < 30:
                suspicious_features.append("Employment duration less than 1 month")
            if end_date > datetime.datetime.now():
                suspicious_features.append("Employment end date is in the future")
        except Exception as e:
            suspicious_features.append("Could not parse employment period dates")
            print(f"Error parsing employment period dates: {e}")

    # 3. Suspicious signatory
    signatory = result.get("signatory", "")
    if signatory:
        if len(signatory.split()) < 2 or re.search(r'HR|Manager|Admin|Department', signatory, re.IGNORECASE):
            suspicious_features.append("Signatory appears too generic or incomplete")

    # 4. Company name mismatch (requires cross-check, so just flag if company name is generic)
    company_name = result.get("company_name", "")
    if company_name and len(company_name.split()) < 2:
        suspicious_features.append("Company name appears too generic")

    # 5. OCR quality (garbled text)
    if len(text) > 0 and sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) > 0.2:
        suspicious_features.append("Certificate text contains many unusual characters (possible OCR error)")

    return {
        "extracted_fields": result,
        "raw_text": text,
        "suspicious_features": suspicious_features
    }

@app.post("/crosscheck_company")
async def crosscheck_company(payload: dict = Body(...)):
    """Stub endpoint to cross-check company name and return an official website."""
    company_name = payload.get("company_name")
    if not company_name:
        return JSONResponse(status_code=400, content={"error": "company_name missing"})
    # Basic normalization: remove non-alphanumeric, lowercase
    normalized = re.sub(r'\W+', '', company_name.lower())
    official_website = f"https://www.{normalized}.com"
    return {"official_website": official_website}

def fuzzy_find_keyword(lines, keywords, threshold=80):
    # Returns (line_idx, keyword, match_score) if found
    for idx, line in enumerate(lines):
        for kw in keywords:
            score = fuzz.partial_ratio(kw.lower(), line.lower())
            if score >= threshold:
                return idx, kw, score
    return None, None, 0

def context_window(lines, idx, window=2):
    # Returns lines[idx:idx+window]
    return ' '.join(lines[idx:idx+window]) if idx is not None else ''

def extract_certificate_fields(text, qr_data=None):
    print("[DEBUG] extract_certificate_fields called")
    import re
    global spacy_model
    fields = {
        "company_name": None,
        "signatory": None,
        "employment_period": None,
        "designation": None,
        "date_of_issuance": None,
        "employee_name": None,
        "id_no": None,
        "department": None,
        "_confidence": {}  # Store confidence/source info for frontend
    }
    # --- QR/Barcode Extraction (if present) ---
    if qr_data:
        import json
        try:
            qr_fields = json.loads(qr_data)
            if isinstance(qr_fields, dict):
                for key in fields:
                    if key in qr_fields and qr_fields[key]:
                        fields[key] = qr_fields[key]
                        fields["_confidence"][key] = "QR"
        except Exception:
            # Fallback: parse as key: value lines
            for line in qr_data.splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip().lower().replace(' ', '_')
                    v = v.strip()
                    for key in fields:
                        if k == key and v:
                            fields[key] = v
                            fields["_confidence"][key] = "QR"
    # --- Advanced Certificate Extraction Logic ---
    # Normalize common OCR mis-readings and split lines
    text = text.replace('rom ', 'from ')
    # Fix OCR variants of diagnostics
    text = re.sub(r'Dri[gq]nostes|Diagrosties', 'Diagnostics', text, flags=re.IGNORECASE)
    # Split lines, filter out blank lines and stray OCR garbage
    raw_lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in raw_lines if l and l.lower() != 'ww']
    # Normalize OCR misreads: 'O8'→'08' for dates
    lines = [re.sub(r'\bO(?=\d)', '0', l) for l in lines]
    top5 = lines[:5]

    # 1. Company Name: pick first top-5 line with org keywords, skip 'CERTIFICATE' and garbage
    org_keywords = ["PVT","LTD","LLP","INC","CORP","HOSPITAL","CLINIC","UNIVERSITY","COLLEGE","INSTITUTE","ORGANISATION","ORGANIZATION","SOCIETY","SCHOOL","LAB","SCANS","DIAGNOSTICS"]
    raw_company = next((l for l in top5 if 'CERTIFICATE' not in l.upper() and any(k in l.upper() for k in org_keywords)), None)
    if not raw_company:
        raw_company = next((l for l in lines if any(k in l.upper() for k in org_keywords)), None)
    if raw_company:
        raw_company = re.sub(r"\baul\b", "and", raw_company, flags=re.IGNORECASE)
    company = re.sub(r"\s*\(.*$", "", raw_company).strip() if raw_company else None
    fields["company_name"] = company
    if company:
        fields["_confidence"]["company_name"] = "top-pattern"

    # 2. Employee Name: regex on 'cert* that ... was'
    employee_name = None
    m = re.search(r'cert\w* that\s+(?:Mr\.?|Ms\.?|Miss\.?|Mrs\.?|Dr\.?|)?\s*([A-Z][a-zA-Z ]+?)\s+was', text, re.IGNORECASE|re.DOTALL)
    if m:
        employee_name = m.group(1).strip()
    else:
        # fallback: next capitalized word on line after 'cert* that'
        idx = next((i for i, l in enumerate(lines) if re.search(r'cert\w* that', l, re.IGNORECASE)), None)
        if idx is not None and idx+1 < len(lines):
            m2 = re.search(r'([A-Z][a-zA-Z ]+)', lines[idx+1])
            if m2: employee_name = m2.group(1).strip()
    # spaCy fallback if still missing
    if not employee_name:
        for ent in spacy_model(text).ents:
            if ent.label_ == 'PERSON': employee_name = ent.text; break
    fields['employee_name'] = employee_name
    if employee_name: fields['_confidence']['employee_name'] = 'context-pattern'

    # 3. Employment Period: span lines if needed (capture multi-line dates)
    # Employment period pattern: include years, across line breaks
    period_pattern = re.search(r'from\s+([\d"\w\s]+?)\s+to\s+([\d"\w\s]+?)(?=\s+as\b|\)|$)', text, re.IGNORECASE|re.DOTALL)
    employment_period = None
    if period_pattern:
        start = period_pattern.group(1).replace('\n', ' ').strip()
        end = period_pattern.group(2).replace('\n', ' ').strip()
        employment_period = f"{start} to {end}"
    fields["employment_period"] = employment_period
    if employment_period:
        fields["_confidence"]["employment_period"] = "context-pattern"

    # 4. Designation: find all 'as a/an ...' and choose the longest match
    designation = None
    # Primary: all 'as a/an ...' (stop at comma, period or newline)
    desigs = re.findall(r'as\s+(?:a|an)\s*([A-Za-z ]+?)(?=[,\.\n]|$)', text, re.IGNORECASE)
    if desigs:
        designation = max([d.strip() for d in desigs], key=len)
    # Fallback: 'was ... with'
    if not designation:
        m3 = re.search(r'was\s+([A-Za-z ]+?)\s+with', text, re.IGNORECASE)
        if m3: designation = m3.group(1).strip()
    fields["designation"] = designation
    if designation:
        fields["_confidence"]["designation"] = "context-pattern"

    # 5. Department: match only the keyword
    dept_pattern = re.search(r'\b(?:department|unit|division|diagnostics)\b', text, re.IGNORECASE)
    department = None
    if dept_pattern:
        department = dept_pattern.group(0).capitalize()
    fields["department"] = department
    if department:
        fields["_confidence"]["department"] = "context-pattern"

    # 6. Signatory: look for line starting with Dr.
    signatory = None
    sign_match = re.search(r'^Dr\.[ \t]*([A-Z][A-Za-z .]+)', text, re.MULTILINE)
    if sign_match:
        signatory = 'Dr. ' + sign_match.group(1).strip()
    fields['signatory'] = signatory
    if signatory:
        fields['_confidence']['signatory'] = 'context-pattern'

    # 7. Date of Issuance: try common date patterns, fallback to numeric grouping
    date_of_issuance = None
    # precise date first
    patterns = [re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'), re.compile(r'\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b')]
    for pattern in patterns:
        for l in reversed(lines):
            m = pattern.search(l)
            if m:
                date_of_issuance = m.group(0).strip()
                break
        if date_of_issuance:
            break
    # fallback: numeric grouping (e.g. '2 | -O8.202.')
    if not date_of_issuance:
        for l in reversed(lines):
            nums = re.findall(r'\d+', l)
            if len(nums) >= 3:
                date_of_issuance = f"{nums[-3]}-{nums[-2]}-{nums[-1]}"
                break
    fields['date_of_issuance'] = date_of_issuance
    if date_of_issuance:
        fields['_confidence']['date_of_issuance'] = 'context-pattern'

    # Return all extracted fields
    print("[DEBUG] extract_certificate_fields returning", fields)
    return fields

@app.get("/analytics")
def analytics(current_user: User = Depends(get_current_active_admin), db: Session = Depends(get_db)):
    total = db.query(func.count(VerificationRequest.id)).scalar()
    success = db.query(func.count(VerificationRequest.id)).filter(VerificationRequest.status == "sent").scalar()
    errors = total - success
    common = db.query(VerificationRequest.extraction_error, func.count(VerificationRequest.extraction_error).label("count")).group_by(VerificationRequest.extraction_error).order_by(func.count(VerificationRequest.extraction_error).desc()).limit(5).all()
    return {"total": total, "success": success, "errors": errors, "common_errors": [{"error": e, "count": c} for e, c in common]}
