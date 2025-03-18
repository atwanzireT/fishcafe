from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import letter
from inventory.models import OrderItem, OrderTransaction

# Printing Receipt for order
@login_required(login_url='/user/login/')
def print_order_receipt(request, order_id):
    # Create a buffer to hold the PDF data
    buffer = BytesIO()

    # Define the PDF size (width x height) for a 57 mm wide receipt
    p = canvas.Canvas(buffer, pagesize=(60 * mm, 100 * mm))  # Increased height for more space

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
    p.drawCentredString(28.5 * mm, y, f"Order ID: {order.random_id} - {order.created.strftime('%Y-%m-%d')}")
    y -= 5 * mm
    p.drawCentredString(28.5 * mm, y, f"Customer: {order.customer_name}")
    y -= 8 * mm

    # Order items header with adjusted positions
    p.setFont("Helvetica-Bold", 9)
    p.drawString(1 * mm, y, "Item")
    p.drawString(25 * mm, y, "Qty")  # Moved quantity column further right
    p.drawString(32 * mm, y, "Unit Px")  # Adjusted unit price position
    p.drawRightString(57 * mm, y, "Total")
    y -= 5 * mm

    # # Order items details with reduced font
    # p.setFont("Helvetica-Bold", 9)
    # for item in order_items:
    #     if y < 20 * mm:  # Move to a new page if not enough space
    #         p.showPage()
    #         y = 85 * mm
    #         p.setFont("Helvetica-Bold", 9)

    #     item_total = item.total_price
    #     p.drawString(1 * mm, y, item.menu_item.name[:25])
    #     p.drawString(25 * mm, y, str(item.quantity))
    #     p.drawString(32 * mm, y, f"{item.menu_item.price}")
    #     p.drawRightString(57 * mm, y, f"{item_total}")
    #     y -= 2 * mm
    #     p.line(1 * mm, y - 2, 57 * mm, y - 2) 
    #     y -= 8 * mm
       



    p.setFont("Helvetica-Bold", 9)
    for item in order_items:
        if y < 20 * mm:  # Move to a new page if not enough space
            p.showPage()
            p.setFont("Helvetica-Bold", 9)
            y = 85 * mm

        item_total = item.total_price

        # Wrap item name to fit within the column width
        item_name = item.menu_item.name
        wrapped_name = []
        column_width = 23 * mm  # Adjust column width for the item menu
        while p.stringWidth(item_name, "Helvetica-Bold", 9) > column_width:
            # Find the maximum number of characters that fit within the column width
            for i in range(1, len(item_name) + 1):
                if p.stringWidth(item_name[:i], "Helvetica-Bold", 9) > column_width:
                    wrapped_name.append(item_name[:i - 1])  # Add text up to the previous character
                    item_name = item_name[i - 1:]  # Remaining text
                    break
        wrapped_name.append(item_name)  # Add the remaining text

        # Draw item name and wrap lines if necessary
        for line in wrapped_name:
            p.drawString(1 * mm, y, line)
            y -= 4 * mm  # Adjust line spacing for wrapped text

        # Draw other columns
        p.drawString(25 * mm, y + 4 * mm, str(item.quantity))  # Align with the first line of the name
        p.drawString(32 * mm, y + 4 * mm, f"{item.menu_item.price}")
        p.drawRightString(57 * mm, y + 4 * mm, f"{item_total}")

        # Draw the horizontal line
        p.line(1 * mm, y - 2, 57 * mm, y - 2)
        y -= 5 * mm  # Adjust spacing after each item




    # Total price
    
    y -= 6 * mm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(3 * mm, y, "TOTAL")
    p.drawRightString(45 * mm, y, f"{total_price}")
    y -= 5 * mm

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
    return FileResponse(buffer, as_attachment=True, filename=f"receipt_{order.random_id}.pdf")

