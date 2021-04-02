# -*- coding:utf-8 -*-
# by pandonglin
from rest_framework import serializers
from workflow import models, constant


class WorkflowGroupSerializers(serializers.ModelSerializer):
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


class WorkflowTplSerializer(serializers.ModelSerializer):
    kwargs = serializers.ListField(write_only=True)

    class Meta:
        model = models.WorkflowTpl
        fields = "__all__"

    def validate(self, data):
        """校验字段"""
        kwargs = data.get('kwargs', [])
        file_field = []
        for x in kwargs:
            if x["category"] == "file":
                file_field.append(x)
                x["field"] = "file"  # 强制修改字段名称

        if len(file_field) > 1:
            raise serializers.ValidationError({'template': '模版只能有一个file类型的字段'})
        else:
            data["kwargs"] = kwargs
        return data

    def set_field(self, tpl, kwargs):
        """保存模版字段"""
        tpl.field.all().delete()
        for item in kwargs:
            item['template'] = tpl
            models.WorkflowTpl.objects.update_or_create(**item)

    def create(self, validated_data):
        kwargs = validated_data.pop('kwargs', [])
        instance = models.WorkflowTpl.objects.create(**validated_data)
        self.set_field(instance, kwargs)
        return instance

    def update(self, instance, validated_data):
        kwargs = validated_data.pop('kwargs', [])
        for k, v in validated_data.items():
            setattr(instance, k, v)
        self.set_field(instance, kwargs)
        instance.save()
        return instance

    def to_representation(self, instance):
        ret = super(WorkflowTplSerializer, self).to_representation(instance)
        ret["display_form_field"] = instance.display_form_field
        return ret


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

    # def to_internal_value(self, data):
    #     return super(TicketFlowSerializer, self).to_internal_value(data)

    def validate(self, data):
        state = data["workflow"].wf_state.filter(state_type=1).first()  # 获取初始状态
        if state:
            data["state"] = state.id
        else:
            raise serializers.ValidationError({"state": "%s no init state" % data["workflow"].name})
        return data

    def create_ticket(self, user):
        data = self.validated_data
        # data["token"] = get_random_code(16)
        data['creator'] = user.username or "nobody"
        field_kwargs = data.pop("field_kwargs")
        self.save()

        for k,v in field_kwargs.items():
            name = self.instance.workflow.get_field_name(k)
            models.TicketFlowField.objects.create(ticket=self.instance, field_name=name, field_key=k, field_value=v)

        models.TicketFlowLog.objects.create(ticket=self.instance, participant=user.username,
                                            state=self.instance.state_display, act_status=constant.TICKET_ACT_STATE_FINISH)


class TicketFlowDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketFlow
        fields = "__all__"

    def to_representation(self, instance):
        ret = super(TicketFlowDetailSerializer, self).to_representation(instance)
        ret["workflow"] = instance.workflow.name
        ret["status"] = instance.get_act_status_display()
        ret["all_state"] = instance.workflow.all_state
        ret["field_kwargs"] = instance.all_ticket_field
        ret["ticket_is_end"] = instance.ticket_is_end
        return ret


class TicketFlowLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketFlowLog
        fields = "__all__"


