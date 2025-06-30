from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import User


class Voucher(models.Model):
    """Model for redeemable vouchers and gift cards."""
    
    VENDOR_CHOICES = [
        ('zomato', 'Zomato'),
        ('swiggy', 'Swiggy'),
        ('ola', 'Ola'),
        ('uber', 'Uber'),
        ('amazon', 'Amazon'),
        ('flipkart', 'Flipkart'),
        ('paytm', 'Paytm'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('redeemed', 'Redeemed'),
        ('expired', 'Expired'),
        ('disabled', 'Disabled'),
    ]
    
    # Voucher details
    vendor = models.CharField(max_length=20, choices=VENDOR_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Voucher value in currency")
    cost_in_coins = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Voucher code
    code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Usage
    max_uses = models.IntegerField(default=1, help_text="Maximum number of times this voucher can be used")
    current_uses = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.vendor} - {self.title} ({self.value})"
    
    @property
    def is_available(self):
        now = timezone.now()
        if self.status != 'available':
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.current_uses >= self.max_uses:
            return False
        return True
    
    @property
    def is_expired(self):
        if self.valid_until:
            return timezone.now() > self.valid_until
        return False


class VoucherRedemption(models.Model):
    """Model to track voucher redemptions by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voucher_redemptions')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='redemptions')
    redeemed_at = models.DateTimeField(auto_now_add=True)
    coins_spent = models.IntegerField()
    
    class Meta:
        ordering = ['-redeemed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.voucher.title}"


class RewardCategory(models.Model):
    """Model for organizing rewards into categories."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    color = models.CharField(max_length=7, default='#3B82F6')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Reward categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Reward(models.Model):
    """Model for different types of rewards."""
    
    REWARD_TYPE_CHOICES = [
        ('voucher', 'Voucher'),
        ('badge', 'Badge'),
        ('title', 'Title'),
        ('feature', 'Feature'),
        ('other', 'Other'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    category = models.ForeignKey(RewardCategory, on_delete=models.CASCADE, related_name='rewards')
    
    # Cost and availability
    cost_in_coins = models.IntegerField(validators=[MinValueValidator(0)])
    is_available = models.BooleanField(default=True)
    
    # Reward details
    reward_data = models.JSONField(default=dict, help_text="Additional data for the reward")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'cost_in_coins']
    
    def __str__(self):
        return self.name


class UserReward(models.Model):
    """Model to track rewards earned by users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_rewards')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE, related_name='user_rewards')
    earned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'reward']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"


class DailyReward(models.Model):
    """Model for daily login rewards."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_rewards')
    date = models.DateField()
    coins_earned = models.IntegerField(default=0)
    streak_bonus = models.IntegerField(default=0)
    total_coins = models.IntegerField(default=0)
    claimed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} ({self.total_coins} coins)"


class ReferralReward(models.Model):
    """Model for referral rewards."""
    
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referred_by')
    coins_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['referrer', 'referred_user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}" 