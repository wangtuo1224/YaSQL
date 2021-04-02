# -*- coding:utf-8 -*-
# by pandonglin
from workflow import constant, models


class TicketFlow:
    def __init__(self, user, data, ticket_obj=None):
        self.user = user
        self.data = data
        self.ticket_obj = ticket_obj

    def handle(self):
        if self.data["state"] != self.ticket_obj.state:
            return False, "工单状态错误"

        if self.data["action"] not in ["deny", "allow", "close"]:
            return False, "无效的操作"

        if self.ticket_obj.act_status in constant.TICKET_ACT_STATE_END:
            return False, "工单已完成"

        if self.user.is_superuser:  # 超级管理员流程，加入到关联用户中
            t_user_obj, _ = models.TicketFlowUser.objects.get_or_create(ticket=self.ticket_obj, state=self.data["state"],
                                                                        username=self.user.username)
            t_user_obj.process = True
            t_user_obj.action = self.data["action"]
            t_user_obj.save()

        if self.data["action"] == "close":
            return self.close_ticket()
        else:
            return self.next_flow()

    def close_ticket(self):
        if self.user.username not in self.ticket_obj.relation_user:  # 判断用户权限
            return False, "无权限执行"

        self.ticket_obj.participant = self.user.username
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_CLOSE
        self.ticket_obj.save()
        models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username,
                                            state="关闭工单", act_status=constant.TICKET_ACT_STATE_CLOSE)
        return True, '关闭成功'

    def next_flow(self):
        if self.user.username not in self.ticket_obj.relation_user:   # 判断用户权限
            return False, "无权限执行"

        if self.ticket_obj.act_status in constant.TICKET_ACT_STATE_END:
            return False, "工单已结束"

        if self.data["action"] == "allow":
            if self.user.is_superuser:  # 超级管理员直接进入下一阶段
                self.ticket_obj.state = self.ticket_obj.next_state or self.ticket_obj.state
            else:
                # todo check state
                if self.check_user_action():  # 根据条件判断是否满足所有条件，则更新阶段
                    self.ticket_obj.state = self.ticket_obj.next_state or self.ticket_obj.state
            self.ticket_obj.participant = self.user.username
            self.ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态
            self.ticket_obj.save()

            if not self.ticket_obj.next_state:  # 结束阶段修改为完成状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_FINISH
            self.ticket_obj.save()
            models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username,
                                                suggestion=self.data["suggestion"], state=self.ticket_obj.state_display,
                                                act_status=constant.TICKET_ACT_STATE_PASS)
        else:
            self.ticket_obj.participant = self.user.username
            self.ticket_obj.act_status = constant.TICKET_ACT_STATE_REFUSE   # 不通过进入 "未通过" 状态
            self.ticket_obj.save()
            models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.user.username,
                                                suggestion=self.data["suggestion"], state=self.ticket_obj.state_display,
                                                act_status=constant.TICKET_ACT_STATE_REFUSE)
        return True, ''

    def check_user_action(self):
        return True