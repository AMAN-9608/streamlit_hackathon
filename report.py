from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib.units import inch

# Create a function to add a page to the PDF with two columns
def add_page_with_columns(doc, image_path, text):
    # Create a two-column table
    data = [
        [Image(image_path, width=1.5 * inch, height=2 * inch), text]
    ]
    table = Table(data, colWidths=[2 * inch, 4 * inch])

    # Define table style (border, alignment, etc.)
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
    ])
    table.setStyle(style)

    # Add the table to the document and create a new page
    doc.build([table, Spacer(1, 0.25 * inch)])

# Create a PDF document
pdf_filename = "two_column_pdf.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

# Add pages with content
add_page_with_columns(doc, "image1.jpg", "Text for Image 1 goes here.")
add_page_with_columns(doc, "image2.jpg", "Text for Image 2 goes here.")
add_page_with_columns(doc, "image3.jpg", "Text for Image 3 goes here.")

# Save the PDF
doc.build([])
