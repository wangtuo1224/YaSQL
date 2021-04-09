# -*- coding:utf-8 -*-
# by pandonglin
import logging
from django.http import Http404
from libs.response import JsonResponseV1
from libs.Pagination import Pagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from workflow import models, serializers, handler
from workflow.filters import TicketFlowFilter, WorkflowGroupFilter


logger = logging.getLogger("main")


class UploadFileView(APIView):
    pass
#     def post(self, request):
#         file_name = request.FILES.get('file')
#         if file_name is None:
#             return ErrorResponse(error="未发现可上传文件")
#
#         try:
#             if not os.path.exists("media/autotask"):
#                 os.makedirs("media/autotask")
#
#             os_file_path = os.path.join('media/autotask', file_name.name)
#             if os.path.exists(os_file_path):
#                 os.remove(os_file_path)
#
#             f = open(os_file_path, 'wb')
#             for chunk in file_name.chunks():  # 循环读取文件的内容
#                 f.write(chunk)
#             f.close()
#
#             logger.info("UploadFileView %s upload success" % os_file_path)
#             return JsonResponse({"file_name": os_file_path})
#         except Exception as error:
#             logger.error("UploadFileView %s upload error: %s" % error)
#             return ErrorResponse(error=error)


class WorkflowSummary(GenericAPIView):
    """工作流程分组"""
    serializer_class = serializers.WorkflowSummarySerializers
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
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
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponseV1(serializer.data)


class TicketFlow(GenericAPIView):
    """工单"""
    queryset = models.TicketFlow.objects.all()
    serializer_class = serializers.TicketFlowSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = TicketFlowFilter

    def get(self, request, *args, **kwargs):
        """条件过滤工单"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        """创建工单"""
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.create_ticket(request.user)
            return JsonResponseV1(serializer.data)
        return JsonResponseV1(code="0002", message=serializer.errors)


class TicketFlowDetail(GenericAPIView):
    """工单详情"""
    queryset = models.TicketFlow.objects.all()
    serializer_class = serializers.TicketFlowDetailSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.get_serializer(queryset)
        return JsonResponseV1(serializer.data)


class TicketFlowAction(APIView):
    """更新工单状态"""
    def get_obj(self, pk):
        try:
            task_obj = models.TicketFlow.objects.get(pk=pk)
            return task_obj
        except models.TicketFlow.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        ticket_obj = self.get_obj(pk)
        ticket = handler.TicketFlow(request.user, request.data, ticket_obj)
        success, error = ticket.handle()
        if success:
            return JsonResponseV1()
        return JsonResponseV1(code="0002", message=error)


class TicketFlowLog(APIView):
    """工单日志"""
    def get(self, request, *args, **kwargs):
        queryset = models.TicketFlowLog.objects.filter(ticket__id=kwargs['pk'])
        serializer = serializers.TicketFlowLogSerializer(queryset, many=True)
        return JsonResponseV1(serializer.data)