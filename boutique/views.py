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

def appointment(request):

    success = False

    if request.method == 'POST':

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        service = request.POST.get('service')
        notes = request.POST.get('notes')

        try:
            Appointment.objects.create(
                name=name,
                phone=phone,
                email=email or '',
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                service=service or 'Consultation',
                notes=notes or ''
            )
        except Exception as e:
            print(f"[Appointment] Error saving to DB: {e}")

        print("EMAIL PASSWORD EXISTS:", bool(settings.EMAIL_HOST_PASSWORD))

        try:
            connection = get_connection()
            connection.open()
            print("SMTP CONNECTED SUCCESSFULLY")
        except Exception as e:
            print("SMTP CONNECTION ERROR:", repr(e))

        # Email to Admin
        try:
            send_mail(
                subject='New Appointment Request',
                message=f'''
NEW APPOINTMENT BOOKING

Customer Details
----------------
Name: {name}
Phone: {phone}
Email: {email}

Appointment Details
-------------------
Service: {service}
Date: {appointment_date}
Time: {appointment_time}

Additional Notes
----------------
{notes}
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['itzsukhmanidesigner@gmail.com'],
                fail_silently=False,
            )
            print("ADMIN EMAIL SENT")

        except Exception as e:
            print("ADMIN EMAIL ERROR:", repr(e))

        # Email to Customer
        try:
            send_mail(
                subject='Appointment Request Received - Sukhmani Designer',
                message=f'''
Dear {name},

Thank you for choosing Sukhmani Designer.

Your appointment request has been received successfully.

Service: {service}
Date: {appointment_date}
Time: {appointment_time}

Our team will contact you shortly.

Regards,
Sukhmani Designer
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            print("CUSTOMER EMAIL SENT")

        except Exception as e:
            print("CUSTOMER EMAIL ERROR:", repr(e))

        # Automated WhatsApp Alert (Name, Number, Time)
        try:
            date_time_str = f"{appointment_date} at {appointment_time}" if appointment_date and appointment_time else (appointment_time or appointment_date or "Flexible")
            send_whatsapp_alert(name=name, phone=phone, date_time_str=date_time_str)
        except Exception as e:
            print("WHATSAPP ALERT ERROR:", repr(e))

        success = True

    return render(
        request,
        'appointment.html',
        {'success': success}
    )