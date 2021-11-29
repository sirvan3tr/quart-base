import os
from quart import render_template
from flask_mail import Message
from app import create_app
from app import mail
from contextvars import copy_context
from functools import partial


async def run_sync(func):
  loop = asyncio.get_running_loop()
  return await loop.run_in_executor(
    None, copy_context().run, func,
  )


async def send_email(recipient, subject, template, **kwargs):
  app = create_app(os.getenv('QUART_CONFIG') or 'default')
  async with app.app_context():
    msg = Message(
      app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
      sender=app.config['EMAIL_SENDER'],
      recipients=[recipient])
    msg.body = await render_template(template + '.txt', **kwargs)
    msg.html = await render_template(template + '.html', **kwargs)
    print(msg)
    mail.send(msg)


async def send_emailx(recipient, subject, template, **kwargs):
  async with app.app_context():
    await run_sync(partial(mailing, recipient, subject, template, **kwargs))

