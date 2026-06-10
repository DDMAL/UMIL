import logging

from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

logger = logging.getLogger("VIM.email")


class LoggingEmailBackend(SMTPBackend):
    """SMTP backend that logs every email attempt, success, and failure."""

    def send_messages(self, email_messages):
        messages = list(email_messages)
        for msg in messages:
            logger.info("EMAIL_QUEUED subject=%r to=%r", msg.subject, msg.to)
        try:
            sent = super().send_messages(messages)
            for msg in messages:
                logger.info("EMAIL_SENT subject=%r to=%r", msg.subject, msg.to)
            return sent
        except Exception as exc:
            for msg in messages:
                logger.error(
                    "EMAIL_FAILED subject=%r to=%r error=%r",
                    msg.subject,
                    msg.to,
                    str(exc),
                    exc_info=True,
                )
            raise
