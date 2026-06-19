import fitz          
import base64        
import io            
from config import MAX_PAGES   


def extract_text_from_pdf(pdf_file) -> str:
    """
    Reads a PDF file and extracts all the text from it.
    
    What is 'pdf_file'?
    - It's the uploaded file from Streamlit (st.file_uploader)
    - We need to read its bytes (raw content) to process it
    
    Returns:
    - A single string with all the text from the PDF
    """
    
    pdf_bytes = pdf_file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    extracted_text = ""
    
    total_pages = min(len(doc), MAX_PAGES)
    
    for page_num in range(total_pages):
        page = doc[page_num]
        
        page_text = page.get_text()
        
        # Add page number so we know where text came from
        extracted_text += f"\n--- Page {page_num + 1} ---\n"
        extracted_text += page_text
    
    # Close the document to free memory
    doc.close()
    
    # Clean up the text a little bit
    # Strip removes extra spaces at start and end
    extracted_text = extracted_text.strip()
    
    # If no text was found (might be a scanned PDF), say so
    if not extracted_text:
        extracted_text = "No text could be extracted from this PDF. It may be a scanned image."
    
    return extracted_text


def extract_images_from_pdf(pdf_file) -> list:
    """
    Reads a PDF file and extracts images from it.
    
    Images are converted to base64 strings so we can send them to Groq.
    Base64 is a way to represent binary data (like images) as text.
    
    Returns:
    - A list of base64 encoded image strings
    - Example: ["iVBORw0KGgo...", "R0lGODlh..."]
    """
    
    # Reset file position to start (important if extract_text already read it)
    # seek(0) moves the reading cursor back to the beginning of the file
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    
    # Open the PDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # This will hold base64 strings of all images found
    images_base64 = []
    
    # We limit to 5 images to avoid sending too much data to Groq
    max_images = 5
    image_count = 0
    
    # Loop through each page
    total_pages = min(len(doc), MAX_PAGES)
    
    for page_num in range(total_pages):
        # Stop if we already have enough images
        if image_count >= max_images:
            break
            
        page = doc[page_num]
        
        # get_images() returns a list of image references on this page
        # full=True gives us complete image information
        image_list = page.get_images(full=True)
        
        for img_info in image_list:
            if image_count >= max_images:
                break
            
            try:
                # img_info[0] is the image reference number (xref)
                xref = img_info[0]
                
                # extract_image() gives us the image data
                base_image = doc.extract_image(xref)
                
                # Get the raw image bytes
                image_bytes = base_image["image"]
                
                # b64encode() converts bytes to base64 bytes
                # decode("utf-8") converts base64 bytes to a string
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                
                # Add to our list
                images_base64.append(image_base64)
                image_count += 1
                
            except Exception as e:
                # If one image fails, skip it and continue with others
                print(f"Could not extract image on page {page_num + 1}: {e}")
                continue
    
    doc.close()
    return images_base64


def get_pdf_info(pdf_file) -> dict:
    """
    Gets basic information about a PDF like number of pages, title etc.
    This is used to show file details in the Streamlit app.
    
    Returns:
    - A dictionary with PDF metadata
    """
    
    # Reset file position
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Get metadata (title, author, etc.) stored inside the PDF
    metadata = doc.metadata
    
    info = {
        "pages": len(doc),                                    # Total number of pages
        "title": metadata.get("title", "Unknown"),           # PDF title if available
        "author": metadata.get("author", "Unknown"),         # PDF author if available
        "file_name": pdf_file.name,                          # Original filename
        "file_size_kb": round(len(pdf_bytes) / 1024, 2)     # File size in KB
    }
    
    doc.close()
    return info


def parse_pdf(pdf_file) -> dict:
    """
    Main function that extracts EVERYTHING from a PDF.
    This combines text extraction and image extraction into one call.
    
    This is what we call from other files - it's the main entry point.
    
    Returns:
    - A dictionary with 'text', 'images', and 'info'
    """
    
    # Get basic PDF information
    info = get_pdf_info(pdf_file)
    
    # Extract text (resets file position internally)
    pdf_file.seek(0)
    text = extract_text_from_pdf(pdf_file)
    
    # Extract images
    pdf_file.seek(0)
    images = extract_images_from_pdf(pdf_file)
    
    return {
        "text": text,          
        "images": images,      
        "info": info            
    }
