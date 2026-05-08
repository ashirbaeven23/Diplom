from django.db import models
from django.contrib.auth.models import User


class Specialization(models.Model):
    """Специальность колледжа"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Код специальности")
    name = models.CharField(max_length=255, verbose_name="Название")
    faculty = models.CharField(max_length=100, verbose_name="Факультет")
    budget_places = models.PositiveSmallIntegerField(verbose_name="Бюджетные места")
    paid_places = models.PositiveSmallIntegerField(default=0, verbose_name="Платные места")
    min_score = models.PositiveSmallIntegerField(default=100, verbose_name="Мин. проходной балл")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class AdmissionCampaign(models.Model):
    """Приемная кампания"""
    year = models.IntegerField(unique=True, verbose_name="Год")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    is_active = models.BooleanField(default=False, verbose_name="Активна")

    class Meta:
        verbose_name = "Приемная кампания"
        verbose_name_plural = "Приемные кампании"
        ordering = ['-year']

    def __str__(self):
        return f"Приемная кампания {self.year}"


class Applicant(models.Model):
    """Абитуриент"""
    SEX_CHOICES = [('M', 'Мужской'), ('F', 'Женский')]
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'Подано'),
        ('under_review', 'На рассмотрении'),
        ('accepted', 'Зачислен'),
        ('rejected', 'Отказ'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='applicant_profile',
        verbose_name="Пользователь"
    )
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    birth_date = models.DateField(verbose_name="Дата рождения")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Пол")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    snils = models.CharField(max_length=14, blank=True, verbose_name="СНИЛС")
    passport_series = models.CharField(max_length=4, blank=True, verbose_name="Серия паспорта")
    passport_number = models.CharField(max_length=6, blank=True, verbose_name="Номер паспорта")
    address = models.TextField(blank=True, verbose_name="Адрес")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"
        ordering = ['user__last_name', 'user__first_name']

    @property
    def full_name(self):
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"

    def __str__(self):
        return self.full_name


class Application(models.Model):
    """Заявление о приеме"""
    PRIORITY_CHOICES = [
        (1, 'Первый приоритет'),
        (2, 'Второй приоритет'),
        (3, 'Третий приоритет'),
    ]
    APP_STATUS = [
        ('draft', 'Черновик'),
        ('submitted', 'Подано'),
        ('agreement_signed', 'Согласие подписано'),
        ('recommended', 'Рекомендован'),
        ('accepted', 'Зачислен'),
    ]

    applicant = models.ForeignKey(
        Applicant, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name="Абитуриент"
    )
    campaign = models.ForeignKey(
        AdmissionCampaign, 
        on_delete=models.CASCADE,
        verbose_name="Приемная кампания"
    )
    specialization = models.ForeignKey(
        Specialization, 
        on_delete=models.CASCADE,
        verbose_name="Специальность"
    )
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES,
        verbose_name="Приоритет"
    )
    status = models.CharField(
        max_length=20, 
        choices=APP_STATUS, 
        default='draft',
        verbose_name="Статус заявления"
    )
    is_agreement_signed = models.BooleanField(
        default=False,
        verbose_name="Согласие на зачисление"
    )
    agreement_date = models.DateTimeField(null=True, blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заявление"
        verbose_name_plural = "Заявления"
        unique_together = [
            ['applicant', 'campaign', 'priority'],
            ['applicant', 'campaign', 'specialization'],
        ]
        ordering = ['-submission_date']

    def __str__(self):
        return f"{self.applicant} → {self.specialization.code} (пр.{self.priority})"


class ExamResult(models.Model):
    """Результат экзамена"""
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='exam_results',
        verbose_name="Заявление"
    )
    subject = models.CharField(max_length=100, verbose_name="Предмет")
    score = models.PositiveSmallIntegerField(verbose_name="Балл")
    is_ege = models.BooleanField(default=True, verbose_name="ЕГЭ")
    exam_date = models.DateField(null=True, blank=True, verbose_name="Дата экзамена")
    document_number = models.CharField(
        max_length=50, blank=True, 
        verbose_name="Номер документа"
    )

    class Meta:
        verbose_name = "Результат экзамена"
        verbose_name_plural = "Результаты экзаменов"
        unique_together = ['application', 'subject']

    def __str__(self):
        return f"{self.subject}: {self.score}"


class Attachment(models.Model):
    """Прикрепленный документ"""
    DOC_TYPES = [
        ('passport', 'Паспорт'),
        ('diploma', 'Аттестат'),
        ('photo', 'Фотография'),
        ('snils', 'СНИЛС'),
        ('other', 'Прочее'),
    ]

    applicant = models.ForeignKey(
        Applicant, 
        on_delete=models.CASCADE, 
        related_name='attachments',
        verbose_name="Абитуриент"
    )
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name="Файл")
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, verbose_name="Тип документа")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False, verbose_name="Проверен")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.applicant}"


class EnrollmentOrder(models.Model):
    """Приказ о зачислении"""
    campaign = models.ForeignKey(
        AdmissionCampaign, 
        on_delete=models.CASCADE,
        verbose_name="Приемная кампания"
    )
    order_number = models.CharField(max_length=50, verbose_name="Номер приказа")
    order_date = models.DateField(verbose_name="Дата приказа")
    file = models.FileField(upload_to='orders/', null=True, blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Кто создал"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    applications = models.ManyToManyField(
        Application, 
        related_name='enrollment_orders',
        verbose_name="Заявления"
    )

    class Meta:
        verbose_name = "Приказ о зачислении"
        verbose_name_plural = "Приказы о зачислении"

    def __str__(self):
        return f"Приказ №{self.order_number} от {self.order_date}"