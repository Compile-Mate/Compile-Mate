from django.contrib import admin
from .models import (
    Voucher, VoucherRedemption, RewardCategory, Reward, 
    UserReward, DailyReward, ReferralReward
)


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'title', 'value', 'cost_in_coins', 'status', 'current_uses', 'is_available')
    list_filter = ('vendor', 'status', 'valid_from', 'valid_until')
    search_fields = ('title', 'description', 'code')
    readonly_fields = ('current_uses', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Voucher Details', {
            'fields': ('vendor', 'title', 'description', 'value', 'cost_in_coins')
        }),
        ('Code & Status', {
            'fields': ('code', 'status', 'current_uses', 'max_uses')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VoucherRedemption)
class VoucherRedemptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'voucher', 'coins_spent', 'redeemed_at')
    list_filter = ('redeemed_at', 'voucher__vendor')
    search_fields = ('user__username', 'voucher__title')
    readonly_fields = ('redeemed_at',)


@admin.register(RewardCategory)
class RewardCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'rewards_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    
    def rewards_count(self, obj):
        return obj.rewards.count()
    rewards_count.short_description = 'Rewards'


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('name', 'reward_type', 'category', 'cost_in_coins', 'is_available')
    list_filter = ('reward_type', 'category', 'is_available')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'reward_type', 'category')
        }),
        ('Cost & Availability', {
            'fields': ('cost_in_coins', 'is_available')
        }),
        ('Reward Data', {
            'fields': ('reward_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'earned_at', 'is_active')
    list_filter = ('is_active', 'earned_at', 'reward__reward_type')
    search_fields = ('user__username', 'reward__name')
    readonly_fields = ('earned_at',)


@admin.register(DailyReward)
class DailyRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'coins_earned', 'streak_bonus', 'total_coins', 'claimed_at')
    list_filter = ('date', 'claimed_at')
    search_fields = ('user__username',)
    readonly_fields = ('claimed_at',)


@admin.register(ReferralReward)
class ReferralRewardAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'coins_earned', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('referrer__username', 'referred_user__username')
    readonly_fields = ('created_at',) 