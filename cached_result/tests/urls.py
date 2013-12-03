"""URLs to run the tests."""
try:
    from django.conf.urls.defaults import patterns, include, url
except ImportError:  # Django 1.6
    from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    '',
)
