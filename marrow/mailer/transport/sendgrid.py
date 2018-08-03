# -*- coding: utf-8 -*-

import sendgrid

from sendgrid.helpers.mail import Email, Content, Mail
from marrow.mailer.exc import MailConfigurationException, DeliveryFailedException, MessageFailedException

__all__ = ['SendgridTransport']

log = __import__('logging').getLogger(__name__)


class SendgridTransport(object):
    __slots__ = ('ephemeral', 'user', 'key', 'bearer')
    
    def __init__(self, config):
        self.bearer = False
        if not 'user' in config:
            self.bearer = True
        else:
            self.user = config.get('user')
        self.key = config.get('key')
    
    def startup(self):
        pass
    
    def deliver(self, message):

        to = Email(message.to)
        author = Email(email=message.author[0].address.encode(message.encoding), name=message.author[0].name.encode(message.encoding))
        mail = Mail(author, message.subject.encode(message.encoding), to, Content('text/plain', message.plain))

        if message.rich:
            mail.add_content(Content('text/html', message.rich))
        
        # Sendgrid doesn't accept CC over the api
        if message.cc:
            mail.personalizations[0].add_to(Email(message.cc))

        if message.bcc:
            mail.personalizations[0].add_bcc(Email(message.bss[0].address.encode(message.encoding)))
        
        if message.reply:
            mail.reply_to = message.reply.encode(message.encoding)
        
        if message.attachments:
            # Not implemented yet
            """
            attachments = []
            
            for attachment in message.attachments:
                attachments.append((
                        attachment['Content-Disposition'].partition(';')[2],
                        attachment.get_payload(True)
                    ))
            
            msg.attachments = attachments
            """
            raise MailConfigurationException()
        
        

        sg = sendgrid.SendGridAPIClient(apikey=self.key)
        response = sg.client.mail.send.post(request_body=mail.get())
        respcode = response.status_code

        if respcode >= 400 and respcode <= 499:
            raise MessageFailedException(response.read())
        elif respcode >= 500 and respcode <= 599:
            raise DeliveryFailedException(message, "Sendgrid service unavailable.")
    
    def shutdown(self):
        pass
