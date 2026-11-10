import json
import logging
from urllib.parse import quote
from urllib.request import urlopen

logger = logging.getLogger(__name__)


def random_booru(type: str):
    url_base = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&tags={quote(type)}%20sort:random&limit=1&json=1&pid=1"
    response = urlopen(url_base)
    json_data = json.loads(response.read())
    file_url = json_data[0]["file_url"]
    source = json_data[0]["source"]
    id = json_data[0]["id"]
    return file_url, source, id

    # we go back to comments
    # x |   |
    #   |   |
    #   |   |
