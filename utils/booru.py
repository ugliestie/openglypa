import json
import logging
import random
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

logger = logging.getLogger(__name__)

def random_booru(type: str):
    url_base = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&tags={quote(type)}%20sort:random&limit=1&json=1&pid=1"
    try:
        response = urlopen(url_base)
        json_data = json.loads(response.read())
        return json_data[0]['file_url'], json_data[0]['source']
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")
        return

        # we go back to comments
        # x |   |
        #   |   |
        #   |   |   