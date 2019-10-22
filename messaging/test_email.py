import pytest
from messaging.email import Email


class Case:
    def __init__(self, email, content, expected):
        self.email = email
        self.content = content
        self.expected = expected


TEST_CASES = [
    Case(
            email = 'test1@gmail.com',
            content = 'Hello gmail! I have an offer for you.',
            expected = '{"email": "test1@gmail.com", "content": "Hello gmail!"}'
        ),
    Case(
            email = 'test2@yandex.ru',
            content = 'Hello yandex! I have an pic <img src="https://spam.org/pic1.png" /> for you.',
            expected = '{"email": "test2@yandex.ru", "content": "Hello yandex! I have an pic https://spam.org/pic1.png for you."}'
        ),
    Case(
            email = 'test3@mail.ru',
            content = 'Hello mail! I have an pic <img src="https://spam.org/pic1.gif" /> for you.',
            expected = '{"email": "test3@mail.ru", "content": "Hello mail! I have an pic <img src=\\"https://spam.org/pic1.png\\" /> for you."}'
        ),
    Case(
            email = 'test4@sailplay.ru',
            content = 'Hello another mail client! I have an offer for you.',
            expected = '{"email": "test4@sailplay.ru", "content": "Hello another mail client!"}'
        ),
]


@pytest.mark.parametrize("test_case", TEST_CASES, ids=lambda c: str(c))
def test_email(test_case):
    sended = Email(test_case.email, test_case.content).send()
    assert sended == test_case.expected
