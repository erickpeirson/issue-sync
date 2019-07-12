

from jira import JIRA

from ..domain import JiraEvent


class JiraService:
    def __init__(self, endpoint: str, username: str, token: str) -> None:
        self._endpoint = endpoint
        self._username = username
        self._token = token
        self._jira = self._new_connection(self._endpoint, self._username,
                                          self._token)

    @staticmethod
    def _new_connection(endpoint: str, username: str, token: str) -> JIRA:
        return JIRA(endpoint, basic_auth=(username, token))

    # def create_ticket(self, ticket_data: JiraTicketData) -> int:
    #     ...

    # def update_ticket_body(self, key: str, body: str) -> None:
    #     ...

    # def update_ticket_status(self, key: str, status: str) -> None:
    #     ...





def propagate(jira_event: JiraEvent) -> JiraEvent:
    ...