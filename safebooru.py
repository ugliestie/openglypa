## https://github.com/shabeille/yuribot/ thanks!!!!!!! kisses yurifully

import json
from random import choice
from string import Template
from urllib.parse import urljoin

import aiohttp

website_url: str = "https://safebooru.org/"
prefix: Template = Template(
    "index.php?page=dapi&s=post&q=index&json=1&limit=${limit}&tags=${tags}"
)


class SafebooruBrowser:
    def __init__(
        self,
        session,
        cache_size=1000,
        default_tags=None,
        fetch_from_latest: bool = False,
        rare_query_cache_size=100,
    ):

        self._session: aiohttp.ClientSession = session

        if default_tags is not None and type(default_tags) not in (tuple, list):
            raise TypeError("Default tags must be passed in as a tuple or list")

        self.default_tags = [] if default_tags is None else list(default_tags)

        if not fetch_from_latest:
            self.default_tags.append("sort:random")

        self.cache_size = cache_size
        self._cached_posts = []

        self.rare_cache_size = rare_query_cache_size
        self._rare_cache = {}

    async def _get_json_response(self, url):
        async with self._session.get(url) as resp:
            data = await resp.json()
            return data or []

    async def update_cache(self, init_rare_cache=True):
        url = build_url(self.default_tags, self.cache_size)
        self._cached_posts = await self._get_json_response(url)

        if init_rare_cache:
            self._rare_cache = {}

    async def get_random(self, *args):
        if len(args) == 0:
            return choice(self._cached_posts)

        tagged_posts = [
            post
            for post in self._cached_posts
            if all(tag in post["tags"].split() for tag in args)
        ]

        if len(tagged_posts) >= 10:
            return choice(tagged_posts)
        elif self.rare_cache_size == 0:
            raise IndexError

        key = tuple(sorted(args))

        if key not in self._rare_cache:
            url = build_url(self.default_tags + list(args), self.rare_cache_size)
            self._rare_cache[key] = await self._get_json_response(url)

        return choice(self._rare_cache[key])

    async def get_cache_size(self):
        return len(self._cached_posts)

    async def autocomplete(self, query: str):
        url = urljoin(
            website_url,
            f"autocomplete.php?q={(query.split(',')[-1]).strip(' ').lstrip('-')}",
        )

        async with self._session.get(url) as resp:
            response_stream = resp.content
            data = await response_stream.read()
            json_data = json.loads(data.decode())

            return json_data or []


def build_url(tags: list, count: int) -> str:
    return urljoin(website_url, prefix.substitute(limit=count, tags="+".join(tags)))
