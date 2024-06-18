"""
Module for custom error views.
"""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# pylint: disable=unused-argument
def custom_404_page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponse:
    """
    Custom view to handle 404 errors.

    Args:
        request (HttpRequest): The request object.
        exception (Exception): The exception that triggered the 404 error.

    Returns:
        HttpResponse: Rendered 404 error page.
    """
    return render(request, "404.html", status=404)
