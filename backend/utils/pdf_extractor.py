import pdfplumber
import os

def extract_text_from_pdf(file_path: str) -> dict:
    """Extract text content from a PDF file."""
    if not os.path.exists(file_path):
        return {"success": False, "error": "File not found", "text": ""}
    
    try:
        extracted_text = []
        page_count = 0
        
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text.strip())
        
        full_text = "\n\n".join(extracted_text)
        
        return {
            "success": True,
            "text": full_text,
            "page_count": page_count,
            "word_count": len(full_text.split()) if full_text else 0
        }
    except Exception as e:
        return {"success": False, "error": str(e), "text": ""}

def compare_reports(text1: str, text2: str) -> dict:
    """Compare two report texts and generate a summary of differences."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    common = words1 & words2
    only_in_first = words1 - words2
    only_in_second = words2 - words1
    
    # Filter meaningful words (length > 4)
    meaningful_new = [w for w in only_in_second if len(w) > 4][:10]
    meaningful_removed = [w for w in only_in_first if len(w) > 4][:10]
    
    similarity = len(common) / max(len(words1 | words2), 1) * 100
    
    return {
        "similarity_percentage": round(similarity, 2),
        "new_terms": meaningful_new,
        "removed_terms": meaningful_removed,
        "summary": f"Reports are {round(similarity, 1)}% similar. "
                   f"{'New findings detected.' if meaningful_new else 'No significant new findings.'} "
                   f"{'Some previous findings not present.' if meaningful_removed else ''}"
    }
