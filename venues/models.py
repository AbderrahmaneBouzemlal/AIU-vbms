from django.db import models


class VenueCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'venue_category'

    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(VenueCategory, on_delete=models.CASCADE, related_name='venues')
    handled_by = models.CharField(choices=(('sa', 'SA'), ('ppk', 'PPK')), default='sa')
    is_available = models.BooleanField(default=True)
    features = models.JSONField(default=dict)

    class Meta:
        db_table = 'venue'

    def __str__(self):
        return self.name


class VenueAvailability(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'venue_availability'
        unique_together = ['venue', 'date', 'start_time', 'end_time']