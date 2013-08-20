from mimetools import Message
from StringIO import StringIO

def get_host_and_port(raw_message):
    request_line, headers = raw_message.split('\r\n', 1)
    headers = Message(StringIO(headers))
    host_header = headers.get('Host', ':')
    try:
        host, port = host_header.split(':', 1)
        port = int(port)
    except ValueError:
        host, port = host_header, 80
    return host, port


