from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from inventory.models import OrderItem, OrderTransaction

# Printing Invoice
@login_required(login_url='/user/login/')
def print_order_invoice(request, order_id):
  # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Define the PDF size (width x height) for a 57 mm wide receipt
    p = canvas.Canvas(buffer, pagesize=(57 * mm, 100 * mm))  # Increased height for more space

    # Retrieve the order by ID and the related order items
    try:
        order = OrderTransaction.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        total_price = sum(item.total_price for item in order_items)
    except OrderTransaction.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

    # Set starting Y position near the top
    y = 85 * mm

    # Business header (Receipt Title)
    p.setFont("Helvetica-Bold", 13)  # Reduced font size for title
    p.drawCentredString(28.5 * mm, y, "RECEIPT")  # Centered for 57 mm width
    y -= 6 * mm  # Reduced spacing

    # Business name and contact
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(28.5 * mm, y, "Fish Cafe And Lounge")
    y -= 4 * mm
    p.setFont("Helvetica", 7)
    p.drawCentredString(28.5 * mm, y, "Tel: +256771207212 / 709663814")
    y -= 6 * mm

    # Order and customer details
    p.setFont("Helvetica-Bold", 7)
    p.drawString(2 * mm, y, f"Order ID: {order.random_id} - {order.created.strftime('%Y-%m-%d')}")
    y -= 5 * mm
    p.drawString(2 * mm, y, f"Customer: {order.customer_name}")
    y -= 6 * mm

    # Order items header with adjusted positions
    p.setFont("Helvetica-Bold", 8)
    p.drawString(2 * mm, y, "Item")
    p.drawString(20 * mm, y, "Qty")  # Moved quantity column further right
    p.drawString(27 * mm, y, "Unit Px")  # Adjusted unit price position
    p.drawRightString(47 * mm, y, "Total")
    y -= 5 * mm

    # Order items details with reduced font
    p.setFont("Helvetica", 6)
    for item in order_items:
        if y < 20 * mm:  # Move to a new page if not enough space
            p.showPage()
            y = 85 * mm

        item_total = item.total_price
        p.drawString(2 * mm, y, item.menu_item.name[:25])
        p.drawString(20 * mm, y, str(item.quantity))
        p.drawString(27 * mm, y, f"{item.menu_item.price}")
        p.drawRightString(47 * mm, y, f"{item_total}")
        y -= 5 * mm

    # Total price
    p.line(3 * mm, y, 50 * mm, y)
    y -= 3 * mm
    p.setFont("Helvetica-Bold", 9)
    p.drawString(3 * mm, y, "TOTAL")
    p.drawRightString(45 * mm, y, f"{total_price}")
    y -= 6 * mm

    # Footer
    p.setFont("Helvetica-Oblique", 7)
    p.drawCentredString(28.5 * mm, y, "Thank you for dining with us!")
    y -= 4 * mm
    p.drawCentredString(28.5 * mm, y, f"Served by: {order.created_by}")

    # Finalize and close the PDF
    p.showPage()
    p.save()

    # Return PDF as response
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"invoice_{order.random_id}.pdf")
