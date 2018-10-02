from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage

from VLE.models import Role


def send_email_verification_link(user):
    """Sends an email verification link to the users email adress."""
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    recovery_link = '%s/EmailVerification/%s' % (settings.BASELINK, token)
    email_body = '''\
We have received a request for email verification, if you have not made this request please ignore this email.
If you did make the request please visit the link below to verify your email address:

{recovery_link}

Or copy the token manually: {token}\
'''.format(recovery_link=recovery_link, token=token)

    email = EmailMessage(
        subject='eJourn.al email verification',
        body=email_body,
        from_email='noreply@ejourn.al',
        headers={'Content-Type': 'text/plain'},
        to=[user.email]
    )

    email.send()


def send_password_recovery_link(user):
    """Sends an email verification link to the users email address.."""
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    recovery_link = '%s/PasswordRecovery/%s/%s' % (settings.BASELINK, user.username, token)
    email_body = '''\
We have received a request for password recovery, if you have not made this request please ignore this email.
If you did make the request please visit the link below and set a new password:

{recovery_link}\
'''.format(recovery_link=recovery_link)

    email = EmailMessage(
        subject='eJourn.al password recovery',
        body=email_body,
        from_email='noreply@ejourn.al',
        headers={'Content-Type': 'text/plain'},
        to=[user.email]
    )

    email.send()


def send_email_feedback(user, files, topic, ftype, feedback, user_agent, url):
    """Sends the feedback of an user to the developers."""
    f_subject = "[Feedback] {}".format(topic[0])
    f_body = "TYPE: {}\n\n".format(ftype[0])
    f_body += "FEEDBACK BY: {}\n".format(user.username)
    f_body += "EMAIL: {}\n".format(user.email)
    f_body += "TEACHER: {}\n".format(user.is_teacher)
    f_body += "ROLES: {}\n".format(Role.objects.filter(role__user=user).values('name'))
    f_body += "USER-AGENT: {}\n".format(user_agent[0])
    f_body += "URL: {}\n\n".format(url[0])
    f_body += "THE FEEDBACK:\n{}".format(feedback[0])

    r_subject = "[eJournal] Submitted feedback"
    r_body = "Hi {},\n\n".format(user.first_name)
    r_body += "Thank you for your feedback! Below you will find a copy of your given feedback. "
    r_body += "If you supplied attachments, then they are added to this e-mail as well.\n\n"
    r_body += "The feedback:\n\n{}\n\n".format(feedback[0])
    r_body += "We might reply to your feedback to ask some questions or just to say thanks!\n\n"
    r_body += "Kind Regards,\n\nThe eJournal Team"

    attachments = []
    for file in files:
        attachments.append((file.name, file.read(), file.content_type))

    reply = EmailMessage(
        subject=r_subject,
        body=r_body,
        attachments=attachments,
        from_email='support@ejourn.al',
        headers={'Content-Type': 'text/plain'},
        to=[user.email]
    )

    forward = EmailMessage(
        subject=f_subject,
        body=f_body,
        attachments=attachments,
        from_email='support@ejourn.al',
        to=['support@ejourn.al'],
        headers={'Content-Type': 'text/plain'},
        reply_to=[user.email]
    )

    reply.send()
    forward.send()
