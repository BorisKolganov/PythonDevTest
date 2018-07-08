from django.core.exceptions import ValidationError
from import_export import resources
from phonenumber_field.formfields import PhoneNumberField

from core.models import User
from django.forms.fields import EmailField


class UserResources(resources.ModelResource):
    class Meta:
        model = User
        exclude = ('is_active', 'is_staff', 'is_superuser', 'password', 'last_login', 'groups', 'user_permissions', 'date_joined')

    def before_import_row(self, row, **kwargs):
        EmailField().run_validators(row.get('email'))
        PhoneNumberField().run_validators(row.get('phone'))

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)

    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.is_active = True
