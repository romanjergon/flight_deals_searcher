import os
from dotenv import load_dotenv
from mail_notifier import MailNotifier

load_dotenv()


def test_send_notif_mail():
    notifier = MailNotifier(
        smtp_host="smtp.gmail.com",
        smtp_port=587,
        notification_mailbox=os.environ["NOTIFICATION_MAILBOX"],
        mail_password=os.environ["MAIL_PASSWORD"],
        personal_mailbox=os.environ["PERSONAL_MAILBOX"],
    )

    result = notifier.send_notif_mail(
        "This is testing mail for mail notifier class", "Lorem Ipsum"
    )
    assert (
        len(result) == 0
    ), "should be zero as no recipient should be rejected by the server"
