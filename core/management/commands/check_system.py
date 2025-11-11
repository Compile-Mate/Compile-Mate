"""
Management command to check system health and dependencies.
Usage: python manage.py check_system
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
import sys


class Command(BaseCommand):
    help = 'Check system health and dependencies'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Running system health checks...'))
        self.stdout.write('')

        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.stdout.write(f'Python Version: {python_version}')
        if sys.version_info >= (3, 9):
            self.stdout.write(self.style.SUCCESS('✓ Python version OK'))
        else:
            self.stdout.write(self.style.ERROR('✗ Python version too old (need 3.9+)'))

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))

        # Check cache connection
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                self.stdout.write(self.style.SUCCESS('✓ Cache connection OK'))
            else:
                self.stdout.write(self.style.ERROR('✗ Cache not working properly'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Cache connection failed: {e}'))

        # Check Redis connection
        try:
            import redis
            from django.conf import settings
            redis_url = settings.CACHES.get('default', {}).get('LOCATION', '')
            if redis_url:
                client = redis.from_url(redis_url)
                client.ping()
                self.stdout.write(self.style.SUCCESS('✓ Redis connection OK'))
            else:
                self.stdout.write(self.style.WARNING('⚠ Redis not configured'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Redis connection failed: {e}'))

        # Check Docker
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self.stdout.write(self.style.SUCCESS('✓ Docker connection OK'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Docker connection failed: {e}'))

        # Check Celery
        try:
            from celery import current_app
            inspector = current_app.control.inspect()
            if inspector.ping():
                self.stdout.write(self.style.SUCCESS('✓ Celery workers OK'))
            else:
                self.stdout.write(self.style.WARNING('⚠ No Celery workers running'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠ Celery check failed: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('System health check complete!'))

