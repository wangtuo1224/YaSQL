# -*- coding:utf-8 -*-
# by pandonglin
from django.db.models import Q
import django_filters
from workflow.models import TicketFlow, WorkflowGroup


class TicketFlowFilter(django_filters.rest_framework.FilterSet):
    my_action = django_filters.NumberFilter(method="search_action")
    workflow_tpl = django_filters.CharFilter(field_name="workflow__id", lookup_expr="iexact")
    act_status = django_filters.NumberFilter(field_name="act_status", lookup_expr="iexact")
    start_created_at = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end_created_at = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    def search_action(self, queryset, name, value):
        if value == 1:  # 我创建的工单
            return queryset.filter(creator=self.request.user.username)
        elif value == 2: # 需要我处理的工单
            return queryset.filter(Q(tf_user__username=self.request.user.username) & Q(tf_user__process=False)).distinct()
        elif value == 3: # 我已经处理的工单
            return queryset.filter(Q(tf_user__username=self.request.user.username) & Q(tf_user__process=True)).distinct()
        else:  # 与我相关的全部工单
            return queryset.filter(Q(creator=self.request.user.username)|Q(participant=self.request.user.username)
                                   | Q(tf_user__username=self.request.user.username)).distinct()

    class Meta:
        model = TicketFlow
        fields =["creator", "my_action", "workflow_tpl", "act_status", "start_created_at", "end_created_at"]


class WorkflowGroupFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='contains')

    class Meta:
        model = WorkflowGroup
        fields = ["name",]