"""
URL configuration for VIM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from VIM.apps.instruments.views.instrument_list import InstrumentList
from VIM.apps.instruments.views.instrument_detail import InstrumentDetail
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("VIM.apps.main.urls", namespace="main")),
    path("instruments/", InstrumentList.as_view(), name="instrument-list"),
    path("instrument/<int:pk>/", InstrumentDetail.as_view(), name="instrument-detail"),
    prefix_default_language=False,
)


if settings.IS_DEVELOPMENT:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]


###############################################################
#                     Custom error handlers                   #
# These handlers define custom views to be displayed for      #
# specific HTTP error responses.                              #
###############################################################
# pylint: disable=invalid-name
handler404 = "VIM.views.custom_404_page_not_found"
