import operator
from functools import reduce

import os

import tablib
from _mysql_exceptions import IntegrityError
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from core.models import User
from core.resources import UserResources


class UsersListView(ListView):
    model = User
    paginate_by = 10
    context_object_name = 'users'
    template_name = 'users_list.html'
    ordering = ['id']
    search_fields = ['email', 'name', 'phone', 'company', 'interests']

    def get_queryset(self):
        search = self.request.GET.get('search')

        qs = super().get_queryset().filter(is_active=True)
        if search:
            orm_lookups = ['{}__icontains'.format(search_field) for search_field in self.search_fields]
            for bit in search.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                qs = qs.filter(reduce(operator.or_, or_queries))
        return qs


class UserCreateView(CreateView):
    model = User
    fields = ['name', 'email', 'phone', 'company', 'interests']
    context_object_name = 'user'
    template_name = 'cu_user.html'

    def get_success_url(self):
        return reverse('core:user_detail', args=(self.object.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_header'] = 'Add user'
        return context


class UserUpdateView(UpdateView):
    model = User
    fields = ['name', 'email', 'phone', 'company', 'interests']
    context_object_name = 'user'
    template_name = 'cu_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_header'] = 'Update user'
        return context

    def get_success_url(self):
        return reverse('core:user_detail', args=(self.object.id,))


class UserDetailView(DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'user_detail.html'


class UserDeleteView(DeleteView):
    model = User
    context_object_name = 'user'
    success_url = reverse_lazy('core:users_list')
    template_name = 'user_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)


class UserExportView(View):
    def get(self, request, *args, **kwargs):
        frmt = request.GET.get('format', 'csv')
        if frmt not in ['csv', 'json']:
            return HttpResponseBadRequest('invalid file format')

        dataset = getattr(UserResources().export(), frmt)
        content_type = 'text/csv' if frmt == 'csv' else 'application/json'

        response = HttpResponse(dataset, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="users.{}"'.format(frmt)
        return response


class UserImportView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return HttpResponseNotFound('file not found')
        frmt = os.path.splitext(file.name)[-1]
        if frmt not in ['.csv', '.json']:
            return HttpResponseBadRequest('invalid file format')

        data = tablib.Dataset()
        if frmt == '.csv':
            data.csv = file.file.read().decode('utf-8')
        else:
            data.json = file.file.read().decode('utf-8')

        ur = UserResources()
        try:
            res = ur.import_data(dataset=data, dry_run=True)
        except (IntegrityError, ValidationError):
            return HttpResponseBadRequest('invalid data')

        if res.has_errors():
            return HttpResponseBadRequest('invalid data')

        UserResources().import_data(dataset=data, dry_run=False)
        messages.add_message(request, messages.INFO, 'Success import')
        return HttpResponseRedirect(reverse('core:users_list'))