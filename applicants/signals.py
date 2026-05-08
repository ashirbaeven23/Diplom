from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Application


@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, created, **kwargs):
    """Отправка уведомления при изменении статуса заявления"""
    if created:
        # Новое заявление
        subject = 'Заявление подано'
        message = f'Ваше заявление на специальность {instance.specialization.name} успешно подано.'
    elif instance.is_agreement_signed:
        subject = 'Согласие подписано'
        message = f'Вы подписали согласие на зачисление на специальность {instance.specialization.name}.'
    elif instance.status == 'recommended':
        subject = 'Вы рекомендованы к зачислению'
        message = f'Поздравляем! Вы рекомендованы к зачислению на специальность {instance.specialization.name}.'
    elif instance.status == 'accepted':
        subject = 'Вы зачислены!'
        message = f'Поздравляем! Вы зачислены на специальность {instance.specialization.name}.'
    else:
        return
    
    # Отправка email
    user_email = instance.applicant.user.email
    if user_email:
        send_mail(
            subject,
            message,
            'noreply@college.ru',
            [user_email],
            fail_silently=True,
        )