import imapclient
import os
import yaml
import ssl
import datetime
import email


class CONFIG:
    pass


with open(os.path.expanduser('~/.mailhack'), 'r') as stream:
    cfg = yaml.load(stream)
    print(cfg)
    CONFIG.folder = os.path.expanduser(cfg['folder'])
    CONFIG.accounts = cfg['accounts']
    acc_info = cfg['accounts'][0]
    CONFIG.host, CONFIG.port = acc_info['imap'].split(':')
    CONFIG.username = acc_info['username']
    CONFIG.password = acc_info['password']


def get_imap_client(host, port, username, password):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    server = imapclient.IMAPClient(host=host, port=port, use_uid=True, ssl=True, ssl_context=ssl_context)
    server.login(username, password)
    return server


def process_mail(start_days_ago=0, num_days=10):
    im = get_imap_client(CONFIG.host, CONFIG.port, CONFIG.username, CONFIG.password)
    im.select_folder('INBOX')

    start_date = datetime.date.today() - datetime.timedelta(days=start_days_ago - 1)

    for i in range(num_days):
        end_date = start_date
        start_date = start_date - datetime.timedelta(days=1)

        dir_path = os.path.join(CONFIG.folder, str(start_date.year), str(start_date.month), str(start_date.day))
        os.makedirs(dir_path, exist_ok=True)
        search_param = ['SINCE', start_date, 'BEFORE', end_date]
        print(search_param)
        las_day_msg = im.search(search_param)
        print(las_day_msg)

        for uid, message_data in im.fetch(las_day_msg, 'RFC822').items():
            email_bytes = message_data[b'RFC822']
            file_path = os.path.join(dir_path, '%s.eml' % str(uid))
            with open(file_path, 'wb') as eml_file:
                eml_file.write(email_bytes)
            email_message = email.message_from_bytes(email_bytes)
            print(uid, email_message.get('From'), email_message.get('Subject'))

    im.logout()
