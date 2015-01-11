from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from events.classes import Event

event_document_create = Event(name='documents_document_create', label=_('Document created'))
event_document_edited = Event(name='documents_document_edit', label=_('Document edited'))
