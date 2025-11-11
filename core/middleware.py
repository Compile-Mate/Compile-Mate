"""
Custom middleware for CompileMate platform.
"""

import time
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor request/response performance."""
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (> 1 second)
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration:.2f}s",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    }
                )
            
            # Add performance header for debugging
            if settings.DEBUG:
                response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware.
    Limits requests per user/IP to prevent abuse.
    """
    
    def process_request(self, request):
        # Skip rate limiting for admin and static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        # Get identifier (user ID or IP address)
        if request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            identifier = f"ip:{self.get_client_ip(request)}"
        
        # Rate limit: 100 requests per minute
        cache_key = f"rate_limit:{identifier}"
        requests_count = cache.get(cache_key, 0)
        
        if requests_count > 100:
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': 60
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, requests_count + 1, 60)
        
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses."""
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (adjust as needed)
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https:; "
                "connect-src 'self';"
            )
        
        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to enable maintenance mode.
    When enabled, all requests return a maintenance page.
    """
    
    def process_request(self, request):
        # Skip for admin
        if request.path.startswith('/admin/'):
            return None
        
        # Check if maintenance mode is enabled
        from core.models import SiteSettings
        settings_obj = SiteSettings.get_settings()
        
        if settings_obj.maintenance_mode:
            # Allow staff users
            if request.user.is_authenticated and request.user.is_staff:
                return None
            
            # Return maintenance page for everyone else
            from django.shortcuts import render
            return render(request, 'maintenance.html', {
                'message': settings_obj.maintenance_message
            }, status=503)
        
        return None


class APIRequestLoggingMiddleware(MiddlewareMixin):
    """Log all API requests for monitoring and debugging."""
    
    def process_request(self, request):
        if request.path.startswith('/api/'):
            logger.info(
                f"API Request: {request.method} {request.path}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    'ip': self.get_client_ip(request),
                }
            )
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

