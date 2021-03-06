from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.errors import AnsibleError
from ansible.module_utils.urls import open_url, ConnectionError, SSLValidationError
from ansible.module_utils._text import to_native
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError
from ansible.utils.display import Display

display = Display()

class Client:

    def __init__(self, username, password, options={}):

        self.options = options
        self.options['endpoint'] = 'https://aperture.section.io/api/v1'

        if 'headers' not in self.options:
            self.options['headers'] = {}

        if not isinstance(self.options, dict):
            raise AnsibleError("Expecting client headers to be dict.")

        self.options['headers']['Content-Type'] = 'application/json'

        self.options['username'] = username
        self.options['password'] = password

        self.options['base_path'] = ''

    def request(self, path='', method='GET', payload={}):
        endpoint = self.options.get('endpoint')
        base_path = self.options.get('base_path').lstrip('/')

        path = path.lstrip('/')

        url = f'{endpoint}/{base_path}/{path}' if len(base_path) > 0 else f'{endpoint}/{path}'

        display.v(f'API call path: {url}')
        display.v("API call payload: %s" % payload)
        display.v("Request headers: %s" % self.options.get('headers'))

        try:
            response = open_url(f'{url}',
                                method=method,
                                url_username=self.options['username'],
                                url_password=self.options['password'],
                                data=json.dumps(payload),
                                force_basic_auth=True,
                                validate_certs=self.options.get(
                                    'validate_certs', False),
                                headers=self.options.get('headers', {}),
                                timeout=self.options.get('timeout', 30))
        except HTTPError as e:
            raise AnsibleError(
                "Received HTTP error: %s" % (to_native(e)))
        except URLError as e:
            raise AnsibleError(
                "Failed lookup url: %s" % (to_native(e)))
        except SSLValidationError as e:
            raise AnsibleError(
                "Error validating the server's certificate: %s" % (to_native(e)))
        except ConnectionError as e:
            raise AnsibleError("Error connecting: %s" % (to_native(e)))

        result = json.loads(response.read())

        display.v('API call result: %s' % result)

        return result
