from django.contrib import admin
from workflow import models
from django import forms


class WorkflowCustomFieldInline(admin.TabularInline):
    model = models.WorkflowCustomField
    extra = 1

    verbose_name = "流程字段"
    verbose_name_plural = "流程字段"


class TicketFlowFieldInline(admin.TabularInline):
    model = models.TicketFlowField
    extra = 1

    verbose_name = "工单字段"
    verbose_name_plural = "工单字段"


class WorkflowTplAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'group', 'all_view', 'display_form',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'description',)

    class Meta:
        model = models.WorkflowTpl
        fields = '__all__'

    inlines = [WorkflowCustomFieldInline, ]
    exclude = ('customField',)


class StateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'workflow', 'name', 'is_hidden', 'order_id', 'state_type', 'participant_type', 'participant', 'distribute_type',
    )
    list_display_links = ('name',)
    search_fields = ('workflow__name',)
    list_filter = ("workflow__name",)
    list_editable = ('is_hidden', 'order_id', 'state_type', 'participant_type', 'participant', 'distribute_type',)

    class Meta:
        model = models.State
        fields = '__all__'


class TransitionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'workflow', 'action', 'transition_type', 'source_state', 'destination_state',
        'condition_expression', 'attribute_type', 'field_require_check'
    )
    list_display_links = ('action',)
    search_fields = ('workflow__name',)
    list_filter = ("workflow__name",)
    list_editable = ('transition_type', 'source_state', 'destination_state', 'condition_expression')

    class Meta:
        model = models.Transition
        fields = '__all__'


class TicketFlowAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'workflow', 'creator', 'state', 'participant', 'act_status',
    )
    list_display_links = ('id',)
    search_fields = ('name', 'creator',)

    class Meta:
        model = models.WorkflowTpl
        fields = '__all__'

    inlines = [TicketFlowFieldInline, ]


class TicketFlowUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ticket', 'state', 'username', 'process', 'action',
    )
    list_display_links = ('id',)
    search_fields = ('username',)

    class Meta:
        model = models.State
        fields = '__all__'


class TicketFlowLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ticket', 'participant', 'state', 'act_status',
    )
    list_display_links = ('id',)
    search_fields = ('ticket',)

    class Meta:
        model = models.State
        fields = '__all__'


admin.site.register(models.WorkflowGroup)
admin.site.register(models.WorkflowTpl, WorkflowTplAdmin)
admin.site.register(models.State, StateAdmin)
admin.site.register(models.Transition, TransitionAdmin)
admin.site.register(models.TicketFlow, TicketFlowAdmin)
admin.site.register(models.TicketFlowUser, TicketFlowUserAdmin)
admin.site.register(models.TicketFlowLog, TicketFlowLogAdmin)