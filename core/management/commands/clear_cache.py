"""
Management command to clear all cache.
Usage: python manage.py clear_cache
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear all cache'

    def handle(self, *args, **options):
        self.stdout.write('Clearing cache...')
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cache cleared successfully!'))

