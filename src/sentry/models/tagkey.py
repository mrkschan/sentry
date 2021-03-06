"""
sentry.models.tagkey
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2014 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from django.core.urlresolvers import reverse
from django.db import models

from sentry.constants import MAX_TAG_KEY_LENGTH, TAG_LABELS
from sentry.db.models import Model, BoundedPositiveIntegerField, sane_repr
from sentry.manager import TagKeyManager
from sentry.utils.http import absolute_uri


class TagKey(Model):
    """
    Stores references to available filters keys.
    """
    DEFAULT_URL_NAME = 'sentry-explore-tag'
    URL_NAMES = {
        'sentry:user': 'sentry-users',
        'sentry:filename': 'sentry-explore-code',
        'sentry:function': 'sentry-explore-code-by-function',
    }

    project = models.ForeignKey('sentry.Project')
    key = models.CharField(max_length=MAX_TAG_KEY_LENGTH)
    values_seen = BoundedPositiveIntegerField(default=0)
    label = models.CharField(max_length=64, null=True)

    objects = TagKeyManager()

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_filterkey'
        unique_together = (('project', 'key'),)

    __repr__ = sane_repr('project_id', 'key')

    def get_label(self):
        return self.label \
            or TAG_LABELS.get(self.key) \
            or self.key.replace('_', ' ').title()

    def get_absolute_url(self):
        # HACK(dcramer): quick and dirty way to support code/users
        try:
            url_name = self.URL_NAMES[self.key]
        except KeyError:
            url_name = self.DEFAULT_URL_NAME
            return absolute_uri(reverse(url_name, args=[
                self.project.team.slug, self.project.slug, self.key]))

        return absolute_uri(reverse(url_name, args=[
            self.project.team.slug, self.project.slug]))
