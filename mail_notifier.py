import smtplib


class MailNotifier:
    # This class is responsible for sending notifications

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        notification_mailbox: str,
        mail_password: str,
        personal_mailbox: str,
    ):
        self.host = smtp_host
        self.port = smtp_port
        self.notification_mailbox = notification_mailbox
        self.mail_password = mail_password
        self.personal_mailbox = personal_mailbox

    def send_notif_mail(
        self,
        subject: str,
        body: str,
    ):
        """Send notification mail from my notification mailbox to my personal mailbox"""

        with smtplib.SMTP(host="smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(self.notification_mailbox, self.mail_password)
            connection.sendmail(
                self.notification_mailbox,
                self.personal_mailbox,
                msg=f"Subject:{subject}\n\n{body}",
            )


def mail_test():
    notifier = MailNotifier(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        notification_mailbox="roman.jergon.notifications@gmail.com",
        mail_password="This1sMyTechPass",
        personal_mailbox="roman.jergon@gmail.com",
    )

    notifier.send_notif_mail(
        "This is testing mail for mail notifier class", "Lorem Ipsum"
    )


if __name__ == "__main__":
    mail_test()
