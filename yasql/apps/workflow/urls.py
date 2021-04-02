# -*- coding:utf-8 -*-
# by pandonglin
from django.urls import path, re_path, include
from workflow import views

v1_patterns = [
    # 获取可见任务流程组信息
    path(r'list', views.WorkflowGroup.as_view({"get": "list"}), name='v1.workflow.list'),
    path(r'group/<int:pk>', views.TicketFlowDetail.as_view(), name='v1.workflow.ticketflow.detail'),
    path(r'template/<int:pk>', views.WorkflowTemplate.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
         name='v1.workflow.template'),
    path(r'ticket', views.TicketFlow.as_view(), name='v1.workflow.ticketflow'),
    path(r'ticket/<int:pk>', views.TicketFlowDetail.as_view(), name='v1.workflow.ticketflow.detail'),
    path(r'ticket/<int:pk>/log', views.TicketFlowLog.as_view(), name='v1.workflow.ticketflow.log'),
    path(r'ticket/<int:pk>/action', views.TicketFlowAction.as_view(), name='v1.workflow.ticketflow.action'),
    path(r'upload', views.UploadFileView.as_view(), name='v1.workflow.uploadfile'),
]

urlpatterns = [
    re_path(r'^v1/workflow/', include(v1_patterns))
]