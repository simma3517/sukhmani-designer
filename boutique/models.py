from django.db import models

class Appointment(models.Model):
    SERVICE_CHOICES = [
        ('Bridal Consultation', 'Bridal Consultation'),
        ('Punjabi Suit Design', 'Punjabi Suit Design'),
        ('Party Wear Styling', 'Party Wear Styling'),
        ('Custom Tailoring', 'Custom Tailoring'),
        ('Measurement Appointment', 'Measurement Appointment'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name



class Review(models.Model):
    name       = models.CharField(max_length=100)
    rating     = models.PositiveSmallIntegerField()
    review     = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.rating}★"