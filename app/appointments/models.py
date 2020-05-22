from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .choices import STATUS_CHOICES

# Create your models here.

class Appointment(models.Model):
    """ A model based on a simple doctor appointment """
    pediatrician_first_name = models.CharField(
        max_length=50, 
        null=True, 
        blank=True
    )
    pediatrician_last_name = models.CharField(
        max_length=50, 
        null=True, 
        blank=True
    )
    comment = models.TextField(max_length=240, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    appointment_request = models.OneToOneField(
        "appointments.AppointmentRequest", 
        on_delete=models.CASCADE, 
        related_name='appointment'
    )
    status = models.CharField(
        max_length=3, 
        choices=STATUS_CHOICES, 
        default='REQ'
    )

    def __str__(self):
        if self.status == 'SEN':
            return (
                'Cita para ' + self.appointment_request.first_name + ' ' 
                + self.appointment_request.last_name + ' con el Doctor ' 
                + self.pediatrician_first_name + ' ' 
                + self.pediatrician_last_name + ' el '
                + str(self.date)
            )
        else:
            return (
                'Cita para ' + self.appointment_request.first_name + ' ' 
                + self.appointment_request.last_name 
                + ' pendiente de asignación.'
            )
    
    @property
    def is_completed(self):
        """
        Property that returns true if all fields of the instance are populated
        or returns a list of non-populated fields
        """
        fields_to_complete = []
        if self.pediatrician_first_name is None:
            fields_to_complete.append('Nombre del pediatra')
        if self.pediatrician_last_name is None:
            fields_to_complete.append('Apellido del pediatra')
        if self.date is None:
            fields_to_complete.append('Fecha de la consulta')
        if len(fields_to_complete) > 0:
            return fields_to_complete
        else:
            return True



class AppointmentRequest(models.Model):
    """ A model for appointment requests performed by a patient """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.email

@receiver(post_save, sender=AppointmentRequest)
def create_appointment(sender, instance, **kwargs):
    """ 
    Django signal that creates an Appointment instance after the AppointmentRequest is created
    """
    Appointment.objects.create(**{'appointment_request': instance})