from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, StaffProfile, AdminProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'staff':
            StaffProfile.objects.create(user=instance, staff_id='STAFF' + str(instance.id))
        elif instance.user_type == 'admin':
            AdminProfile.objects.create(user=instance, admin_id='ADMIN' + str(instance.id))
        else:
            StudentProfile.objects.create(user=instance, student_id='AIU' + str(instance.id))


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    if not created:
        if instance.user_type == 'student':
            try:
                if hasattr(instance, 'profile'):
                    instance.profile.save()
            except StudentProfile.DoesNotExist:
                StudentProfile.objects.create(user=instance, student_id='AIU' + str(instance.id))

        elif instance.user_type == 'staff':
            try:
                if hasattr(instance, 'profile'):
                    instance.profile.save()
            except StaffProfile.DoesNotExist:
                StaffProfile.objects.create(user=instance, staff_id='STAFF' + str(instance.id))

        elif instance.user_type == 'admin':
            try:
                if hasattr(instance, 'profile'):
                    instance.profile.save()
            except AdminProfile.DoesNotExist:
                AdminProfile.objects.create(user=instance, admin_id='ADMIN' + str(instance.id))
