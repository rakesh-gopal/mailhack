import imapclient
import os
import yaml
import ssl
import datetime
import email

ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def get_imap_client(host, port, username, password):
    server = imapclient.IMAPClient(host=host, port=port, use_uid=True, ssl=True, ssl_context=ssl_context)
    server.login(username, password)
    return server


with open(os.path.expanduser('~/.mailhack'), 'r') as stream:
    acc_info = yaml.load(stream)[0]
    print(acc_info)

host, port = acc_info['imap'].split(':')
im = get_imap_client(host, port, acc_info['username'], acc_info['password'])
im.select_folder('INBOX')


start_date = datetime.date.today() + datetime.timedelta(days=1)

for i in range(50):
    end_date = start_date
    start_date = start_date - datetime.timedelta(days=1)

    las_day_msg = im.search(['SINCE', start_date, 'BEFORE', end_date])

    for uid, message_data in im.fetch(las_day_msg, 'RFC822').items():
        email_bytes = message_data[b'RFC822']
        email_message = email.message_from_bytes(email_bytes)
        print(uid, email_message.get('From'), email_message.get('Subject'))
