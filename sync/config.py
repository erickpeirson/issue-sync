from os import environ

LOGLEVEL = int(environ.get('LOGLEVEL', '40'))

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI',
                                      'sqlite:///:memory:')

JIRA_ENDPOINT = environ.get('JIRA_ENDPOINT')
JIRA_USERNAME = environ.get('JIRA_USERNAME')
JIRA_TOKEN = environ.get('JIRA_TOKEN')
JIRA_COMPONENTS = {
    'arxiv-auth': '16109',    # Authentication
    'arxiv-references': '15800',    # References
    'arxiv-fulltext': '16001',      # Plain text extraction
    'arxiv-browse': '15700',        # Browse,
    'arxiv-search': '16000',        # Search
    'arxiv-submission-core': '16110',    # Agent
    'arxiv-base': '16028',          # Base
    'arxiv-sync': '16046',
    'arxiv-docs': '16038',
    'arxiv-submission-ui': '15801',
    'arxiv-readability': '16048', # Labs
    'arxiv-rss': '16027',
    'arxiv-compiler': '16047',
    'arxiv-api-gateway': '16045',
    'arxiv-canonical': '16100',
    'arxiv-marxdown': '16038',
    'arxiv-vault': '16112',
    'arxiv-external-links': '16105',
    'arxiv-authors': '16014',
}

WEBHOOK_TOKEN = environ.get('WEBHOOK_TOKEN')

NAMESPACE = environ.get('NAMESPACE')
"""Namespace in which this service is deployed; to qualify keys for secrets."""

NS_AFFIX = '' if NAMESPACE == 'production' else f'-{NAMESPACE}'

KUBE_TOKEN = environ.get('KUBE_TOKEN', 'fookubetoken')
"""Service account token for authenticating with Vault. May be a file path."""

VAULT_ENABLED = bool(int(environ.get('VAULT_ENABLED', '0')))
"""Enable/disable secret retrieval from Vault."""

VAULT_HOST = environ.get('VAULT_HOST', 'foovaulthost')
"""Vault hostname/address."""

VAULT_PORT = environ.get('VAULT_PORT', '1234')
"""Vault API port."""

VAULT_ROLE = environ.get('VAULT_ROLE', 'issue-sync')
"""Vault role linked to this application's service account."""

VAULT_CERT = environ.get('VAULT_CERT')
"""Path to CA certificate for TLS verification when talking to Vault."""

VAULT_SCHEME = environ.get('VAULT_SCHEME', 'https')
"""Default is ``https``."""

VAULT_REQUESTS = [
    {'type': 'generic',
     'name': 'WEBHOOK_TOKEN',
     'mount_point': f'secret{NS_AFFIX}/',
     'path': 'github',
     'key': 'webhook-token',
     'minimum_ttl': 60},
    {'type': 'generic',
     'name': 'JIRA_USERNAME',
     'mount_point': f'secret{NS_AFFIX}/',
     'path': 'jira',
     'key': 'username',
     'minimum_ttl': 60},
    {'type': 'generic',
     'name': 'JIRA_TOKEN',
     'mount_point': f'secret{NS_AFFIX}/',
     'path': 'jira',
     'key': 'token',
     'minimum_ttl': 60},
    {'type': 'database',
     'engine': environ.get('SQLALCHEMY_DATABASE_ENGINE', 'mysql+mysqldb'),
     'host': environ.get('SQLALCHEMY_DATABASE_HOST', 'localhost'),
     'database': environ.get('SQLALCHEMY_DATABASE', 'sync'),
     'params': 'charset=utf8mb4',
     'port': '3306',
     'name': 'SQLALCHEMY_DATABASE_URI',
     'mount_point': f'database{NS_AFFIX}/',
     'role': 'issue-sync-write'}
]
"""Requests for Vault secrets."""