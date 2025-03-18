from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from inventory.models import OrderItem

@login_required(login_url='/user/login/')
def print_order(request, id):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Define the PDF size (57mm wide, height dynamically adjustable)
    receipt_width = 57 * mm
    initial_height = 100 * mm
    line_height = 5 * mm

    # Retrieve the order by ID and the related order items
    try:
        order = OrderItem.objects.get(id=id)
    except OrderItem.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    # Dynamically calculate the receipt height based on content
    total_lines = 15  # Adjust this based on content (e.g., 15 lines = base height)
    receipt_height = initial_height + (line_height * total_lines)

    # Create the PDF canvas
    p = canvas.Canvas(buffer, pagesize=(receipt_width, receipt_height))

    # Set starting Y position near the top
    y = receipt_height - 10 * mm  # Start 10mm from the top

    # Business header
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(receipt_width / 2, y, "FishPoint Cafe And Lounge")
    y -= 6 * mm
    p.setFont("Helvetica", 7)
    p.drawCentredString(receipt_width / 2, y, "Tel: +256771207212 / 709663814")
    y -= 8 * mm

    # Receipt Title
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(receipt_width / 2, y, "RECEIPT")
    y -= 8 * mm

    # Order and customer details
    p.setFont("Helvetica-Bold", 7)
    p.drawString(2 * mm, y, f"Order ID: {order.order.random_id}")
    y -= 5 * mm
    p.drawString(2 * mm, y, f"Customer: {order.customer_name}")
    y -= 5 * mm
    p.drawString(2 * mm, y, f"Date: {order.order_date.strftime('%Y-%m-%d')}")
    y -= 6 * mm

    # Items Section Header
    p.setFont("Helvetica-Bold", 7)
    p.drawString(2 * mm, y, "Item")
    p.drawString(32 * mm, y, "Qty")
    p.drawString(38 * mm, y, "OrderType")
    y -= 6 * mm

    # Items in the order
    p.setFont("Helvetica", 8)
    p.drawString(2 * mm, y, f"{order.menu_item}")
    p.drawString(32 * mm, y, f"{order.quantity}")
    p.drawString(38 * mm, y, f"{order.order_type}")
    y -= 6 * mm

    # Special Notes
    if order.special_notes:
        y -= 3 * mm  # Extra spacing for special notes section
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(5 * mm, y, "Special Notes:")
        y -= 4 * mm
        p.setFont("Helvetica", 8)
        p.drawString(5 * mm, y, order.special_notes[:50])  # Limit notes length to avoid overflow
        y -= 6 * mm

    # Footer
    p.setFont("Helvetica-Bold", 7)
    p.drawCentredString(receipt_width / 2, y, "Thank you for dining with us!")
    y -= 5 * mm
    p.setFont("Helvetica", 8)
    p.drawCentredString(receipt_width / 2, y, f"Served by: {order.order.created_by.username}")

    # Finalize and close the PDF
    p.showPage()
    p.save()

    # Return PDF as response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"receipt_{order.id}.pdf")
