# -*- coding:utf-8 -*-
# by pandonglin
import requests, json
from celery import shared_task
from celery.utils.log import get_task_logger
from workflow import models, utils, constant
from workflow.notice import MsgNotice

logger = get_task_logger(__name__)


@shared_task(queue='workflow', acks_late=False)
def run_task(ticket):
    """处理任务"""
    pass


@shared_task(queue='workflow', acks_late=False)
def hook_task(ticket):
    """hook任务"""
    ticket_obj = models.TicketFlow.objects.filter(id=ticket).first()
    ticket_obj.act_status = constant.TICKET_ACT_STATE_DOING  # 更新状态中
    ticket_obj.participant = "hookbot"
    ticket_obj.save()

    state_obj = models.State.objects.filter(id=ticket_obj.state).first()
    hook_config = state_obj.participant_data
    hook_config_dict = json.loads(hook_config)
    hook_url = hook_config_dict.get('hook_url')
    hook_token = hook_config_dict.get('hook_token')
    extra_info = hook_config_dict.get('extra_info')

    all_ticket_data = ticket_obj.all_ticket_field
    if extra_info is not None:
        all_ticket_data.update(dict(extra_info=extra_info))

    header = utils.gen_hook_signature(hook_token)
    try:
        r = requests.post(hook_url, headers=header, json=all_ticket_data, timeout=10)
        result = r.json()
    except Exception as e:
        result = dict(code=-1, msg=e.__str__())
    if result.get('code') == 0:   # 调用成功
        allow_transition = models.Transition.objects.filter(workflow=ticket_obj.workflow, source_state=ticket_obj.state,
                                                            attribute_type=1).first()
        if allow_transition is None:
            return False, '状态流转未配置'

        ticket_obj.state = allow_transition.destination_state.id
        ticket.save()
        relation_user_list = ticket_obj.cur_state_relation_user()
        for user in relation_user_list:
            models.TicketFlowUser.objects.create(ticket=ticket_obj, state=ticket_obj.state, username=user)
        return True, ''
    else:
        ticket_obj.act_status = constant.TICKET_ACT_STATE_FAIL
        ticket_obj.save()
        return False, '执行失败'


@shared_task()
def msg_notice(**kwargs):
    MsgNotice(**kwargs).run()
