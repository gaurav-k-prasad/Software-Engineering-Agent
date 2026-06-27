from pprint import pprint
import re
from collections import defaultdict


class Tokenizer:
    def tokenize(self, text: str) -> dict[str, int]:
        d: dict[str, int] = defaultdict(int)

        text = text.strip()
        text = re.sub(r"[^\w.]", " ", text)
        splitted: list[str] = re.split(r"[\s.]+", text)
        for word in splitted:
            d[self.preprocess_token(word.lower())] += 1
            stripped_underscore = word.strip("_")

            if len(stripped_underscore) != len(word):
                d[self.preprocess_token(stripped_underscore.lower())] += 1

            stripped_underscore = re.sub(
                r"([A-Z]+)([A-Z][a-z]+)", r"\1_\2", stripped_underscore
            )
            stripped_underscore = re.sub(
                r"([a-z\d])([A-Z])", r"\1_\2", stripped_underscore
            )

            snake_case_components = self.split_snake_case(stripped_underscore)

            if (
                len(snake_case_components) > 1
            ):  # ensure that there was more than one split otherwise the word would be the same
                for sc_component in snake_case_components:
                    d[self.preprocess_token(sc_component.lower())] += 1

            snake_camal_pascal_components = list(
                map(self.split_pascal_camal_case, snake_case_components)
            )

            for scp_component in snake_camal_pascal_components:
                if len(scp_component) > 1:  # ensure that splitting actually happen
                    for component in scp_component:
                        d[self.preprocess_token(component.lower())] += 1

        return {k: v for k, v in d.items() if len(k) > 1}

    def preprocess_token(self, token: str) -> str:
        # if token.endswith("s") and len(token) > 3:
        #     return token[:-1]
        return token

    def split_on_dot(self, text: str) -> list[str]:
        return text.split(".")

    def split_snake_case(self, text: str) -> list[str]:
        return text.split("_")

    def split_pascal_camal_case(self, text: str) -> list[str]:
        res = re.split(r"(?=[A-Z])", text)
        return [item for item in res if len(item) > 0]


if __name__ == "__main__":
    t = Tokenizer()
    pprint(t.tokenize("UserControllersClass.login_user"))
    pprint(t.tokenize("XMLHttpResponse"))
    pprint(t.tokenize("OAuthJWTValidator"))
    pprint(t.tokenize("HTTPRequest"))
    pprint(t.tokenize("UserControllersClass"))
    pprint(t.tokenize("getJSONResponse"))
    pprint(t.tokenize("JWTToken"))
    pprint(t.tokenize("JWTManager.generate_access_token"))
