# -*- coding:utf-8 -*-
# by pandonglin
import logging, os
from django.http import Http404
from libs.response import JsonResponseV1
from libs.Pagination import Pagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from workflow import models, serializers, handler
from workflow.filters import TicketFlowFilter, WorkflowGroupFilter
from libs import permissions


logger = logging.getLogger("main")


class UploadFileView(APIView):
    def post(self, request):
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return JsonResponseV1(code="0002", message="未发现可上传文件")

        try:
            if not os.path.exists("media/workflow"):
                os.makedirs("media/workflow")

            os_file_path = os.path.join('media/workflow', file_obj.name)
            if os.path.exists(os_file_path):
                os.remove(os_file_path)

            f = open(os_file_path, 'wb')
            for chunk in file_obj.chunks():  # 循环读取文件的内容
                f.write(chunk)
            f.close()

            logger.info("UploadFileView %s upload success" % os_file_path)
            return JsonResponseV1(data={"file_name": os_file_path})
        except Exception as error:
            logger.error("UploadFileView %s upload error: %s" % error)
            return JsonResponseV1(code="0002", message=error)


class WorkflowSummary(GenericAPIView):
    """工作流程分组"""
    serializer_class = serializers.WorkflowSummarySerializers
    pagination_class = Pagination
    permission_classes = (permissions.anyof(permissions.CanUpdateWorkFlowPermission,
                                            permissions.CanViewTicketPermission,
                                            permissions.CanUpdateTicketPermission),
                          )

    def get(self, request, *args, **kwargs):
        # TODO 只能看到授权的模版
        # my_queryset = models.WorkflowGroup.objects.filter(rg_group__user=request.user)
        my_queryset = models.WorkflowGroup.objects.all()
        page = self.paginate_queryset(my_queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class WorkflowGroup(ModelViewSet):
    queryset = models.WorkflowGroup.objects.all()
    serializer_class = serializers.WorkflowGroupSerializers
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = WorkflowGroupFilter
    permission_classes = (permissions.CanUpdateWorkFlowPermission,)

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(queryset)
        return JsonResponseV1(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class WorkflowTemplate(ModelViewSet):
    """流程模版"""
    queryset = models.WorkflowTpl.objects.all()
    serializer_class = serializers.WorkflowTplSerializer
    permission_classes = (permissions.CanUpdateWorkFlowPermission,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return JsonResponseV1()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponseV1(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponseV1(serializer.data)


class WorkflowState(ModelViewSet):
    """流程状态"""
    queryset = models.State.objects.all()
    serializer_class = serializers.WorkflowStateSerializer
    permission_classes = (permissions.CanUpdateWorkFlowPermission,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return JsonResponseV1()

    def retrieve(self, request, *args, **kwargs):
        try:
            tpl = models.WorkflowTpl.objects.get(pk=kwargs.get("pk"))
            instance = tpl.wf_state.all()
            serializer = self.get_serializer(instance, many=True)
            return JsonResponseV1(serializer.data)
        except:
            return JsonResponseV1(code="0002", message="not found")


class WorkflowTransition(ModelViewSet):
    """状态转换"""
    queryset = models.Transition.objects.all()
    serializer_class = serializers.WorkflowTransitionSerializer
    permission_classes = (permissions.CanUpdateWorkFlowPermission,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return JsonResponseV1()

    def retrieve(self, request, *args, **kwargs):
        try:
            tpl = models.WorkflowTpl.objects.get(pk=kwargs.get("pk"))
            instance = tpl.wf_transition.all()
            serializer = self.get_serializer(instance, many=True)
            return JsonResponseV1(serializer.data)
        except:
            return JsonResponseV1(code="0002", message="not found")


class TicketFlow(GenericAPIView):
    """工单"""
    queryset = models.TicketFlow.objects.all()
    serializer_class = serializers.TicketFlowSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = TicketFlowFilter
    permission_classes = (permissions.CanViewTicketPermission,)

    def get(self, request, *args, **kwargs):
        """条件过滤工单"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TicketFlowNew(GenericAPIView):
    serializer_class = serializers.TicketFlowSerializer
    permission_classes = (permissions.CanUpdateTicketPermission,)

    def post(self, request, *args, **kwargs):
        """创建工单"""
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.create_ticket(request.user.username)
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)


class TicketFlowDetail(GenericAPIView):
    """工单详情"""
    queryset = models.TicketFlow.objects.all()
    serializer_class = serializers.TicketFlowDetailSerializer
    permission_classes = (permissions.CanViewTicketPermission,)

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        if queryset.workflow.all_view or request.user.username == queryset.creator or \
                request.user.username in queryset.all_relation_user:
            serializer = self.get_serializer(queryset)
        else:
            raise Http404
        return JsonResponseV1(serializer.data)


class TicketFlowAction(APIView):
    """更新工单状态"""
    permission_classes = (permissions.CanUpdateTicketPermission,)

    def get_obj(self, pk):
        try:
            ticket_obj = models.TicketFlow.objects.get(pk=pk)
            return ticket_obj
        except models.TicketFlow.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        ticket_obj = self.get_obj(pk)
        ticket = handler.TicketFlow(request.user.username, ticket_obj, request.data)
        success, error = ticket.handle()
        if success:
            return JsonResponseV1()
        return JsonResponseV1(code="0002", message=error)


class TicketFlowLog(APIView):
    """工单日志"""
    permission_classes = (permissions.CanViewTicketPermission,)

    def get(self, request, *args, **kwargs):
        queryset = models.TicketFlowLog.objects.filter(ticket__id=kwargs['pk'])
        serializer = serializers.TicketFlowLogSerializer(queryset, many=True)
        return JsonResponseV1(serializer.data)