from django.urls import path

from .views import (
    home,
    investigate,
    investigation_result,
    trace_running,
    graph_explorer,
    get_trace_status
)

urlpatterns = [
    path("", home, name="landing"),
    path("investigate/", investigate, name="investigation_setup"),
    path("trace_running/", trace_running, name="trace_running"),
    path("investigation_result/", investigation_result, name="investigation_result"),
    path("graph_explorer/", graph_explorer, name="graph_explorer"),
    
    path("api/get_trace_status/<task_id>/", get_trace_status),
]