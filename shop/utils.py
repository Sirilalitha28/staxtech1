from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from decimal import Decimal

def generate_invoice_pdf(order):
    # PDF file path
    file_name = f"invoice_{order.id}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    # Create PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "INVOICE")
    y -= 30

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Order ID: {order.id}")
    y -= 20
    c.drawString(50, y, f"Customer: {order.user.username}")
    y -= 20
    c.drawString(50, y, f"Date: {order.created_at.strftime('%d %b %Y, %I:%M %p')}")
    y -= 40

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product")
    c.drawString(300, y, "Quantity")
    c.drawString(400, y, "Price")
    y -= 20
    c.line(50, y, 550, y)
    y -= 20

    c.setFont("Helvetica", 12)
    for item in order.orderitem_set.all():
        c.drawString(50, y, item.product.name)
        c.drawString(300, y, str(item.quantity))
        c.drawString(400, y, f"{item.price} ₹")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    y -= 20
    c.line(50, y, 550, y)
    y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Total Amount: ₹ {order.total_price}")

    c.save()
    return file_name
