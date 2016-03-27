from __future__ import unicode_literals

import logging

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _

from acls import ModelPermission
from common import (
    MayanAppConfig, menu_object, menu_sidebar
)
from common.widgets import two_state_template
from mayan.celery import app
from navigation import SourceColumn

from .handlers import unverify_signatures, verify_signatures
from .links import (
    link_document_version_signature_delete,
    link_document_version_signature_details,
    link_document_version_signature_download,
    link_document_version_signature_list,
    link_document_version_signature_upload,
)
from .permissions import (
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_view,
)

logger = logging.getLogger(__name__)


class DocumentSignaturesApp(MayanAppConfig):
    app_namespace = 'signatures'
    app_url = 'signatures'
    name = 'document_signatures'
    test = True
    verbose_name = _('Document signatures')

    def ready(self):
        super(DocumentSignaturesApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        Key = apps.get_model(
            app_label='django_gpg', model_name='Key'
        )

        DetachedSignature = self.get_model('DetachedSignature')

        EmbeddedSignature = self.get_model('EmbeddedSignature')

        SignatureBaseModel = self.get_model('SignatureBaseModel')

        DocumentVersion.register_post_save_hook(
            order=1, func=EmbeddedSignature.objects.create
        )
        DocumentVersion.register_pre_open_hook(
            order=1, func=EmbeddedSignature.objects.open_signed
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_version_signature_delete,
                permission_document_version_signature_download,
                permission_document_version_signature_view,
                permission_document_version_signature_upload,
            )
        )

        SourceColumn(
            source=SignatureBaseModel, label=_('Date'), attribute='date'
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Key ID'), attribute='key_id'
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Signature ID'),
            func=lambda context: context['object'].signature_id or _('None')
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Public key fingerprint'),
            func=lambda context: context['object'].public_key_fingerprint or _('None')
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Is embedded?'),
            func=lambda context: two_state_template(
                SignatureBaseModel.objects.get_subclass(
                    pk=context['object'].pk
                ).is_embedded
            )
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Is detached?'),
            func=lambda context: two_state_template(
                SignatureBaseModel.objects.get_subclass(
                    pk=context['object'].pk
                ).is_detached
            )
        )

        app.conf.CELERY_QUEUES.append(
            Queue(
                'signatures', Exchange('signatures'), routing_key='signatures'
            ),
        )

        app.conf.CELERY_ROUTES.update(
            {
                'document_signatures.tasks.task_verify_signatures': {
                    'queue': 'signatures'
                },
                'document_signatures.tasks.task_unverify_signatures': {
                    'queue': 'signatures'
                },
            }
        )

        menu_object.bind_links(
            links=(link_document_version_signature_list,),
            sources=(DocumentVersion,)
        )
        menu_object.bind_links(
            links=(
                link_document_version_signature_details,
                link_document_version_signature_download,
                link_document_version_signature_delete,
            ), sources=(SignatureBaseModel,)
        )
        menu_sidebar.bind_links(
            links=(
                link_document_version_signature_upload,
            ), sources=(DocumentVersion,)
        )
        post_delete.connect(
            unverify_signatures,
            dispatch_uid='unverify_signatures',
            sender=Key
        )
        post_save.connect(
            verify_signatures,
            dispatch_uid='verify_signatures',
            sender=Key
        )
