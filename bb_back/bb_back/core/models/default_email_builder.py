from django.core.mail import EmailMultiAlternatives


class DefaultEmailBuilder:
    def __init__(self, email_from, email_subject, user_emails):
        self._email_from = email_from
        self._email_subject = email_subject
        self._user_emails = user_emails

    def get_email_message(self):
        return EmailMultiAlternatives(subject=self._email_subject,
                                      from_email=self._from_email,
                                      to=self._to_users_emails)

