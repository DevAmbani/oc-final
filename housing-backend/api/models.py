from django.db import models


class ScrappedData(models.Model):
    url = models.CharField(max_length=255)
    description = models.TextField()
    issue = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.url


class OpenAIAnalysis(models.Model):
    url = models.CharField(max_length=255)
    description = models.TextField()
    religion = models.TextField()
    race_color_national_origin = models.TextField()
    sex_gender_preferences = models.TextField()
    disability = models.TextField()
    familial_status = models.TextField()
    source_of_income = models.TextField()
    arrest_conviction_records = models.TextField()
    eviction_history = models.TextField()
    credit_score_employment = models.TextField()
    coded_language = models.TextField()
    discriminatory = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.url


class NewOpenAIAnalysis(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    analysis = models.TextField(null=True, blank=True)  # Store full analysis if needed
    comments = models.JSONField(null=True, blank=True)  # Store comments as JSON
    categories = models.JSONField(null=True, blank=True)  # Store categories as JSON
    flagged = models.BooleanField(default=False)
    isDiscriminatory = models.CharField(max_length=255, null=True, blank=True)