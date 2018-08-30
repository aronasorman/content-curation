#!/usr/bin/env python
#
# Utilities related to caching expensive endpoints.
#

from django.core.cache import cache

from contentcuration.models import Channel

class ChannelCacher(object):
    """
    A proxy to the Channel object that caches return values for
    expensive queries.
    """

    PUBLIC_CHANNEL_CACHE_KEY = "public_channel_cache"
    PUBLIC_CHANNEL_CACHE_TIMEOUT = 60 # seconds

    @classmethod
    def get_public_channels(cls):
        return cache.get_or_set(
            cls.PUBLIC_CHANNEL_CACHE_KEY,
            cls.regenerate_public_channel_cache,
            cls.PUBLIC_CHANNEL_CACHE_TIMEOUT
        )

    @classmethod
    def regenerate_public_channel_cache(cls):
        """
        Invalidate and recalculate the list of public channels and their attributes.
        Returns the new list of public channels.

        """
        channels = list(Channel.get_public_channels())
        cache.set(cls.PUBLIC_CHANNEL_CACHE_KEY, channels)

        return channels

    @classmethod
    def for_channel(cls, channel):
        """
        Return a proxy for the cache specific to a channel.
        """

        return ChannelSpecificCacher(channel)


class ChannelSpecificCacher(object):

    CHANNEL_TOKEN_CACHE_KEY_PREFIX = "channel_token"
    CHANNEL_TOKEN_CACHE_TIMEOUT = 60 # seconds

    def __init__(self, channel):
        self.channel = channel
        # cache key prefix is the first 5 characters of the channel id
        self.key = channel.id[:5]

    def get_human_token(self):
        key = "{prefix}_human_token_{key}".format(
            prefix=self.CHANNEL_TOKEN_CACHE_KEY_PREFIX,
            key=self.key
        )
        return cache.get_or_set(
            key,
            self.channel.get_human_token,
            self.CHANNEL_TOKEN_CACHE_TIMEOUT,
        )

    def get_channel_id_token(self):
        key = "{prefix}_channel_id_token_{key}".format(
            prefix=self.CHANNEL_TOKEN_CACHE_KEY_PREFIX,
            key=self.key
        )
        return cache.get_or_set(
            key,
            self.channel.get_channel_id_token,
            self.CHANNEL_TOKEN_CACHE_TIMEOUT,
        )