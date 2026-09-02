from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil, os, uuid

router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    property_code: str = Form(...),
    property_address: str = Form(None),
    document_type: str = Form(...),
    created_by: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are permitted.")

    unique_filename = f"{property_code}_{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Document uploaded successfully", "path_url": f"/{file_path}"}

@router.get("/by-property/{property_code}")
async def get_property_documents(property_code: str):
    # Query database for all documents with matching property_code
    return []