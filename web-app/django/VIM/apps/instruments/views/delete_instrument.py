"""Django view to handle instrument deletion."""

import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from VIM.apps.instruments.exceptions import (
    InstrumentException,
    NotFoundException,
    PermissionException,
)
from VIM.apps.instruments.error_codes import ErrorCode
from VIM.apps.instruments.models import Instrument
from VIM.apps.instruments.utils.response_helpers import (
    success_response,
    handle_exception,
)
from VIM.apps.instruments.utils.solr_indexer import delete_instrument_from_solr

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["DELETE"])
def delete_instrument(request: HttpRequest, umil_id: str) -> JsonResponse:
    """
    Delete a user-created instrument.

    Only the user who created the instrument (or a superuser) can delete it.
    Wikidata-imported instruments cannot be deleted.

    Args:
        request: HTTP request
        umil_id: UMIL identifier of the instrument to delete

    Returns:
        JsonResponse with success or error status
    """
    try:
        # Fetch the instrument
        try:
            instrument = Instrument.objects.get(umil_id=umil_id)
        except Instrument.DoesNotExist:
            raise NotFoundException(
                ErrorCode.INSTRUMENT_NOT_FOUND,
                f"Instrument with UMIL ID '{umil_id}' does not exist",
                details={"umil_id": umil_id},
            )

        # Only user-created instruments can be deleted
        if not instrument.is_user_created:
            raise PermissionException(
                ErrorCode.PERMISSION_DENIED,
                "Wikidata-imported instruments cannot be deleted",
                details={"umil_id": umil_id},
            )

        # Only the creator or a superuser can delete
        if not (request.user.is_superuser or instrument.created_by == request.user):
            raise PermissionException(
                ErrorCode.PERMISSION_DENIED,
                "You are not allowed to delete this instrument",
                details={
                    "umil_id": umil_id,
                    "created_by": (
                        instrument.created_by.username
                        if instrument.created_by
                        else None
                    ),
                },
            )

        # Store ID before deletion (needed for Solr cleanup)
        instrument_id = instrument.id

        with transaction.atomic():
            # Delete associated AVResources explicitly since FK uses on_delete=SET_NULL.
            # QuerySet.delete() fires post_delete per instance, so django-cleanup
            # will remove the underlying files from disk automatically.
            instrument.avresource_set.all().delete()

            # Delete the instrument (InstrumentNames cascade automatically)
            instrument.delete()

            # Schedule Solr cleanup after transaction commits
            transaction.on_commit(lambda: delete_instrument_from_solr(instrument_id))

        logger.info(
            "User '%s' deleted instrument %s (id=%s)",
            request.user.username,
            umil_id,
            instrument_id,
        )

        return success_response(
            "Instrument deleted successfully",
            redirect_url="/instruments/",
        )

    except (InstrumentException, ValidationError) as e:
        return handle_exception(
            e,
            context="delete_instrument",
            request_user=(
                request.user.username if request.user.is_authenticated else None
            ),
        )
