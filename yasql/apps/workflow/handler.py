# -*- coding:utf-8 -*-
# by pandonglin
from workflow import constant, models, tasks


class TicketFlow:
    def __init__(self, username, ticket_obj, data=None):
        self.username = username
        self.ticket_obj = ticket_obj
        self.data = data

    def handle(self):
        if self.ticket_obj.act_status in constant.TICKET_ACT_STATE_END:
            return False, "工单已完成"

        if self.data["state"] != self.ticket_obj.state:
            return False, "工单状态错误"

        if self.data["action"] not in ["deny", "allow", "close"]:
            return False, "无效的操作"

        if self.data["action"] == "close":
            return self.close_ticket()
        else:
            return self.transition_state()

    def close_ticket(self):
        if self.username not in self.ticket_obj.all_relation_user:  # 判断用户权限
            return False, "无权限执行"
        self.ticket_obj.participant = self.username
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_CLOSE
        self.ticket_obj.save()
        self.add_ticket_log("关闭工单", constant.TICKET_ACT_STATE_CLOSE)
        models.TicketFlowUser.objects.filter(ticket=self.ticket_obj, process=False).delete()
        # 推送消息
        tasks.msg_notice.delay(
            pk=self.ticket_obj.pk,
            op="_close",
            title="关闭流程工单",
            username=self.username
        )
        return True, '关闭成功'

    def transition_state(self):
        """转换状态"""
        if self.username not in self.ticket_obj.cur_state_relation_user:  # 判断用户权限
            return False, "无权限执行"

        if self._check_relation_user_has_action():   # 判断用户是否重复执行
            return False, "您已经处理过"

        if self.data["action"] == "allow":
            return self.transition_state_for_allow()
        else:
            return self.transition_state_for_deny()

    def _check_relation_user_has_action(self):
        participant = self.ticket_obj.tf_user.filter(ticket=self.ticket_obj, state=self.ticket_obj.state, username=self.username,
                                                     process=True)
        if participant:
            return True
        else:
            return False

    def _get_state_all_user_has_processed(self, distribute_type="all"):
        """判断所有用户都已经处理"""
        cur_state = models.State.objects.get(id=self.ticket_obj.state)
        if cur_state.participant_type in [constant.PARTICIPANT_TYPE_ROBOT, constant.PARTICIPANT_TYPE_HOOK]:
            return True

        tf_users = self.ticket_obj.tf_user.filter(ticket=self.ticket_obj, state=self.ticket_obj.state)
        if distribute_type == "all":
            return all([user.process for user in tf_users])
        else:
            return any([user.process for user in tf_users])

    def update_participant_action(self, clean_flag=False):
        """更新相关人操作记录"""
        ticketflow_user = models.TicketFlowUser.objects.get(ticket=self.ticket_obj, state=self.ticket_obj.state,
                                                            username=self.username)
        ticketflow_user.process = True
        ticketflow_user.action = self.data["action"]
        ticketflow_user.save()
        if clean_flag:  # 清洗当前阶段相关人
            models.TicketFlowUser.objects.filter(ticket=self.ticket_obj, state=self.data["state"], process=False).delete()

    def create_next_state_relation_user(self):
        # 更新下一流程相关人
        relation_user_list = self.ticket_obj.cur_state_relation_user
        for user in relation_user_list:
            models.TicketFlowUser.objects.create(ticket=self.ticket_obj, state=self.ticket_obj.state, username=user)

    def exec_auto_process(self):
        # 是否有需要自动处理阶段
        if self.ticket_obj.next_state.participant_type == constant.PARTICIPANT_TYPE_ROBOT:  # 机器人处理阶段
            tasks.run_task.delay(self.ticket_obj.id)
        elif self.ticket_obj.next_state.participant_type == constant.PARTICIPANT_TYPE_HOOK:  # hook阶段
            tasks.hook_task.delay(self.ticket_obj.id)
        else:  # 其他模式跳过
            pass

    def add_ticket_log(self, state, status, suggestion=None, ticket_data=None):
        """记录工单日志"""
        models.TicketFlowLog.objects.create(ticket=self.ticket_obj, participant=self.username, state=state,
                                            act_status=status, suggestion=suggestion, ticket_data=ticket_data)

    def transition_state_for_allow(self):
        allow_transition = models.Transition.objects.filter(workflow=self.ticket_obj.workflow,
                                                            source_state=self.ticket_obj.state, attribute_type=1).first()
        if allow_transition is None:
            return False, '状态流转未配置'

        self.update_participant_action()  # 更新相关人状态
        self.ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
        self.ticket_obj.participant = self.username
        self.ticket_obj.save()
        self.add_ticket_log(self.ticket_obj.state_display, constant.TICKET_ACT_STATE_PASS, self.data.get("suggestion"))

        # if transition.condition_expression and json.loads(transition.condition_expression):   # 状态流转判断
        #     ticket_value = self.ticket_obj.all_ticket_field
        #     condition_expression_list = json.loads(transition.condition_expression)
        #     for condition_expression in condition_expression_list:
        #         expression = condition_expression.get('expression')
        #         expression_format = expression.format(**ticket_value)
        #         if eval(expression_format):
        #             break

        # 判断状态是否向下一步流转
        if self._get_state_all_user_has_processed(allow_transition.source_state.distribute_type):  # 所有人都已经处理
            self.ticket_obj.state = allow_transition.destination_state.id
            self.ticket_obj.save()
            if allow_transition.destination_state.state_type == constant.STATE_TYPE_END:  # 目标状态是结束状态
                self.ticket_obj.act_status = constant.TICKET_ACT_STATE_FINISH
                self.ticket_obj.save()
                models.TicketFlowUser.objects.filter(ticket=self.ticket_obj, process=False).delete()
            else:
                self.create_next_state_relation_user()
                self.exec_auto_process()
        else:
            pass
        # 推送消息
        tasks.msg_notice.delay(
            pk=self.ticket_obj.pk,
            op="_next_flow",
            title="流程工单已更新",
            username=self.username
        )
        return True, ''

    def transition_state_for_deny(self):
        deny_transition = models.Transition.objects.filter(workflow=self.ticket_obj.workflow,
                                                           source_state=self.ticket_obj.state, attribute_type=2).first()

        allow_transition = models.Transition.objects.filter(workflow=self.ticket_obj.workflow,
                                                            source_state=self.ticket_obj.state, attribute_type=1).first()

        if deny_transition is None and allow_transition is None:
            return False, '状态流转未配置'

        self.ticket_obj.participant = self.username
        self.ticket_obj.save()
        self.add_ticket_log(self.ticket_obj.state_display, constant.TICKET_ACT_STATE_REFUSE, self.data.get("suggestion"))
        if deny_transition:   # 配置了拒绝流程时
            self.update_participant_action(clean_flag=True)
            self.ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
            self.ticket_obj.state = deny_transition.destination_state.id
            self.ticket_obj.save()
            self.create_next_state_relation_user()
            self.exec_auto_process()
        else:       # 没有拒绝流程关闭工单
            self.ticket_obj.act_status = constant.TICKET_ACT_STATE_REFUSE  # 不通过进入 "未通过" 状态
            self.ticket_obj.save()

        # 推送消息
        tasks.msg_notice.delay(
            pk=self.ticket_obj.pk,
            op="_next_flow",
            title="流程工单已更新",
            username=self.username
        )
        return True, ''
