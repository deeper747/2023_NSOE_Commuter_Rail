import fitz
import glob
import os

def extract_page_7(pdf_file, output_folder):
    doc = fitz.open(pdf_file)
    if doc.page_count >= 7:
        page = doc[-1]  # Last page

        # Get the pixmap of the page
        copy = page.get_pixmap(dpi = 144)

        # Create a new document
        new_doc = fitz.open()

        # Add a new blank page with the same dimensions as the original page
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)

        # Scale and paste the pixmap onto the new page
        rect = (0, 0, page.rect.width, page.rect.height)
        new_page.insert_image(rect = rect, 
                              pixmap = copy,
                              xref = 0) 
        # Documentation: https://pymupdf.readthedocs.io/en/latest/page.html#Page.insert_image

        # Save the new document as a PDF file
        output_file = os.path.join(output_folder, f"RouteLevelReport_{os.path.basename(pdf_file)}")
        new_doc.save(output_file)
        new_doc.close()

def main():
    # Define the file path patterns
    file_path_pattern = "../01_Data/01_Source/Amtrak/Monthly_Performance_Report/*/Amtrak-Monthly-Performance-Report-*-*.pdf"

    # Output folder for extracted pages
    output_folder = "../01_Data/01_Source/Amtrak/RouteLevelReport"

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get a list of PDF files matching the pattern
    pdf_files = glob.glob(file_path_pattern)

    for pdf_file in pdf_files:
        extract_page_7(pdf_file, output_folder)

if __name__ == "__main__":
    main()
