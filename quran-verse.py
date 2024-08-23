import os
import re
from variety.plugins.IQuoteSource import IQuoteSource
from gettext import gettext as _
import logging
import random
from variety.Util import Util
from variety.Util import cache

logger = logging.getLogger("variety")

class QuranVersesSource(IQuoteSource):
    def __init__(self):
        logger.debug("Initializing QuranVersesSource...")
        super().__init__()
        self.verses = []
        self.active = False
        logger.debug("Initialization complete.")

    @classmethod
    def get_info(cls):
        logger.debug("Getting plugin info...")
        return {
            "name": "Quran Verse",
            "description": _("Random Verses From the Quran"),
            "author": "Mohammed Sowaity",
            "version": "0.1"
        }

    def supports_search(self):
        logger.debug("Checking if search is supported...")
        return True

    def activate(self):
        if self.active:
            logger.debug("Plugin already active.")
            return

        logger.debug("Activating plugin...")
        super().activate()
        self.active = True
        logger.debug("Plugin activated.")

    def deactivate(self):
        logger.debug("Deactivating plugin...")
        self.active = False
        self.verses = []
        logger.debug("Plugin deactivated.")

    def needs_internet(self):
        logger.debug("Checking if internet is needed...")
        return True

    def get_random(self):
        logger.debug("Getting random verse...")
        verse = self._get_verse()
        mapped_verse = self._map_verse(verse)
        logger.debug(f"Random verse retrieved: {mapped_verse}")
        return mapped_verse

    def _map_verse(self, verse):
        logger.debug("Mapping verse data...")
        mapped = {
            "quote": verse.get('text', "Can't load verse..."),
            "author": verse.get("surah", {}).get("name", "Unknown Surah"),
            "sourceName": 'QuranAPI',
            "link": None
        }
        logger.debug(f"Mapped verse: {mapped}")
        return [mapped]

    def _get_verse(self):
        logger.debug("Retrieving verse from cache or API...")
        if self.verses:
            verse = self.verses.pop(0)
            logger.debug(f"Returning cached verse: {verse}")
            return verse

        if not Util.internet_enabled:
            logger.warning("Internet is not enabled.")
            return {}

        try:
            verse = self._fetch_verse(random.randint(1, 6236))
            logger.debug(f"Verse fetched from API: {verse}")
        except Exception as err:
            logger.warning(f"Failed to fetch verse: {err}")
            return {}

        if not isinstance(verse, dict) or 'text' not in verse:
            logger.warning("Invalid response. No verse found.")
            return {}

        return verse

    @cache(ttl_seconds=30, debug=True)
    def _fetch_verse(self, verse_number):
        logger.debug(f"Fetching verse {verse_number} from API...")
        URL = f"https://api.alquran.cloud/v1/ayah/{verse_number}"
        response = Util.fetch_json(URL)
        
        if response.get('code') == 200 and response.get('status') == "OK":
            logger.debug("Successfully fetched verse from API.")
            return response['data']
        else:
            logger.warning(f"Failed to fetch verse from API. Response: {response}")
            return {}


