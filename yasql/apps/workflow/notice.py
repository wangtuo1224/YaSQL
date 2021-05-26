# -*- coding:utf-8 -*-
# by pandonglin
import json
import requests
from celery.utils.log import get_task_logger
from dingtalkchatbot.chatbot import DingtalkChatbot
from django.core.mail import EmailMessage

from config import NOTICE_URL, NOTICE
from workflow import models, constant
from users.models import UserAccounts

logger = get_task_logger('celery.logger')


class MsgNotice(object):
    """
    工单通知模块，支持：钉钉/邮件/企业微信
    注：钉钉和企业微信需要拉群，如果用户的手机号存在，则在群里面at用户，否则at all
    进阶：当然您也可以直接对接钉钉或企业微信的企业接口，这个需要您自己开发接口
          如此，消息会直接at用户，不需要拉群，会发送到个人消息中心
    """

    def __init__(self, **kwargs):
        # 工单的基本信息
        self.pk = kwargs.get('pk')  # 工单的主键
        self.op = kwargs.get('op')  # 操作，如：commit/approve/feedback等
        self.title = kwargs.get('title')
        self.username = kwargs.get('username')  # 用户

        # 获取工单信息
        self.ticket_obj = models.TicketFlow.objects.get(pk=self.pk)
        self.notice_url = f"{NOTICE_URL}/workflow/ticket/detail/{self.pk}"

        # 获取申请人mobile&email
        self.creator_mobile = list(filter(None, UserAccounts.objects.filter(username=self.ticket_obj.creator).values_list('mobile', flat=True)))
        self.creator_email = list(filter(None, UserAccounts.objects.filter(username=self.ticket_obj.creator).values_list('email', flat=True)))

        # 获取相关人mobile&email
        self.participant_mobile = list(filter(None, UserAccounts.objects.filter(username__in=self.ticket_obj.cur_state_relation_user).values_list('mobile', flat=True)))
        self.participant_email = list(filter(None, UserAccounts.objects.filter(username__in=self.ticket_obj.cur_state_relation_user).values_list('email', flat=True)))

        # 格式化工单进度
        self.fmt_progress = self.ticket_obj.state_display

    def push(self, content=None, mobiles=None, emails=None):
        if NOTICE['DINGDING']['enabled']:
            dingding_content = content.copy()
            dingding_content.append(f"请访问 {self.notice_url} 查看详情")
            self.dingding(dingding_content, mobiles)
        if NOTICE['WEIXIN']['enabled']:
            weixin_content = content.copy()
            weixin_content.append(f"\n请访问 [{self.notice_url}]({self.notice_url}) 查看详情")
            self.weixin(weixin_content, mobiles)
        if NOTICE['MAIL']['enabled']:
            mail_content = content.copy()
            mail_content.append(f"请访问 {self.notice_url} 查看详情")
            self.mail(mail_content, emails)

    def dingding(self, content=None, mobiles=None):
        # 此处您可以改写下面的接口对接企业接口，消息会推送到个人的消息中心
        key = NOTICE['DINGDING']['key']
        xiaoding = DingtalkChatbot(NOTICE['DINGDING']['webhook'])
        content = '\n'.join(['\n\n'.join(content), key])
        # 如果通知人mobile存在，at指定的用户，否则at all
        if mobiles:
            xiaoding.send_markdown(title='工单通知', text=content, at_mobiles=mobiles)
        else:
            xiaoding.send_markdown(title='工单通知', text=content, is_at_all=True)

    def weixin(self, content, mobiles=None):
        # 此处您可以改写下面的接口对接企业接口，消息会推送到个人的消息中心
        webhook = NOTICE['WEIXIN']['webhook']
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "msgtype": "markdown",
            "markdown": {"content": '\n'.join(content)},
            "mentioned_mobile_list": mobiles
        }
        request = requests.post(
            url=webhook,
            data=json.dumps(data),
            timeout=3,
            headers=headers
        )
        # 记录下请求响应的信息
        logger.info(request.json())

    def mail(self, content, emails=None):
        try:
            if self.op == '_commit':
                # 发送邮件
                msg = EmailMessage(subject=self.title,
                                   body='<br>'.join(content),
                                   from_email=NOTICE['MAIL']['email_host_user'],
                                   to=emails,
                                   )
            else:
                # 发送邮件
                headers = {'Reply: ': emails}
                title = 'Re: ' + self.title
                msg = EmailMessage(subject=title,
                                   body='<br>'.join(content),
                                   from_email=NOTICE['MAIL']['email_host_user'],
                                   to=emails,
                                   reply_to=emails,
                                   headers=headers)
            msg.content_subtype = "html"
            msg.send()
        except Exception as err:
            logger.error(err)

    def _commit(self):
        """提交工单时，发送消息"""
        content = [
            f"您好，{self.username}提交了工单，^_^",
            f">标题: {self.title}",
            f">工单类型: {self.ticket_obj.workflow.name}",
            f">申请人: {self.ticket_obj.creator}",
        ]

        self.push(
            content=content,
            mobiles=list(set(self.creator_mobile + self.participant_mobile)),
            emails=list(set(self.creator_email + self.participant_email))
        )

    def _next_flow(self):
        """审核操作，发送信息"""
        # 发送审核动作通知
        content = [
            f"您好，{self.username}已处理了工单，请关注，^_^",
            f">工单标题: {self.title}",
            f">工单类型: {self.ticket_obj.workflow.name}",
            f">申请人: {self.ticket_obj.creator}",
            f">工单状态: {self.fmt_progress}",
        ]

        self.push(
            content=content,
            mobiles=list(set(self.creator_mobile + self.participant_mobile)),
            emails=list(set(self.creator_email + self.participant_email))
        )

    def _close(self):
        """关闭"""
        content = [
            f"您好，工单已被{self.username}关闭 (⊙︿⊙)",
            f">工单标题: {self.title}",
            f">工单类型: {self.ticket_obj.workflow.name}",
            f">申请人: {self.ticket_obj.creator}",
            f">工单状态: {self.fmt_progress}",
            f">关闭人: {self.username}"
        ]
        self.push(
            content=content,
            mobiles=list(set(self.creator_mobile)),
            emails=list(set(self.creator_email))
        )

    def run(self):
        if self.op == '_commit':
            self._commit()
        if self.op == '_next_flow':
            self._next_flow()
        if self.op == '_close':
            self._close()
