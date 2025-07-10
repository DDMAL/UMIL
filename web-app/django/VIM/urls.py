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
from VIM.apps.instruments.views.update_umil_db import add_name, delete_name
from VIM.apps.instruments.views.instrument_upload import InstrumentNameListView
from VIM.apps.instruments.views.wiki_apis import (
    wikidata_authorize,
    wikidata_callback,
    get_wikidata_access_token,
    edit_wikidata,
)
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("VIM.apps.main.urls", namespace="main")),
    path("instruments/", InstrumentList.as_view(), name="instrument-list"),
    path("instrument/<int:pk>/", InstrumentDetail.as_view(), name="instrument-detail"),
    path("add-name/", add_name, name="add-name"),
    path("delete-name/", delete_name, name="delete-name"),
    path("upload/", InstrumentNameListView.as_view(), name="instrument-upload"),
    path("oauth/authorize/", wikidata_authorize, name="wikidata-authorize"),
    path("oauth/callback/", wikidata_callback, name="wikidata-callback"),
    path("get-wikidata-access-token/", get_wikidata_access_token, name="get-wikidata-access-token"),
    path("edit-wikidata/", edit_wikidata, name="edit-wikidata"),
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
