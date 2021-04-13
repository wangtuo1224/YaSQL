# -*- coding:utf-8 -*-
# by pandonglin
from django.urls import path, re_path, include
from workflow import views

v1_patterns = [
    path(r'summary', views.WorkflowSummary.as_view(), name='v1.workflow.summary'),
    path(r'group', views.WorkflowGroup.as_view({"get": "list", "post": "create"}), name='v1.workflow.group.list'),
    path(r'group/<int:pk>', views.WorkflowGroup.as_view({"get": "get", "put": "update"}), name='v1.workflow.group.detail'),
    path(r'template', views.WorkflowTemplate.as_view({"get": "list", "post": "create"}), name='v1.workflow.template'),
    path(r'template/<int:pk>', views.WorkflowTemplate.as_view({"get": "retrieve", "put": "update"}), name='v1.workflow.template.detail'),
    path(r'ticket', views.TicketFlow.as_view(), name='v1.workflow.ticketflow'),
    path(r'ticket/<int:pk>', views.TicketFlowDetail.as_view(), name='v1.workflow.ticketflow.detail'),
    path(r'ticket/<int:pk>/log', views.TicketFlowLog.as_view(), name='v1.workflow.ticketflow.log'),
    path(r'ticket/<int:pk>/action', views.TicketFlowAction.as_view(), name='v1.workflow.ticketflow.action'),
    path(r'upload', views.UploadFileView.as_view(), name='v1.workflow.uploadfile'),
]

urlpatterns = [
    re_path(r'^v1/workflow/', include(v1_patterns))
]