from django.db import models
from django.conf import settings
from django.db.models import Count


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # mark private conversation between two users
    is_direct = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name()

    def display_name(self):
        if self.is_direct:
            users = [m.user.username for m in self.memberships.select_related('user')]
            return "DM: " + " & ".join(users)
        return self.name

    @classmethod
    def get_or_create_direct(cls, user1, user2):
        """Get or create a direct message group between two users."""
        if user1.id == user2.id:
            raise ValueError("Cannot start a direct chat with yourself")
        # normalize users so we search consistently (always user1 < user2 by ID)
        if user1.id > user2.id:
            user1, user2 = user2, user1
        # search for existing group with both users 
        groups = cls.objects.filter(
            is_direct=True,
            memberships__user__in=[user1, user2]
        ).annotate(
            member_count=Count('memberships')
        ).filter(member_count=2)
        if groups.exists():
            return groups.first(), False
        # create new direct group
        group = cls.objects.create(
            name=f"DM:{user1.id}:{user2.id}",
            description="",
            created_by=user1,
            is_direct=True,
        )
        GroupMembership.objects.bulk_create([
            GroupMembership(user=user1, group=group, role='member'),
            GroupMembership(user=user2, group=group, role='member'),
        ])
        return group, True


class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"
