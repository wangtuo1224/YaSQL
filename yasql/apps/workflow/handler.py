# -*- coding:utf-8 -*-
# by pandonglin
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
            return self.next_flow()

    def close_ticket(self):
        self.ticket_obj.participant = self.user.username
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_CLOSE
        self.ticket_obj.save()
        self._update_user_action()
        models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username,
                                            state="关闭工单", act_status=constant.TICKET_ACT_STATE_CLOSE)
        return True, '关闭成功'

    def next_flow(self):
        if self.data["action"] == "allow":
            ticket_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
            log_status = constant.TICKET_ACT_STATE_PASS
        else:
            ticket_status = constant.TICKET_ACT_STATE_REFUSE   # 不通过进入 "未通过" 状态
            log_status = constant.TICKET_ACT_STATE_REFUSE

        self.ticket_obj.act_status = ticket_status
        self.ticket_obj.participant = self.user.username
        self.ticket_obj.save()

        models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username,
                                            suggestion=self.data["suggestion"], state=self.ticket_obj.state_display,
                                            act_status=log_status)
        return True, ''

    def _check_user_action(self):
        participant = self.ticket_obj.tf_user.filter(ticket=self.ticket_obj, state=self.ticket_obj.state,
                                                     username=self.user.username, process=True)
        if participant:
            return True

    def _update_user_action(self):
        models.TicketFlowUser.objects.create(ticket=self.ticket_obj, state=self.data["state"],
                                             username=self.user.username, process=True, action=self.data["action"])

    def _update_ticket_state(self):
        transition = models.Transition.objects.filter(workflow=self.ticket_obj.workflow,
                                                      source_state=self.ticket_obj.state,
                                                      destination_state=self.ticket_obj.next_state)

        # if self.ticket_obj.next_state:  # 检查当前阶段是否为最终阶段
        #     if self._update_ticket_state():  # 满足条件 进入下一阶段
        #         self.ticket_obj.state = self.ticket_obj.next_state
        #         self.ticket_obj.save()
        # else:  # 结束阶段工单修改为完成状态
        #     self.ticket_obj.act_status = constant.TICKET_ACT_STATE_FINISH
        #     self.ticket_obj.save()
        return True
