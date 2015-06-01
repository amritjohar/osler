from django.db import models
from django.core.exceptions import ValidationError
from django.forms import ModelForm
import django.utils.timezone
# Create your models here.


def validate_zip(value):
    '''verify that the given value is in the ZIP code format'''
    if len(str(value)) != 5:
        raise ValidationError('{0} is not a valid ZIP, because it has {1} digits.'.format(
                              str(value), len(str(value))))

    if not str(value).isdigit():
        raise ValidationError("%s is not a valid ZIP, because it contains non-digit characters." %
                              value)


class Language(models.Model):
    language_name = models.CharField(max_length=50, primary_key=True)

    def __unicode__(self):
        return self.language_name


class Ethnicity(models.Model):
    ethnicity_name = models.CharField(max_length=50)


class ActionInstruction(models.Model):
    instruction = models.CharField(max_length=50)

    def __unicode__(self):
        return self.instruction


class ProviderType(models.Model):
    long_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)


class Gender(models.Model):
    long_name = models.CharField(max_length=30)
    short_name = models.CharField(max_length=1)


class Person(models.Model):

    class Meta:
        abstract = True

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50)

    gender_type = models.ForeignKey(Gender)

    def name(self, reverse=True, middle_short=False):
        if self.middle_name:
            if middle_short:
                middle = self.middle_name[0]+"."
            else:
                middle = self.middle_name
        else:
            middle = ""

        if reverse:
            return " ".join([self.last_name+",",
                             self.first_name,
                             middle])
        else:
            return " ".join([self.first_name,
                             middle,
                             self.last_name])


class Patient(Person):
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50,
                            default="St. Louis")
    state = models.CharField(max_length=2,
                             default="MO")
    zip_code = models.CharField(max_length=5,
                                validators=[validate_zip])

    date_of_birth = models.DateField()
    language = models.ForeignKey(Language)

    ethnicity = models.ForeignKey(Ethnicity)

    def age(self):
        import datetime
        return (datetime.date.today()-self.date_of_birth).days/365

    def notes(self):
        l = []
        l.extend(self.followup_set)
        l.extend(self.workup_set)
        return l.sort(key=lambda(k): k.date)

    def __unicode__(self):
        return self.name()


class Provider(Person):

    email = models.EmailField()


class ClinicType(models.Model):
    name = models.CharField(max_length=50)


class ClinicDate(models.Model):
    clinic_type = models.ForeignKey(ClinicType)

    clinic_date = models.DateField()
    gcal_id = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.clinic_type)+" ("+str(self.clinic_date)+")"


class Note(models.Model):
    class Meta:
        abstract = True

    author = models.ForeignKey(Provider)
    author_type = models.ForeignKey(ProviderType)
    patient = models.ForeignKey(Patient)


# class Documents(Note):
#     image
#     comments
#     title
#     upload type (i.e. lab, prescription)


class ActionItem(Note):
    written_date = models.DateTimeField(default=django.utils.timezone.now)
    next_action = models.DateField()
    comments = models.CharField(max_length=300)
    instruction = models.ForeignKey(ActionInstruction)
    done = models.BooleanField(default=False)

    def __unicode__(self):
        return "AA: "+self.instruction+" on "+str(self.next_action)


class Workup(Note):
    clinic_day = models.ForeignKey(ClinicDate)

    #TODO: careteam

    CC = models.CharField(max_length=300)
    #TODO: CC categories (ICD10?)

    HandP = models.TextField()
    AandP = models.TextField()

    #TODO: diagnosis categories (ICD10?)
    diagnosis = models.CharField(max_length=100)

    plan = models.TextField()

    # def __unicode__(self):
    #     return "Workup: "+self.patient.name()+" on "+str(self.clinic_day.date)

    def date(self):
        import datetime
        return datetime.date(self.clinic_day.date)


class Followup(Note):
    note = models.TextField()

    written_date = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return "Followup: "+self.patient.name()+" on "+str(self.written_date)

    def date(self):
        import datetime
        return datetime.date(self.written_date)
