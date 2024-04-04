from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from users.models import Department


@receiver(m2m_changed, sender=Department.head.through)
def update_head_department(sender, instance, action, reverse, model, pk_set, **kwargs):
    print(instance.head)
    if action == 'post_add':
        if instance.head.exists():
            head_users = instance.head.all()
            for user in head_users:
                print(user)
                if user.department != instance:
                    user.department = instance
                    user.save()