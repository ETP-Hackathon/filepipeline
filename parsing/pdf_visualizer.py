import fitz  # PyMuPDF


filename = "../output_searchable.pdf"
doc = fitz.open(filename)
# page = doc[1]

for page in doc[:2]:
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"]
                font = span["font"]
                size = span["size"]
                print(f"Text: {text} | Font: {font} | Size: {size}")