from django.shortcuts import render, redirect
from .models import Appointment
from django.core.mail import send_mail
from django.conf import settings
def home(request):
    return render(request, 'home.html')


def collections(request):
    return render(request, 'collections.html')

def gallery(request):
    return render(request, 'gallery.html')


from .models import Review

def reviews(request):
    if request.method == 'POST':
        Review.objects.create(
            name=request.POST.get('name'),
            rating=request.POST.get('rating'),
            review=request.POST.get('review'),
            is_approved=False  # always pending by default
        )
    all_reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'reviews.html', {'reviews': all_reviews})



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

        Appointment.objects.create(
            name=name,
            phone=phone,
            email=email,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            service=service,
            notes=notes
        )

        print("EMAIL PASSWORD EXISTS:", bool(settings.EMAIL_HOST_PASSWORD))
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
            print("ADMIN EMAIL ERROR:", e)

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
            print("CUSTOMER EMAIL ERROR:", e)

        success = True

    return render(
        request,
        'appointment.html',
        {'success': success}
    )