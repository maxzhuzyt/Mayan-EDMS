import logging
import uuid
from django.apps import apps
from django.core.files import File
from django.db import models, transaction
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _
from mayan.apps.common.signals import signal_mayan_pre_save
from ..events import (
    event_document_create, event_document_properties_edit,
    event_document_trashed, event_document_type_changed,
)
from ..literals import DEFAULT_LANGUAGE
from ..managers import DocumentManager, PassthroughManager, TrashCanManager
from ..signals import post_document_type_change
from .document_type_models import DocumentType
class Review(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text=_(
            'UUID of a review, universally Unique ID. An unique identifier '
            'generated for each document.'
        ), verbose_name=_('UUID')
    )
    document = models.ForeignKey(
        help_text=_('The documents that this review is for'),
    )
    date_added = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'The server date and time when the review was finally '
            'processed and added to the system.'
        ), verbose_name=_('Added')
    )
    gpa_score = models.IntegerField(
        blank=True, default=0, editable=True, help_text=_(
            'score for gpa'
        )
    )
    skills_score = models.IntegerField(
        blank=True, default=0, editable=True, help_text=_(
            'score for skills'
        )
    )
    experience_score = models.IntegerField(
        blank=True, default=0, editable=True, help_text=_(
            'score for experience'
        )
    )