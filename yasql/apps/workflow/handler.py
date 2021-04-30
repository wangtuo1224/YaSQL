# -*- coding:utf-8 -*-
# by pandonglin
import json
from workflow import constant, models


class TicketFlow:
    def __init__(self, user, data, ticket_obj=None):
        self.user = user
        self.data = data
        self.ticket_obj = ticket_obj

    def handle(self):
        if self.user.username not in self.ticket_obj.relation_user:   # 判断用户权限
            return False, "无权限执行"

        if self.ticket_obj.act_status in constant.TICKET_ACT_STATE_END:
            return False, "工单已完成"

        if self.data["state"] != self.ticket_obj.state:
            return False, "工单状态错误"

        if self._check_user_action():   # 判断用户是否重复执行
            return False, "您已经处理过"

        if self.data["action"] not in ["deny", "allow", "close"]:
            return False, "无效的操作"

        if self.data["action"] == "close":
            return self.close_ticket()
        else:
            status, result = self.transition_state()
            if self.ticket_obj.next_state is not None:
                if self.ticket_obj.next_state.participant_type == constant.PARTICIPANT_TYPE_ROBOT:
                    pass
                elif self.ticket_obj.next_state.participant_type == constant.PARTICIPANT_TYPE_HOOK:
                    pass
                else:  # 其他不处理
                    pass
        return status, result

    def _check_user_action(self):
        participant = self.ticket_obj.tf_user.filter(ticket=self.ticket_obj, state=self.ticket_obj.state,
                                                     username=self.user.username, process=True)
        if participant:
            return True

    def _update_user_action(self, clean_flag=False):
        ticketflow_user = models.TicketFlowUser.objects.get(ticket=self.ticket_obj, state=self.data["state"],
                                                            username=self.user.username)
        ticketflow_user.process = True
        ticketflow_user.action = self.data["action"]
        ticketflow_user.save()

        if clean_flag:
            models.TicketFlowUser.objects.filter(ticket=self.ticket_obj, state=self.data["state"],
                                                 process=False).delete()

        if self.ticket_obj.act_status in constant.TICKET_ACT_STATE_END:  # 结束状态，清洗数据
            models.TicketFlowUser.objects.filter(ticket=self.ticket_obj, process=False).delete()

    def _ticket_log(self, state, status, suggestion=None):
        models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username, state=state,
                                            act_status=status, suggestion=suggestion)

    def close_ticket(self):
        self.ticket_obj.participant = self.user.username
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_CLOSE
        self.ticket_obj.save()
        self._update_user_action()
        self._ticket_log("关闭工单", constant.TICKET_ACT_STATE_CLOSE)
        return True, '关闭成功'

    def transition_state(self):
        if self.data["action"] == "allow":
            return self._transition_state_for_allow()
        else:
            return self._transition_state_for_deny()

    def _transition_state_for_allow(self):
        transition = models.Transition.objects.filter(workflow=self.ticket_obj.workflow,
                                                      source_state=self.ticket_obj.state, attribute_type=1).first()
        if transition is None:
            return False, '状态流转错误'
        # if transition.condition_expression and json.loads(transition.condition_expression):   # 状态流转判断
        #     ticket_value = self.ticket_obj.all_ticket_field
        #     condition_expression_list = json.loads(transition.condition_expression)
        #     for condition_expression in condition_expression_list:
        #         expression = condition_expression.get('expression')
        #         expression_format = expression.format(**ticket_value)
        #         if eval(expression_format):
        #             break
        if transition.source_state.distribute_type == "any":  # 其中一人处理即可
            if transition.destination_state.state_type == constant.STATE_TYPE_END:  # 目标状态是结束状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_FINISH
            else:  # 目标状态是开始/中间状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
                self.ticket_obj.state = transition.destination_state.id
        else:
            # TODO 判断所有人是否都已经处理
            if transition.destination_state.state_type == constant.STATE_TYPE_END:  # 目标状态是结束状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_FINISH
            else:  # 目标状态是开始/中间状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
        self.ticket_obj.state = transition.destination_state.id
        self.ticket_obj.participant = self.user.username
        self.ticket_obj.save()
        self._ticket_log(self.ticket_obj.state_display, constant.TICKET_ACT_STATE_PASS, self.data["suggestion"])
        return True, ''

    def _transition_state_for_deny(self):
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_REFUSE  # 不通过进入 "未通过" 状态
        self.ticket_obj.participant = self.user.username
        self.ticket_obj.save()
        self._ticket_log(self.ticket_obj.state_display, constant.TICKET_ACT_STATE_REFUSE, self.data["suggestion"])
        return True, ''
