import re
import json


class HandlerBase:
    """База функций обработки"""

    def __init__(self, content):
        self.sentences = re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', content)

    def exclude_by_pattern(self, content: str, pattern: str) -> str:
        """Удаляет из контента предложение, содержащее паттерн"""

        for index, sentence in enumerate(self.sentences):
            if re.search(pattern, sentence):
                self.sentences.pop(index)
        result = ' '.join(self.sentences)
        return result

    def replace_in_content(self, content: str, pattern: str, repl: str, is_nested: bool) -> str:
        """Заменяет паттерн в контенте

        Заменяет pattern на repl, при этом возможны 2 случая:
            - repl содержится в предложении с pattern и задается шаблоном regex(is_neted = True);
            - repl это новое значение(is_nested = False).

        """

        for index, sentence in enumerate(self.sentences):
            target = re.search(pattern, sentence)
            if target:
                target = target.group()
                if is_nested:
                    replacement = re.search(repl, sentence).group()
                else:
                    replacement = repl
                self.sentences[index] = re.sub(target, replacement, sentence)
        result = ' '.join(self.sentences)
        return result


class Handler:
    """Обработчик контента"""

    def __init__(self, email: str, content: str, default_handler: str = 'gmail') -> None:
        self.domain = re.search('(?<=@)[^.]*.[^.]*(?=\.)', email).group()
        self._content = content
        self.default_handler = default_handler
        self._handler_base = HandlerBase(content)

    def _normalize_domain(self, domain):
        """Нормализация домена

        Приведение имени домена к виду, позводяющему использовать
        имя домена в качестве имени переменной в Python3.

        """
        return re.sub('-|\.', '_', domain)

    def _handle_gmail(self) -> str:
        """Функция обработки конктертного домена

        Агрегатор правил обработки

        """
        pattern = ' offer '
        self._content = self._handler_base.exclude_by_pattern(self._content, pattern)
        return self._content

    def _handle_yandex(self) -> str:
        pattern = '<img src.*>'
        repl = '(?<=\<img src=").*(?=\")'
        is_nested = True
        result = self._handler_base.replace_in_content(self._content, pattern, repl, is_nested)
        return result

    def _handle_mail(self) -> str:
        pattern = '(?<=\.)gif(?=\")'
        repl = 'png'
        is_nested = False
        result = self._handler_base.replace_in_content(self._content, pattern, repl, is_nested)
        return result

    def _resolve_handler(self):
        """Выбор метода обработки в зависимости от домена

        Имя метода обработки складывается из приставки
        _handle_ и имени домена, соблюдение такой формы
        наименования позволяет расширять количество
        обратываемых доменов.

        """
        normalized_domain = self._normalize_domain(self.domain)
        normalized_default = self._normalize_domain(self.default_handler)
        try:
            result = getattr(self, '_handle_' + normalized_domain)
        except AttributeError:
            result = getattr(self, '_handle_' + normalized_default)
        return result

    def handle(self) -> str:
        handle_by_domen = self._resolve_handler()
        result = handle_by_domen()
        return result


class Email:
    def __init__(self, email: str, content: str) -> None:
        self._email = email
        self._content = content

    def _filter_content(self) -> str:
        handler = Handler(self._email, self._content)
        filtered_content = handler.handle()
        return filtered_content

    def send(self) -> str:
        to_send = {
            'email': self._email,
            'content': self._filter_content()
        }
        result = json.dumps(to_send)
        return result
