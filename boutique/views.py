from django.shortcuts import render, redirect
from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.contrib import messages
from .models import Appointment, Review
from .whatsapp import send_whatsapp_alert, send_whatsapp_message

def home(request):
    return render(request, 'home.html')

def collections(request):
    return render(request, 'collections.html')

def gallery(request):
    return render(request, 'gallery.html')

def reviews(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        rating_raw = request.POST.get('rating', '5')
        review_text = request.POST.get('review', '').strip()
        try:
            rating = int(rating_raw)
            if rating < 1 or rating > 5:
                rating = 5
        except (ValueError, TypeError):
            rating = 5

        if name and review_text:
            try:
                Review.objects.create(
                    name=name,
                    rating=rating,
                    review=review_text,
                    is_approved=True
                )
                messages.success(request, 'Thank you for sharing your experience! Your review is now live.')
                return redirect('reviews')
            except Exception as e:
                print(f"[Reviews] Error saving review: {e}")

    try:
        all_reviews = list(Review.objects.all().order_by('-created_at'))
    except Exception as e:
        print(f"[Reviews] Table access notice (falling back to default display): {e}")
        all_reviews = []

    return render(request, 'reviews.html', {'reviews': all_reviews})

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def contact(request):
    return render(request, 'contact.html')

import threading
import urllib.parse

def _send_appointment_notifications(name, phone, email, service, appointment_date, appointment_time, notes):
    """Background task to send email and WhatsApp alerts without blocking the web response."""
    # 1. Email to Admin
    if getattr(settings, 'EMAIL_HOST_PASSWORD', None):
        try:
            send_mail(
                subject=f'New Appointment: {name} - Sukhmani Designer',
                message=f'''NEW APPOINTMENT BOOKING

Customer Details:
Name: {name}
Phone: {phone}
Email: {email or 'N/A'}

Appointment Details:
Service: {service}
Date: {appointment_date}
Time: {appointment_time}

Additional Notes:
{notes or 'None'}
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['itzsukhmanidesigner@gmail.com'],
                fail_silently=True,
            )
            print("[Appointment] Admin email sent.")
        except Exception as e:
            print(f"[Appointment] Admin email error: {e}")

        # 2. Email to Customer (if email provided)
        if email:
            try:
                send_mail(
                    subject='Appointment Request Received - Sukhmani Designer',
                    message=f'''Dear {name},

Thank you for choosing Sukhmani Designer.

Your appointment request for {appointment_date} at {appointment_time} ({service}) has been received successfully.

Our team will contact you shortly to confirm your consultation.

Warm regards,
Sukhmani Designer
Phone: +91 98787 76028 / +91 82840 99286
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                print("[Appointment] Customer email sent.")
            except Exception as e:
                print(f"[Appointment] Customer email error: {e}")

    # 3. Automated WhatsApp Alert
    try:
        date_time_str = f"{appointment_date} at {appointment_time}" if appointment_date and appointment_time else (appointment_time or appointment_date or "Flexible")
        send_whatsapp_alert(name=name, phone=phone, date_time_str=date_time_str)
    except Exception as e:
        print(f"[Appointment] WhatsApp alert error: {e}")


def appointment(request):
    success = False
    whatsapp_url = None
    booking_details = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        appointment_date = request.POST.get('appointment_date', '').strip()
        appointment_time = request.POST.get('appointment_time', '').strip()
        service = request.POST.get('service', 'Consultation').strip()
        notes = request.POST.get('notes', '').strip()

        # 1. Save to Database instantly
        if name and phone and appointment_date and appointment_time:
            try:
                Appointment.objects.create(
                    name=name,
                    phone=phone,
                    email=email,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    service=service or 'Consultation',
                    notes=notes
                )
            except Exception as e:
                print(f"[Appointment] DB Error: {e}")

            # 2. Trigger notifications in background thread (never freezes web page)
            t = threading.Thread(
                target=_send_appointment_notifications,
                args=(name, phone, email, service, appointment_date, appointment_time, notes),
                daemon=True
            )
            t.start()

            # 3. Pre-build instant WhatsApp link for the customer
            wa_text = f"Hello Sukhmani Designer, I have booked an appointment.\n\n👤 Name: {name}\n📞 Phone: {phone}\n📅 Date: {appointment_date}\n⏰ Time: {appointment_time}\n👗 Service: {service}"
            if notes:
                wa_text += f"\n📝 Notes: {notes}"
            whatsapp_url = f"https://wa.me/919878776028?text={urllib.parse.quote(wa_text)}"

            booking_details = {
                'name': name,
                'phone': phone,
                'date': appointment_date,
                'time': appointment_time,
                'service': service,
            }
            success = True

    return render(
        request,
        'appointment.html',
        {
            'success': success,
            'whatsapp_url': whatsapp_url,
            'booking_details': booking_details,
        }
    )