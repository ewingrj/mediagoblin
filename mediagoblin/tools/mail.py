# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import smtplib
from email.MIMEText import MIMEText
from mediagoblin import mg_globals
from mediagoblin.tools import common

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### Special email test stuff begins HERE
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# We have two "test inboxes" here:
#
# EMAIL_TEST_INBOX:
# ----------------
#   If you're writing test views, you'll probably want to check this.
#   It contains a list of MIMEText messages.
#
# EMAIL_TEST_MBOX_INBOX:
# ----------------------
#   This collects the messages from the FakeMhost inbox.  It's reslly
#   just here for testing the send_email method itself.
#
#   Anyway this contains:
#    - from
#    - to: a list of email recipient addresses
#    - message: not just the body, but the whole message, including
#      headers, etc.
#
# ***IMPORTANT!***
# ----------------
# Before running tests that call functions which send email, you should
# always call _clear_test_inboxes() to "wipe" the inboxes clean.

EMAIL_TEST_INBOX = []
EMAIL_TEST_MBOX_INBOX = []


class FakeMhost(object):
    """
    Just a fake mail host so we can capture and test messages
    from send_email
    """
    def login(self, *args, **kwargs):
        pass

    def sendmail(self, from_addr, to_addrs, message):
        EMAIL_TEST_MBOX_INBOX.append(
            {'from': from_addr,
             'to': to_addrs,
             'message': message})


def _clear_test_inboxes():
    global EMAIL_TEST_INBOX
    global EMAIL_TEST_MBOX_INBOX
    EMAIL_TEST_INBOX = []
    EMAIL_TEST_MBOX_INBOX = []


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
### </Special email test stuff>
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def send_email(from_addr, to_addrs, subject, message_body):
    """
    Simple email sending wrapper, use this so we can capture messages
    for unit testing purposes.

    Args:
     - from_addr: address you're sending the email from
     - to_addrs: list of recipient email addresses
     - subject: subject of the email
     - message_body: email body text
    """
    if common.TESTS_ENABLED or mg_globals.app_config['email_debug_mode']:
        mhost = FakeMhost()
    elif not mg_globals.app_config['email_debug_mode']:
        mhost = smtplib.SMTP(
            mg_globals.app_config['email_smtp_host'],
            mg_globals.app_config['email_smtp_port'])

        # SMTP.__init__ Issues SMTP.connect implicitly if host
        if not mg_globals.app_config['email_smtp_host']:  # e.g. host = ''
            mhost.connect()  # We SMTP.connect explicitly

    if mg_globals.app_config['email_smtp_user'] \
            or mg_globals.app_config['email_smtp_pass']:
        mhost.login(
            mg_globals.app_config['email_smtp_user'],
            mg_globals.app_config['email_smtp_pass'])

    message = MIMEText(message_body.encode('utf-8'), 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = from_addr
    message['To'] = ', '.join(to_addrs)

    if common.TESTS_ENABLED:
        EMAIL_TEST_INBOX.append(message)

    if mg_globals.app_config['email_debug_mode']:
        print u"===== Email ====="
        print u"From address: %s" % message['From']
        print u"To addresses: %s" % message['To']
        print u"Subject: %s" % message['Subject']
        print u"-- Body: --"
        print message.get_payload(decode=True)

    return mhost.sendmail(from_addr, to_addrs, message.as_string())