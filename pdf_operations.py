import fitz  # PyMuPDF
import PyPDF2
import os
from pdf2docx import Converter
from PyPDF2 import PdfReader, PdfWriter

def merge_pdfs(pdf_list, output_filename):
    """
    Merge multiple PDFs in the specified order and save as a new file.
    """
    merger = PyPDF2.PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()

def convert_pdf_to_docx(pdf_path, output_filename):
    """
    Convert a PDF to a DOCX file.
    """
    cv = Converter(pdf_path)
    cv.convert(output_filename, start=0, end=None)  # Convert entire document
    cv.close()

def remove_pages(pdf_path, pages_to_remove, output_filename):
    """
    Remove specific pages from a PDF.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    pdf_writer = PyPDF2.PdfWriter()

    pages_to_remove = [int(p) - 1 for p in pages_to_remove]  # Convert to 0-based index

    for i in range(len(pdf_reader.pages)):
        if i not in pages_to_remove:
            pdf_writer.add_page(pdf_reader.pages[i])

    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

def set_pdf_permissions(pdf_path, permissions, output_filename):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # Copy pages from reader to writer
    for page in reader.pages:
        writer.add_page(page)
    
    # Calculate permissions flags - we need to use standard PDF permissions flags
    # These are defined in the PDF specification
    # Start with all permissions disabled
    permissions_flag = 0
    
    # Add permission flags based on what's allowed
    if "/Print" in permissions:
        permissions_flag |= 4  # Print permission bit
    
    if "/Modify" in permissions:
        permissions_flag |= 8  # Modify contents permission bit
    
    if "/Copy" in permissions:
        permissions_flag |= 16  # Extract/copy text and graphics permission bit
    
    if "/Annotate" in permissions:
        permissions_flag |= 32  # Annotate permission bit
    
    # Apply encryption with the permissions flags
    writer.encrypt(
        user_password="",  # Empty user password allows opening
        owner_password="owner123",  # Owner password needed to change restrictions
        use_128bit=True,  # Use stronger encryption
        permissions_flag=permissions_flag  # Apply permissions using the numeric flag
    )
    
    # Save the new PDF
    with open(output_filename, "wb") as output_pdf:
        writer.write(output_pdf)

def password_protect_pdf(pdf_path, password, output_filename):
    """
    Add password protection to a PDF file.
    """
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    pdf_writer = PyPDF2.PdfWriter()

    for page in pdf_reader.pages:
        pdf_writer.add_page(page)

    pdf_writer.encrypt(password)

    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
