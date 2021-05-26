# -*- coding:utf-8 -*-
# by pandonglin
import json
from rest_framework import serializers
from workflow import models, constant, tasks
from users.models import UserAccounts


class WorkflowSummarySerializers(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowGroup
        fields = "__all__"

    def to_representation(self, instance):
        ret = {
            "wg_id": instance.id,
            "name": instance.name,
            "children": [{"wf_id": x.id, "name": x.name, "description": x.description} for x in instance.wf.all()]
        }
        return ret


class WorkflowGroupSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.WorkflowGroup
        fields = "__all__"


class WorkflowTplSerializer(serializers.ModelSerializer):
    field_kwargs = serializers.ListField(write_only=True)

    class Meta:
        model = models.WorkflowTpl
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(WorkflowTplSerializer, self).to_representation(instance)
        ret["display_form_field"] = instance.display_form_field
        ret["all_form_field"] = instance.all_form_field
        ret["group"] = {"id": instance.group.id, "name": instance.group.name}
        return ret

    def validate_display_form(self, data):
        if not data:
            raise serializers.ValidationError('表单显示字段必填')
        try:
            d = json.loads(data)
            if isinstance(d, list):
                return data
            else:
                raise serializers.ValidationError('表单显示字段格式错误，请配置成：["id","title"]')
        except:
            raise serializers.ValidationError('表单显示字段格式错误，请配置成：["id","title"]')

    def validate(self, data):
        """校验字段"""
        field_kwargs = data.get('field_kwargs')
        if field_kwargs is None:
            raise serializers.ValidationError('未配置表单字段')

        file_field = []
        error_list = []
        for x in field_kwargs:
            if x.get("field_name") is None:
                error_list.append("字段名必填")
            if x.get("field_key") is None:
                error_list.append("字段key必填")
            if x.get("field_type") is None:
                error_list.append("字段类型必填")
            if x.get("order_id") is None:
                error_list.append("字段顺序必填")

            # 对select类型进行验证，需要有field_value有值
            if x.get("field_type") in ["select", "multiselect"]:
                field_value = x.get("field_value")
                if field_value:
                    try:
                        j = json.loads(field_value)
                        if not isinstance(j, dict):
                            error_list.append('字段数据必须为json格式键值对，如:{"1":"需要","0":"不需要"}')
                    except:
                        error_list.append('字段数据必须为json格式键值对，如:{"1":"需要","0":"不需要"}')
                else:
                    error_list.append('%s为%s类型，字段数据必填' % (x['field_name'], x['field_type']))

            # 对附件进行验证，每个工单保持一个附件
            if x.get("field_type") == "file":
                file_field.append(x)

        if len(error_list) > 0:
            raise serializers.ValidationError('\n'.join(error_list))
        elif len(file_field) > 1:
            raise serializers.ValidationError('每个工单只能有一个附件类型的字段')
        else:
            data["field_kwargs"] = field_kwargs
            return data

    def set_field(self, tpl, kwargs):
        """保存模版字段"""
        tpl.wf_field.all().delete()
        for item in kwargs:
            tpl.wf_field.create(**item)

    def create(self, validated_data):
        field_kwargs = validated_data.pop('field_kwargs', [])
        instance = models.WorkflowTpl.objects.create(**validated_data)
        self.set_field(instance, field_kwargs)
        return instance

    def update(self, instance, validated_data):
        field_kwargs = validated_data.pop('field_kwargs', [])
        for k, v in validated_data.items():
            setattr(instance, k, v)
        self.set_field(instance, field_kwargs)
        instance.save()
        return instance


class WorkflowStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.State
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(WorkflowStateSerializer, self).to_representation(instance)
        if ret["participant_type"] in [constant.PARTICIPANT_TYPE_ROBOT, constant.PARTICIPANT_TYPE_HOOK]:
            ret["participant_data"] = instance.participant_data
        else:
            ret["participant_data"] = json.loads(instance.participant_data) if instance.participant_data else []
        return ret

    def validate_participant_data(self, data):
        try:
            participant_data = json.loads(data)
            return json.dumps(participant_data, ensure_ascii=False)
        except:
            raise serializers.ValidationError('操作人参数错误')

    def validate(self, data):
        participant_type = data.get("participant_type")
        # 操作人类型为：角色时，流转方式为空
        if participant_type == constant.PARTICIPANT_TYPE_ROLE and data.get("distribute_type"):
            raise serializers.ValidationError('流转方式必须为空')
        # 操作人类型为：个人, 工单字段时，需要填操作人和流转方式
        if participant_type in [constant.PARTICIPANT_TYPE_PERSONAL, constant.PARTICIPANT_TYPE_FIELD]:
            if data.get("participant_data") is None:
                raise serializers.ValidationError('操作人必填')
            if data.get("distribute_type") is None:
                raise serializers.ValidationError('流转方式必填')
        # 操作人类型为：机器人, Hook时，order_id不能为1
        if participant_type in [constant.PARTICIPANT_TYPE_ROBOT, constant.PARTICIPANT_TYPE_HOOK] and data["order_id"] == 1:
            raise serializers.ValidationError('顺序为1时，与操作人类型[%s]冲突' % self._participant_type_display(participant_type))

        request = self.context["request"]
        state_list = models.State.objects.filter(workflow=data["workflow"])
        state_type_list = [x.state_type for x in state_list]
        order_id_list = [x.order_id for x in state_list]

        if request.method.upper() == "POST":   # 创建状态检测
            if data["state_type"] == 1 and (1 in state_type_list):
                raise serializers.ValidationError('初始状态已存在')
            if data["state_type"] == 2 and (2 in state_type_list):
                raise serializers.ValidationError('结束状态已存在')
            if data["order_id"] in order_id_list:
                raise serializers.ValidationError('状态顺序重复')

        if request.method.upper() == "PUT":   # 更新状态检测
            if data["state_type"] != self.instance.state_type and data["state_type"] == 1 and (1 in state_type_list):
                raise serializers.ValidationError('初始状态已存在')
            if data["state_type"] != self.instance.state_type and data["state_type"] == 2 and (2 in state_type_list):
                raise serializers.ValidationError('结束状态已存在')
            if data["order_id"] != self.instance.order_id and data["order_id"] in order_id_list:
                raise serializers.ValidationError('状态顺序重复')
        return data

    def create(self, validated_data):
        instance = models.State.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        if validated_data.get("participant_type") is None:
            instance.participant_type = None
        if validated_data.get("participant_data") is None:
            instance.participant_data = None
        if validated_data.get("distribute_type") is None:
            instance.distribute_type = None

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def _participant_type_display(self, key):
        for item in constant.PARTICIPANT_TYPE:
            if item[0] == key:
                return item[1]


class WorkflowTransitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Transition
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(WorkflowTransitionSerializer, self).to_representation(instance)
        ret["source_state_name"] = instance.source_state.name
        ret["destination_state_name"] = instance.destination_state.name
        return ret

    def validate(self, data):
        return data

    def create(self, validated_data):
        instance = models.Transition.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class TicketFlowSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(read_only=True)
    state = serializers.CharField(read_only=True)
    field_kwargs = serializers.JSONField(write_only=True)

    class Meta:
        model = models.TicketFlow
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(TicketFlowSerializer, self).to_representation(instance)
        ret["workflow"] = instance.workflow.name
        return ret

    def _get_workflow_start_state(self, workflow):    # 获取流程的初始状态
        state_obj = models.State.objects.filter(workflow=workflow, state_type=constant.STATE_TYPE_START).first()
        return state_obj

    def _get_ticket_init_relation_user(self, ticket_obj, next_state):   # 获取工单的关联人
        if next_state.participant_type == constant.PARTICIPANT_TYPE_PERSONAL and next_state.participant_data:
            user_list = json.loads(next_state.participant_data)
        elif next_state.participant_type == constant.PARTICIPANT_TYPE_ROLE and next_state.participant_data:
            users = UserAccounts.objects.filter(userroles__role_name__in=json.loads(next_state.participant_data))
            user_list = [x["username"] for x in users.values("username")]
        elif next_state.participant_type == constant.PARTICIPANT_TYPE_FIELD and next_state.participant_data:
            field_list = ticket_obj.tf_field.filter(field_key__in=json.loads(next_state.participant_data))
            user_list = [x["field_value"] for x in field_list.values("field_value")]
        else:
            user_list = []
        return user_list

    def validate(self, data):
        start_state = self._get_workflow_start_state(data["workflow"])
        if start_state is None:
            raise serializers.ValidationError("%s no start state" % data["workflow"].name)
        else:
            data["state"] = start_state.id
            return data

    def create_ticket(self, username):
        data = self.validated_data
        # data["token"] = get_random_code(16)

        data['creator'] = username
        field_kwargs = data.pop("field_kwargs")
        self.save()

        # 更新工单字段值
        for k, v in field_kwargs.items():
            name, field_type = self.instance.workflow.get_field_attr(k)
            models.TicketFlowField.objects.create(ticket=self.instance, field_name=name,
                                                  field_type=field_type, field_key=k, field_value=v)

        models.TicketFlowLog.objects.create(ticket=self.instance, participant=username, state=self.instance.state_display,
                                            act_status=constant.TICKET_ACT_STATE_FINISH)

        # 更新工单处理人
        transition = models.Transition.objects.filter(workflow=self.instance.workflow, source_state=self.instance.state).first()
        if transition:
            self.instance.state = transition.destination_state.id
            self.instance.save()
            relation_user = self._get_ticket_init_relation_user(self.instance, transition.destination_state)
            for user in relation_user:
                models.TicketFlowUser.objects.create(ticket=self.instance, state=self.instance.state, username=user)

        # 推送消息
        tasks.msg_notice.delay(
            pk=self.instance.pk,
            op="_commit",
            title="新建流程工单",
            username=username
        )


class TicketFlowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketFlow
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(TicketFlowDetailSerializer, self).to_representation(instance)
        ret["workflow"] = instance.workflow.name
        ret["state"] = instance.state if instance.act_status != constant.TICKET_ACT_STATE_CLOSE else -1
        ret["status"] = instance.get_act_status_display()
        ret["all_state"] = instance.all_state
        ret["field_kwargs"] = instance.all_ticket_field
        ret["ticket_is_end"] = instance.ticket_is_end
        return ret


class TicketFlowLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketFlowLog
        fields = "__all__"


