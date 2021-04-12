# -*- coding:utf-8 -*-
# by pandonglin
import json, datetime
from django.db import models
from workflow.constant import TICKET_ACT_STATE_MAP, PARTICIPANT_TYPE, TICKET_ACT_STATE_END


class BaseModel(models.Model):
    """基础model"""
    id = models.AutoField(primary_key=True, verbose_name='主键ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class WorkflowGroup(BaseModel):
    """流程组"""
    name = models.CharField(max_length=32, verbose_name="名称")

    class Meta:
        verbose_name = "流程组"
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_group'

    def __str__(self):
        return self.name


class WorkflowTpl(BaseModel):
    """流程模版"""
    name = models.CharField(max_length=64, verbose_name='流程名称')
    description = models.CharField(max_length=128, verbose_name='描述')
    group = models.ForeignKey("WorkflowGroup", related_name='wf', on_delete=models.CASCADE, verbose_name="流程组")
    all_view = models.BooleanField(default=True, verbose_name='工单可见性',
                                   help_text='只允许工单的关联人(创建人、需要处理人)查看工单,默认所有人可见')
    # 提交工单显示的字段,field_key的list,如["title","sn"],
    display_form = models.CharField(max_length=1024, default='[]', verbose_name="表单字段", help_text='表单中可见字段,自定义字段中的field_key')

    class Meta:
        verbose_name = "流程模版"
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_tpl'

    def __str__(self):
        return self.name

    def get_field_name(self, key):
        f = self.wf_field.filter(field_key=key)
        if f:
            return f[0].field_name
        return key

    @property
    def all_state(self):
        data = []
        states = self.wf_state.all()
        for state in states:
            data.append({
                "id": state.id,
                "name": state.name,
                "participant": state.participant,
            })
        return data

    @property
    def display_form_field(self):
        data = []
        display_form_list = json.loads(self.display_form) or []
        custom_field_filter = self.wf_field.filter(field_key__in=display_form_list)
        for item in custom_field_filter:
            data.append({
                "order_id": item.order_id,
                "field_name": item.field_name,
                "field_key": item.field_key,
                "field_type": item.field_type,
                "required": item.required,
                "default_value": item.default_value,
                "placeholder": item.placeholder,
                "field_value": json.loads(item.field_value) if item.field_value else {}
            })
        return data


class WorkflowCustomField(BaseModel):
    """流程自定义字段"""
    FIELD_TYPE = (
        ("string", "字符串"),
        ("integer", "整型"),
        ("boolean", "布尔值"),
        ("textarea", "文本框"),
        ("select", "单选下拉列表"),
        ("multiselect", "多选下拉列表"),
        ("file", "附件"),
        ("user", "用户"),  # 可以多选用户
    )
    workflow = models.ForeignKey(WorkflowTpl, related_name="wf_field", on_delete=models.CASCADE, verbose_name="关联流程")
    field_name = models.CharField(max_length=64, verbose_name='字段名称')
    field_key = models.CharField(max_length=64, help_text='字段类型请尽量特殊，避免与系统中关键字冲突', verbose_name='字段key')
    field_type = models.CharField(choices=FIELD_TYPE, max_length=32, verbose_name='类型')
    required = models.BooleanField(default=False, verbose_name='字段值是否必填')
    order_id = models.IntegerField(default=0, verbose_name='字段顺序',
                                   help_text='工单表单中排序:工单号0,标题20,状态id40,状态名41,创建人80,创建时间100,更新时间120.前端根据id顺序排列')
    default_value = models.CharField(max_length=128, null=True, blank=True, verbose_name='默认值',
                                     help_text='作为表单中的该字段的默认值')
    placeholder = models.CharField(max_length=128, null=True, blank=True, verbose_name='占位符',
                                   help_text='用户工单详情表单中作为字段的占位符显示')
    field_value = models.TextField(null=True, blank=True, verbose_name='字段数据',
                                    help_text='select/multiselect提供选项，格式为json如:{"1":"需要","0":"不需要"},{"1":"中国", "2":"美国"}')

    class Meta:
        verbose_name = "流程字段"
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_field'

    def __str__(self):
        return self.field_name


class State(BaseModel):
    """状态记录, 变量支持通过脚本获取"""
    STATE_TYPE = (
        (0, "普通类型"),
        (1, "初始状态"),
        (2, "结束状态"),
    )
    DISTRIBUTE_TYPE = (
        ("any", "any"),
        ("all", "all"),
    )
    workflow = models.ForeignKey(WorkflowTpl, related_name="wf_state", on_delete=models.CASCADE, verbose_name="关联流程")
    name = models.CharField(max_length=64, verbose_name='状态名称')
    is_hidden = models.BooleanField(default=False, verbose_name='是否隐藏',
                                    help_text='设置为True时,获取工单步骤api中不显示此状态(当前处于此状态时除外)')
    order_id = models.IntegerField(default=0, verbose_name='状态顺序', help_text='用于工单步骤接口时，step上状态的顺序，值越小越靠前')
    state_type = models.IntegerField(choices=STATE_TYPE, default=0, verbose_name='状态类型id',
                                     help_text="初始状态:新建工单时,获取对应的字段必填及transition信息，结束状态：此状态下的工单不得再处理，即没有对应的transition")
    participant_type = models.IntegerField(choices=PARTICIPANT_TYPE, default=1, verbose_name='操作人类型')
    participant = models.CharField(max_length=1024, null=True, blank=True, verbose_name='操作人',
                                   help_text='可以为空、用户\多用户(以,隔开)\部门id\角色id\变量(creator,creator_tl)\脚本记录的id等，包含子工作流的需要设置处理人为bot')
    distribute_type = models.CharField(choices=DISTRIBUTE_TYPE, max_length=32, verbose_name='流转方式', help_text='any其中一人处理即可，all所有人都要处理')
    #'json格式字典存储,包括读写属性1：只读，2：必填，3：可选. 示例：{"created_at":1,"title":2, "sn":1},
    state_field_str = models.TextField(default='{}', verbose_name='表单字段')

    class Meta:
        verbose_name = "流程状态"
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_state'
        ordering = ('-workflow__id', 'order_id')

    def __str__(self):
        return self.name


class Transition(BaseModel):
    """流程流转，条件(允许跳过)"""
    TRANSITION_TYPE = (
        (1, "常规流转"),
        (2, "其他")
    )
    workflow = models.ForeignKey(WorkflowTpl, related_name="wf_transition", on_delete=models.CASCADE, verbose_name="关联流程")
    action = models.CharField(max_length=64, verbose_name='状态转换动作')
    transition_type = models.IntegerField(choices=TRANSITION_TYPE, verbose_name='流转类型', help_text='1.常规流转，2.其他')
    source_state = models.ForeignKey(State, related_name="state_source", on_delete=models.CASCADE, verbose_name='源状态')
    destination_state = models.ForeignKey(State, related_name="state_destination", on_delete=models.CASCADE, verbose_name='目的状态')
    condition_expression = models.CharField(max_length=2048, default='[]', verbose_name='条件表达式',
                                            help_text='流转条件表达式，根据表达式中的条件来确定流转的下个状态')
    attribute_type = models.IntegerField(default=1, verbose_name='属性类型', help_text='1.同意，2.拒绝，3.超时，4.其他')
    field_require_check = models.BooleanField(default=True, verbose_name='是否校验必填项',
                                              help_text='提交数据时需要校验工单表单的必填项。如"退回"属性的操作，不需要填写表单内容')

    class Meta:
        verbose_name = "流程状态流转"
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_transition'
        ordering = ('-workflow__id', 'destination_state')

    def __str__(self):
        return self.action


class TicketFlow(models.Model):
    """工单"""
    id = models.AutoField(primary_key=True, verbose_name='主键ID')
    creator = models.CharField(max_length=32, db_index=True, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    workflow = models.ForeignKey(WorkflowTpl, related_name="wf_tickflow", on_delete=models.CASCADE, verbose_name="关联流程")
    state = models.IntegerField(verbose_name="当前状态")
    parent_ticket_id = models.IntegerField(default=0, verbose_name="父工单id")
    participant = models.CharField(max_length=32, null=True, blank=True, verbose_name="当前处理人")
    act_status = models.IntegerField(choices=TICKET_ACT_STATE_MAP, default=1, verbose_name="操作状态")
    multi_all_person = models.CharField(max_length=1024, null=True, blank=True, verbose_name="全部处理的结果", help_text='需要当前状态处理人全部处理时实际的处理结果，json格式')
    run_result = models.TextField(default='', verbose_name="执行结果")

    class Meta:
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_tickflow'
        ordering = ('-id',)

    def __str__(self):
        return "#%s" % self.id

    @property
    def relation_user(self):
        return [x["username"] for x in self.tf_user.all().values("username")]

    @property
    def ticket_is_end(self):
        if self.act_status in TICKET_ACT_STATE_END:
            return True
        return False

    @property
    def all_ticket_field(self):
        return [{"name": x.field_name, "key": x.field_key, "value": x.field_value} for x in self.tf_filed.all()]

    @property
    def state_display(self):
        state = State.objects.filter(pk=self.state).first()
        if state:
            return state.name
        return ''

    @property
    def next_state(self):
        cur_state = State.objects.filter(pk=self.state).first()
        if cur_state:  # 当前状态非完成状态
            next_state_obj = State.objects.filter(workflow=self.workflow, order_id__gt=cur_state.order_id).order_by("order_id").first()
            return next_state_obj.id if next_state_obj else None
        return None


class TicketFlowField(BaseModel):
    """工单自定义字段， 工单自定义字段实际的值"""
    ticket = models.ForeignKey(TicketFlow, related_name="tf_filed", on_delete=models.CASCADE, verbose_name="工单")
    field_name = models.CharField(max_length=64, verbose_name="字段名称")
    field_key = models.CharField(max_length=64, verbose_name="字段key")
    field_value = models.CharField(max_length=2048, null=True, blank=True, verbose_name='字符串值')

    class Meta:
        verbose_name = '工单字段'
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_tickflowfiled'

    def __str__(self):
        return self.field_name


class TicketFlowUser(BaseModel):
    """工单关系人"""
    ticket = models.ForeignKey(TicketFlow, related_name="tf_user", on_delete=models.CASCADE, verbose_name="工单")
    state = models.IntegerField(verbose_name="当前状态")
    username = models.CharField(max_length=64, verbose_name="处理人")
    process = models.BooleanField(default=False, verbose_name="是否处理")
    action = models.CharField(max_length=64, default='', verbose_name="执行操作")  # allow通过，deny拒绝

    class Meta:
        verbose_name = '工单处理人'
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_tickflowuser'

    def __str__(self):
        return self.username


class TicketFlowLog(BaseModel):
    """工单流转日志"""
    ticket = models.ForeignKey(TicketFlow, related_name="tf_log", on_delete=models.CASCADE, verbose_name="工单")
    participant = models.CharField(max_length=64, verbose_name="处理人")
    state = models.CharField(max_length=64, verbose_name="当前状态")
    suggestion = models.CharField(max_length=2048, null=True, blank=True, verbose_name="处理意见")
    act_status = models.IntegerField(choices=TICKET_ACT_STATE_MAP, default=1, verbose_name="操作状态", help_text='constant中定义：拒绝/通过/中止/超时')
    ticket_data = models.TextField(null=True, blank=True, verbose_name="工单数据", help_text='可以用于记录当前表单数据，json格式')

    class Meta:
        verbose_name = '工单流转日志'
        verbose_name_plural = verbose_name
        db_table = 'yasql_workflow_tickflowlog'
        ordering = ('-id',)

    def __str__(self):
        return "#%s" % self.id
