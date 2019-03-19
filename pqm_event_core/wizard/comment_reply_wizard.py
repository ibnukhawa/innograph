# -*- coding:utf-8 -*-
from odoo import models, fields

class EventCommentReply(models.TransientModel):
	_name = 'event.comment.reply'

	comment_id = fields.Many2one('event.comment', string="Comment")
	event_id = fields.Many2one('event.event', related="comment_id.event_id", string="Event")
	email_to = fields.Char(related="comment_id.email")
	reply_comment = fields.Text(string="Reply")

	def send_reply_comment(self):
		user = self.env.user
		reply = self.env['event.comment'].create({
			'event_id': self.event_id.id,
			'user_id': user.id,
			'comment': self.reply_comment,
		})
		self.comment_id.reply_id = reply.id
		if reply:
			context = {
				'comment': self.comment_id,
				'reply': self.reply_comment
			}
			email = self.env.ref('pqm_event_core.email_reply_comment')
			email.with_context(data=context).send_mail(self.id, force_send=True)
		return True
		