from django.db import models
from helpers import get_lat_lng
from image_cropping.fields import ImageRatioField, ImageCropField

# CHOICE FIELDS
SEX_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('T', 'Transgender'),
    ('U', 'Unknown'),
)
INC_TYPE_CHOICES = (
    ('SH', 'Shooting'),
    ('ST', 'Stabbing'),
    ('VH', 'Vehicular'),
    ('OT', 'Other'),
)
STATE_CHOICES = (
    ('DE', 'Delaware'),
    ('PA', 'Pennsylvania'),
    ('NJ', 'New Jersey'),
    ('MD', 'Maryland'),
)


class Incident(models.Model):
    """
    Incident model.
    """
    headline = models.CharField('Headline', max_length=255)
    is_approximate_address = models.BooleanField('Approximate address')
    address = models.CharField(max_length=255, blank=True, help_text="Enter either the Latitude and Longitude <em>OR</em> Address and the following two fields.")
    city = models.CharField(max_length=255, blank=True, default="Wilmington")
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, default="DE")
    latitude = models.CharField('Latitude', blank=True, max_length=100)
    longitude = models.CharField('Longitude', blank=True, max_length=100)
    formatted_address = models.CharField('Formatted Address', blank=True, max_length=255)
    inc_date = models.DateField('Incident Date')
    inc_time = models.TimeField('Incident Time', null=True, blank=True)
    inc_type = models.CharField('Incident Type', max_length=2, choices=INC_TYPE_CHOICES)
    is_homicide = models.BooleanField('Homicide')
    victim_count = models.IntegerField('No. of Victims', max_length=12, blank=True, null=True)
    killed_count = models.IntegerField('No. of Killed', max_length=12, blank=True, null=True, default="0")
    is_victims_unknown = models.BooleanField('Victims not identified')
    summary = models.TextField('Incident Summary', blank=True, help_text="Give just the details. Try to keep it under 5 grafs.")
    suspect_count = models.IntegerField('No. of Arrests', max_length=12, blank=True, null=True, default=0)
    is_suspects_unknown = models.BooleanField('Suspects not identified')
    suspects = models.ManyToManyField('Suspect', null=True, blank=True)
    victims = models.ManyToManyField('Victim', blank=True, null=True)
    inc_slug = models.SlugField('Slug')

    def __unicode__(self):
        return self.headline

    def _get_full_address(self):
        return u'%s %s %s' % (self.address, self.city, self.state)
    full_address = property(_get_full_address)

    def save(self, *args, **kwargs):
        if not self.latitude and not self.longitude:
            location = '+'.join(filter(None, (self.address, self.city, self.state)))
            self.latitude, self.longitude, self.formatted_address = get_lat_lng(location)
        super(Incident, self).save(*args, **kwargs)


def uploadVicPhoto(instance, filename):
    """
    Returns a directory structure like so:
    ../victim_photos/<Filename>
    """
    return 'victim_photos/%s' % (filename)


class Victim(models.Model):
    """
    Victim Model
    """
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    age = models.IntegerField('Age', max_length=3, blank=True, null=True)
    sex = models.CharField('Sex', max_length=1, choices=SEX_CHOICES)
    is_killed = models.BooleanField('This person was killed')
    is_unidentified = models.BooleanField('Unidentified')
    victim_photo = ImageCropField('Victim Photo', upload_to=uploadVicPhoto, null=True, blank=True)
    cropping = ImageRatioField('victim_photo', '300x400')
    about = models.TextField('Victim Info.', null=True, blank=True)
    vic_slug = models.SlugField()

    def __unicode__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def get_full_name(self):
        """
            Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


def uploadSuspectPhoto(instance, filename):
    """
    Returns a directory structure like so:
    ../suspect_photos/<Filename>
    """
    return 'suspect_photos/%s' % (filename)


class Suspect(models.Model):
    """
    Suspect Model
    """
    first_name = models.CharField('First Name', max_length=100)
    last_name = models.CharField('Last Name', max_length=100)
    age = models.IntegerField('Age', max_length=3, blank=True, null=True)
    sex = models.CharField('Sex', max_length=1, choices=SEX_CHOICES)
    arrest_date = models.DateField('Arrest Date', null=True, blank=True)
    is_unidentified = models.BooleanField('Unidentified')
    suspect_photo = ImageCropField('Suspect Photo', upload_to=uploadSuspectPhoto, null=True, blank=True)
    cropping = ImageRatioField('suspect_photo', '300x400')
    about = models.TextField('Suspect Info.', null=True, blank=True)
    suspect_slug = models.SlugField()

    def __unicode__(self):
        return "%s, %s" % (self.last_name, self.first_name)

    def get_full_name(self):
        """
            Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
