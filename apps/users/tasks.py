# -*- coding: utf-8 -*-
from django.core.mail import send_mail
from sleekxmpp import ClientXMPP

from celery import shared_task

from django.conf import settings


class SendMsgBot(ClientXMPP):
    def __init__(self, recipient, message):
        ClientXMPP.__init__(self, settings.XMPP_JID, settings.XMPP_PWD)

        self.recipient = recipient
        self.msg = message
        self.add_event_handler("session_start", self.start, threaded=True)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        self.disconnect(wait=True)


@shared_task(soft_time_limit=60*3)  # мягкое ограничение по времени(sec)
def send_xmppp_message(recipient, message):
    bot = SendMsgBot(recipient, message)

    bot.register_plugin('xep_0030')  # Service Discovery
    bot.register_plugin('xep_0199')  # XMPP Ping

    connect = bot.connect(
        address=(settings.XMPP_SERVER, settings.XMPP_PORT)
    )

    if connect:
        bot.process(block=False)


@shared_task(soft_time_limit=60*3)  # мягкое ограничение по времени(sec)
def send_mail_to_user(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)
