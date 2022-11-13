from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Group(models.Model):
    group_name = models.CharField(max_length=20)
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    group_info = models.CharField(max_length=300, blank=True, null=True)
    members = models.ManyToManyField(User, related_name="all_groups")

    def __str__(self):
        return self.group_name

    def last_messages(grp_name):
        group = Group.objects.get(group_name=grp_name)
        return list(group_messages.objects.filter(parent_group=group).order_by("date_posted"))


class group_messages(models.Model):
    parent_group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="messages")
    parent_user = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default='1')
    message_text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.localtime().now)

    def save(self, *args, **kwargs):
        print(self.parent_group.members)

        for member in self.parent_group.members.all():
            Notification.objects.create(
                user_to=member, is_group=True, group=self.parent_group, 
                notification_text=f"you have new message from {self.parent_user.username} in group {self.parent_group.group_name }")
        super().save(*args, **kwargs)

    def __str__(self):
        tup = tuple([self.parent_user, self.parent_group, self.message_text])
        return str(tup)


class One_to_one_room(models.Model):
    group_name = models.CharField(max_length=20, default="mygroup")
    members = models.ManyToManyField(User, related_name="chats")

    def __str__(self):
        return self.group_name


class personal_messages(models.Model):
    message_to = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default='1', related_name="tomessages")
    message_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default='1', related_name="bymessages")
    message_text = models.TextField()
    chat_room = models.ForeignKey(
        One_to_one_room, on_delete=models. CASCADE)
    date_posted = models.DateTimeField(default=timezone.localtime().now)

    def __str__(self):
        tup = (self.message_by, self.message_to, self.message_text)
        return str(tup)

    def save(self, *args, **kwargs):
        Notification.objects.create(
            user_to=self.message_to, is_group=False, notify_by=self.message_by, notification_text=f"you have new message from {self.message_by.username}")
        super().save(*args, **kwargs)

    def last_messages(grp_name):
        group = One_to_one_room.objects.get(group_name=grp_name)
        return list(personal_messages.objects.filter(chat_room=group).order_by("date_posted"))


class Notification(models.Model):
    notification_text = models.CharField(max_length=100)
    is_seen = models.BooleanField(default=False, null=True, blank=True)
    user_to = models.ForeignKey(User,
                                on_delete=models.CASCADE,default='1', related_name="notification_to")
    date_posted = models.DateTimeField(default=timezone.localtime().now)
    is_group = models.BooleanField(default=False)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, null=True, blank=True, default='1', related_name="messagess")
    notify_by = models.ForeignKey(User, null=True, blank=True, default='1',
                                  on_delete=models.CASCADE, related_name="notification_by")

    def unseen_notification(user_to):

        return Notification.objects.filter(is_seen=False,user_to=user_to).count()

    def last_notifications(userr):
        return Notification.objects.filter(user_to=userr).order_by("date_posted")

    def latest_notifications(userr, date):
        return Notification.objects.filter(user_to=userr, date_posted__gt=date).order_by("date_posted")

    def __str__(self):
        tup = tuple([self.notification_text, self.is_seen, self.user_to])
        return str(tup)
