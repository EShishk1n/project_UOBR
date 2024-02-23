from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.utils.translation import gettext as _

from .forms import DrillingRigForm, PadForm, RigPositionForm, UploadFileForm, ExportDataForm, DefinePositionForm, \
    RigPositionAddForm
from .models import DrillingRig, Pad, RigPosition, NextPosition, PositionRating
from .services.data_putter import put_rigs_position_data, put_pads_data
from .services.data_taker import take_file_cration_data
from .services.define_position import define_position_and_put_into_BD
from .services.define_rigs_for_definition_next_position import _get_status_to_pads
from .services.func_for_view import handle_uploaded_file, _change_next_position, get_search_result
from .services.get_rating import _get_marker_for_drilling_rig, _get_inf_about_RNB_department


def start_page(request):
    """Рендерит стартовую страницу"""

    return render(request, 'dvizhenie/start_page.html')


def about_app(request):
    """Рендерит страницу 'о приложении'"""

    return render(request, 'dvizhenie/about_app.html')


def contacts(request):
    """Рендерит страницу 'контакты'"""

    return render(request, 'dvizhenie/contacts.html')


class DrillingRigView(LoginRequiredMixin, ListView):
    """Отображает данные из модели DrillingRig"""

    template_name = 'dvizhenie/rig.html'
    context_object_name = 'rigs'
    model = DrillingRig
    fields = '__all__'


class DrillingRigAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель DrillingRig"""

    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.add_drillingrig'


class DrillingRigUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели DrillingRig"""

    model = DrillingRig
    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.change_drillingrig'


class DrillingRigDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели DrillingRig"""

    model = DrillingRig
    context_object_name = 'rig'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    template_name = 'dvizhenie/delete_rig.html'
    permission_required = 'dvizhenie.delete_drillingrig'


class PadView(LoginRequiredMixin, ListView):
    """Отображает данные из модели Pad"""

    queryset = (Pad.objects.exclude(status='drilling') & Pad.objects.exclude(status='drilled'))
    template_name = 'dvizhenie/pad.html'
    context_object_name = 'pads'


class PadAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель Pad"""

    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.add_pad'


class PadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели Pad"""

    model = Pad
    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.change_pad'


class PadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели Pad"""

    model = Pad
    pk_url_kwarg = 'pk'
    context_object_name = 'pad'
    success_url = reverse_lazy('pad')
    template_name = 'dvizhenie/delete_pad.html'
    permission_required = 'dvizhenie.delete_pad'


class RigPositionView(LoginRequiredMixin, ListView):
    """Отображает данные из модели RigPosition"""

    template_name = 'dvizhenie/rig_position.html'
    context_object_name = 'rig_positions'
    queryset = RigPosition.objects.filter(pad__status='drilling')

    def get(self, request, *args, **kwargs):

        _get_status_to_pads()

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                    self.object_list, "exists"
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )
        context = self.get_context_data()
        return self.render_to_response(context)


class RigPositionAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель RigPosition"""

    form_class = RigPositionAddForm
    template_name = 'dvizhenie/add_rig_position.html'
    success_url = reverse_lazy('rig_position')
    permission_required = 'dvizhenie.add_rigposition'


class RigPositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели RigPosition"""

    model = RigPosition
    form_class = RigPositionForm
    context_object_name = 'rig_position'
    template_name = 'dvizhenie/update_rig_position.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig_position')
    permission_required = 'dvizhenie.change_rigposition'


class RigPositionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели RigPosition"""

    model = RigPosition
    pk_url_kwarg = 'pk'
    context_object_name = 'rig_position'
    success_url = reverse_lazy('rig_position')
    template_name = 'dvizhenie/delete_rig_position.html'
    permission_required = 'dvizhenie.delete_rigposition'


class NextPositionView(LoginRequiredMixin, PermissionRequiredMixin, ListView, FormMixin):
    """Отображает экземпляры из модели NextPosition по которым требуются действия специалиста"""

    template_name = 'dvizhenie/next_position.html'
    context_object_name = 'next_positions'
    queryset = (NextPosition.objects.filter(status='Требуется подтверждение') |
                NextPosition.objects.filter(status='Изменено. Требуется подтверждение') |
                NextPosition.objects.filter(status='Отсутствют кандидаты') |
                NextPosition.objects.filter(status='Удалено пользователем'))
    ordering = "current_position__end_date"
    permission_required = 'dvizhenie.view_nextposition'

    form_class = DefinePositionForm

    def post(self, request):
        form = DefinePositionForm(request.POST)
        if form.is_valid():
            define_position_and_put_into_BD(start_date_for_calculation=form.cleaned_data['start_date_for_calculation'],
                                            end_date_for_calculation=form.cleaned_data['end_date_for_calculation'])
            return redirect('next_position')
        else:
            return redirect('next_position')


@login_required(login_url='accounts/')
def get_detail_info_for_next_position(request, pk):
    """Получает подробную информацию об экземляре NextPosition (рейтинг, маркер, стратегию)"""

    if request.method == 'GET':
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = (
                PositionRating.objects.filter(current_position=next_position_object.current_position.id)
                & PositionRating.objects.filter(next_position=next_position_object.next_position.id))

        marker = _get_marker_for_drilling_rig(
            rig_for_define_next_position=position_rating[0].current_position)

        strategy = _get_inf_about_RNB_department(
            rig_for_define_next_position=position_rating[0].current_position)

        return render(request, 'dvizhenie/position_rating.html',
                      {"position_rating": position_rating[0], "marker": marker, "strategy": strategy})


@login_required(login_url='accounts/')
def get_detail_info_for_position_rating(request, pk):
    """Получает подробную информацию об экземляре PositionRating (рейтинг, маркер, стратегию)"""

    if request.method == 'GET':
        position_rating = PositionRating.objects.filter(id=pk)

        marker = _get_marker_for_drilling_rig(
            rig_for_define_next_position=position_rating[0].current_position)

        strategy = _get_inf_about_RNB_department(
            rig_for_define_next_position=position_rating[0].current_position)

        return render(request, 'dvizhenie/position_rating.html',
                      {"position_rating": position_rating[0], "marker": marker, "strategy": strategy})


@login_required(login_url='accounts/')
def get_rating_for_all_possible_next_positions(request, pk):
    """Получает все экземпляры модели PositionRating для БУ, для которой определяется следующая позиция"""

    if request.method == 'GET':
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = PositionRating.objects.filter(
            current_position=next_position_object.current_position.id).order_by('-common_rating')

        return render(request, 'dvizhenie/position_rating_all.html',
                      {"position_rating": position_rating})


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def commit_next_position(request, pk):
    """Подтверждает (меняет статус пары в NextPosition на 'подтверждено') следующую позицию для БУ"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(status='Подтверждено')
        pad_id = NextPosition.objects.filter(id=pk)[0].next_position.id

        Pad.objects.filter(id=pad_id).update(status='commited_next_positions')

    return redirect('next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def change_next_position(request, pk):
    """Берет из рейтинга другую позицию для БУ и вставляет в NextPosition со статусом
    'Изменено. Требуется подтверждение'"""

    if request.method == 'GET':
        different_next_position = PositionRating.objects.filter(id=pk)[0]
        _change_next_position(different_next_position=different_next_position)

    return redirect('next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def delete_next_position(request, pk):
    """Удаляет текущее предложение NextPosition"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(next_position=None)
        NextPosition.objects.filter(id=pk).update(status='Удалено пользователем')

    return redirect('next_position')


class CommitedNextPositionView(LoginRequiredMixin, ListView):
    """Отображает, подтвержденные специалистом, экземплры модели NextPosition"""

    template_name = 'dvizhenie/commited_next_position.html'
    context_object_name = 'next_positions'
    queryset = NextPosition.objects.filter(status='Подтверждено')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def delete_commited_position(request, pk):
    """Меняет статус подтвержденной пары на 'Требуется подтверждение'"""

    if request.method == 'GET':
        next_position = NextPosition.objects.filter(id=pk)
        Pad.objects.filter(id=next_position[0].next_position.id).update(status='')
        next_position.update(next_position=None)
        next_position.update(status='Удалено пользователем')

    return redirect('commited_next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def commit_commited_position(request, pk):
    """Переносит пару из подтвержденных позиций (актуальное движение) в расположение БУ"""

    if request.method == 'GET':
        next_position = NextPosition.objects.filter(id=pk)
        drilling_rig = next_position[0].current_position.drilling_rig
        pad = next_position[0].next_position

        NextPosition.objects.filter(id=pk).delete()
        RigPosition(drilling_rig=drilling_rig, pad=pad).save()

    return redirect('commited_next_position')


class Search(LoginRequiredMixin, ListView):
    """Поиск по моделям приложения"""

    template_name = "dvizhenie/search.html"
    context_object_name = "result"

    def get_id(self) -> dict:
        return {'pad': Pad.objects.filter(number__contains=self.request.GET.get('q')).values_list('id'),
                'rig': DrillingRig.objects.filter(number__contains=self.request.GET.get('q')).values_list('id')}

    def get_queryset(self) -> list:
        pads_id = self.get_id()['pad']
        rigs_id = self.get_id()['rig']
        result = get_search_result(pads_id, rigs_id)

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')

        return context


@permission_required(perm='dvizhenie.change_rigposition', raise_exception=True)
def export_data_rig_positions(request):
    """Обновляет даты окончания бурения по инф. из загруженного файла 'Движение_БУ'"""

    file_creation_date = take_file_cration_data()
    try:
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
            if form.is_valid():
                put_rigs_position_data(table_start_row=form.cleaned_data['table_start_row'],
                                       table_end_row=form.cleaned_data['table_end_row'])
                return redirect('rig_position')
        else:
            form = ExportDataForm()

        return render(request, "dvizhenie/export_data_rig_positions.html", {"form": form,
                                                                            "file_creation_date": file_creation_date})
    except IndexError:

        return render(request, "dvizhenie/export_data_rig_positions.html",
                      {"error_message": 'На данной кустовой площадке нет буровой установки'})
    except AttributeError:
        return render(request, "dvizhenie/export_data_rig_positions.html",
                      {"error_message": 'Пустая ячейка с датой в файле "Движение_БУ"'})
    except IntegrityError:
        return render(request, "dvizhenie/export_data_rig_positions.html",
                      {"error_message": 'Некорректный тип данных'})
    except ValueError:
        return render(request, "dvizhenie/export_data_rig_positions.html",
                      {"error_message": 'Несоответствие данных в файле "Движение_БУ"'})


@permission_required(perm='dvizhenie.change_pad', raise_exception=True)
def export_data_pads(request):
    """Обновляет информацию по кустам по инф. из загруженного файла 'Движение_БУ'"""

    file_creation_date = take_file_cration_data()
    try:
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
            if form.is_valid():
                put_pads_data(table_start_row=form.cleaned_data['table_start_row'],
                              table_end_row=form.cleaned_data['table_end_row'])
                return redirect('pad')
        else:
            form = ExportDataForm()

        return render(request, "dvizhenie/export_data_pads.html", {"form": form,
                                                                   "file_creation_date": file_creation_date})
    except AttributeError:
        return render(request, "dvizhenie/export_data_pads.html",
                      {"error_message": 'Пустая ячейка с датой в файле "Движение_БУ"'})
    except IntegrityError:
        return render(request, "dvizhenie/export_data_pads.html",
                      {"error_message": 'Некорректный тип данных'})
    except ValueError:
        return render(request, "dvizhenie/export_data_pads.html",
                      {"error_message": 'Несоответствие данных в файле "Движение_БУ"'})


@permission_required(perm='dvizhenie.change_rigposition', raise_exception=True)
def upload_file(request):
    """Рендерит страницу с загрузкой, загружает файл"""

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = UploadFileForm()

    return render(request, "dvizhenie/upload_file.html", {"form": form})
