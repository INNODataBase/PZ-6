from django.db import models
from django.conf import settings 
from django.contrib import admin
from django.core import validators 
from django.core.exceptions import ValidationError

def validate_even(val):
  if val % 2 != 0:
    raise ValidationError('Число %(value)s нечетное', code='odd',
                          params={'value': val})

class MinMaxValueValidator:
   def __init__(self, min_value, max_value):
      self.min_value = min_value
      self.max_value = max_value
   def __call__(self, val):
      if val < self.min_value or val > self.max_value:
         raise ValidationError('Введенное число должно ' + \
                               'находиться в диапазоне от %(min)s до %(max)s',
                               code='out_of_range',
                               params={'min': self.min_value, 'max': self.max_value})
   def get_absolute_url(self):
      return "/bboard/%s/" % self.pk

class AdvUser(models.Model):
   is_activated = models.BooleanField(default=True)
   user = models.OneToOneField(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE) 
   def get_absolute_url(self):
     return "/bboard/%s/" % self.pk

class Spare(models.Model):
   name = models.CharField(max_length=30)
   def get_absolute_url(self):
     return "/bboard/%s/" % self.pk

class Machine(models.Model):
   name = models.CharField(max_length=30)
   spares = models.ManyToManyField(Spare) 
   def get_absolute_url(self):
     return "/bboard/%s/" % self.pk

class Bb(models.Model):
    title = models.CharField(max_length=50, verbose_name='Товар')
    content = models.TextField(verbose_name='Описание')
    price = models.FloatField(verbose_name='Цена')
    added = models.DateTimeField()
    published = models.DateTimeField() 
    rubric = models.ForeignKey('Rubric')
    @property
    @admin.display(description='Название и цена')
    def title_and_price(self):
       if self.price:
          return '%s (%.2f)' % (self.title, self.price)
       else:
          return self.title     
    title_and_price.short_description = 'Название и цена'
    title = models.CharField(max_length=50, verbose_name='Товар',
                             validators=[validators.RegexValidator(regex='^.{4,}$')],
                             error_messages={'invalid': 'Неправильное название товара'})
    def get_absolute_url(self):
     return "/bboard/%s/" % self.pk
    def clean(self):
       errors = {}
       if self.title = 'Прошлогодний снег':
          errors['content'] = ValidationError('Такой товар не продается')
       if self.price < 0:
             errors['price'] = ValidationError('Укажите ' + \
                                               'неотрицательное значение цены')
             if errors:
                raise ValidationError(errors) 
    
    class Kinds(models.TextChoices):
       BUY = 'b', 'Куплю'
       SELL = 's', 'Продам'
       EXCHANGE = 'c', 'Обменяю'
       RENT = 'r'
       __empty__ = 'Выберите тип публикуемого объявления'
    
    kind = models.CharField(max_length=1, choices=Kinds.choices,
                           default=Kinds.SELL)
    def get_absolute_url(self):
     return "/bboard/%s/" % self.pk
    
    rubric = models.ForeignKey(
        'Rubric', 
        null=True, 
        on_delete=models.PROTECT, 
        verbose_name='Рубрика'
    )
    
    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-published', 'title']
        get_latest_by = ['edited', 'published']
        order_with_respect_to = 'rubric' 
        unique_together = (
           ('title', 'published'),
           ('title', 'price', 'rubric'),
        ) 
        indexes = [models.Index(fields=['-published', 'title']),
                   models.Index(fields=['title', 'price', 'rubric'],
                                name='%(app_label)s_%(class)s_additional'),
                  ]
        constraints = (models.UniqueConstraint('title', 'price',
                                               name='bbs_title_price_constraint',
                                               condition=models.Q(price__gte=100000)),
                      ) 
        managed = False 
        def get_absolute_url(self):
           return "/bboard/%s/" % self.pk

    
    def __str__(self):
        return self.title

class Rubric(models.Model):
  def __str__(self):
    return self.name
  name = models.CharField(max_length=20, db_index=True,
                          verbose_name='Название')
  def get_absolute_url(self):
     return "/bboard/%s/" % self.pk
  def save(self, *args, **kwargs): 
     # Выполняем какие-либо действия перед сохранением
     super().save(*args, **kwargs) # Сохраняем запись, вызвав
     # унаследованный метод
     if self.is_model_correct():
        super().save(*args, **kwargs)# Выполняем какие-либо действия после сохран
  def delete(self, *args, **kwargs): 
     super().delete(*args, **kwargs) 
     if self.need_to_delete(): 
        super().delete(*args, **kwargs) 

  class Meta:
    verbose_name_plural = 'Рубрики'
    verbose_name = 'Рубрика'
    ordering = ['name'] 

import uuid
from django.db import models
class Bb(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                        editable=False) 

# 1. DecimalField для точного хранения цен
price_exact = models.DecimalField(
  max_digits=10, 
  decimal_places=2,
  verbose_name='Точная цена',
  null=True,
  blank=True
  )
    
# 2. PositiveIntegerField для количества товара
quantity = models.PositiveIntegerField(
  default=1,
  verbose_name='Количество'
)
    
# 3. DateField для срока годности/акции
expiration_date = models.DateField(
  verbose_name='Срок годности/акции',
  null=True,
  blank=True
)
    
# 4. BooleanField для отметки "в наличии"
in_stock = models.BooleanField(
  default=True,
  verbose_name='В наличии'
)
    
# 5. EmailField для контактов продавца
seller_email = models.EmailField(
  verbose_name='Email продавца',
  max_length=254,
  null=True,
  blank=True
)
    
# 6. URLField для ссылки на страницу товара
product_url = models.URLField(
  verbose_name='Ссылка на товар',
  max_length=200,
  null=True,
  blank=True
)
    
# 7. JSONField для хранения дополнительных характеристик
specifications = models.JSONField(
  verbose_name='Характеристики',
  null=True,
  blank=True,
  default=dict
)
    
  # 8. PositiveSmallIntegerField для категории (1-5 звезд или что-то подобное)
rating = models.PositiveSmallIntegerField(
  verbose_name='Рейтинг (1-5)',
  choices=[(i, f'{i} звезд') for i in range(1, 6)],
  null=True,
  blank=True
)
    
# 9. DurationField для времени акции (если это временное предложение)
sale_duration = models.DurationField(
  verbose_name='Длительность акции',
  null=True,
  blank=True,
  help_text='Формат: дни часы:минуты:секунды'
)
    
# 10. GenericIPAddressField для отслеживания IP продавца
seller_ip = models.GenericIPAddressField(
  verbose_name='IP продавца',
  protocol='both',
  unpack_ipv4=False,
  null=True,
  blank=True
)
    
# 11. SlugField для SEO-friendly URL
slug = models.SlugField(
  verbose_name='Слаг',
  max_length=50,
  allow_unicode=False,
  unique=True,
  null=True,
  blank=True
)
