"""Ponto de entrada HTTP; as rotas de negócio serão adicionadas por TDD."""

from django.urls import URLResolver, include, path

urlpatterns: list[URLResolver] = [path("", include("library.urls"))]
