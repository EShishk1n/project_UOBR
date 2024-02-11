from datetime import date

import django
from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View, generic
from django.db.utils import IntegrityError

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .forms import DrillingRigForm, PadForm, RigPositionForm, UploadFileForm, ExportDataForm
from .models import DrillingRig, Pad, RigPosition, NextPosition, PositionRating
from .services.data_putter import put_rigs_position_data, put_pads_data
from .services.data_taker import take_file_cration_data
from .services.define_position import define_position_and_put_into_BD
from .services.func_for_view import handle_uploaded_file
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

    template_name = 'dvizhenie/rig.html'
    context_object_name = 'rigs'
    model = DrillingRig
    fields = '__all__'


class DrillingRigAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.add_drillingrig'


class DrillingRigUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = DrillingRig
    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.change_drillingrig'


class DrillingRigDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = DrillingRig
    context_object_name = 'rig'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    template_name = 'dvizhenie/delete_rig.html'
    permission_required = 'dvizhenie.delete_drillingrig'


class PadView(LoginRequiredMixin, ListView):
    queryset = (Pad.objects.exclude(status='drilling_or_drilled_pad') & Pad.objects.exclude(number='Мобилизация'))
    template_name = 'dvizhenie/pad.html'
    context_object_name = 'pads'


class PadAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.add_pad'


class PadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Pad
    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.change_pad'


class PadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Pad
    pk_url_kwarg = 'pk'
    context_object_name = 'pad'
    success_url = reverse_lazy('pad')
    template_name = 'dvizhenie/delete_pad.html'
    permission_required = 'dvizhenie.delete_pad'


class RigPositionView(LoginRequiredMixin, ListView):
    template_name = 'dvizhenie/rig_position.html'
    context_object_name = 'rig_positions'
    model = RigPosition
    fields = '__all__'


class RigPositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = RigPosition
    form_class = RigPositionForm
    context_object_name = 'rig_position'
    template_name = 'dvizhenie/update_rig_position.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig_position')
    permission_required = 'dvizhenie.change_rigposition'


@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def define_next_position(request):
    if request.method == 'GET':
        define_position_and_put_into_BD()
    return redirect("next_position")


class NextPositionView(LoginRequiredMixin, ListView):
    template_name = 'dvizhenie/next_position.html'
    context_object_name = 'next_positions'
    queryset = (NextPosition.objects.filter(status='Требуется подтверждение') |
                NextPosition.objects.filter(status='Изменено. Требуется подтверждение') |
                NextPosition.objects.filter(status='Отсутствют кандидаты') |
                NextPosition.objects.filter(status='Удалено пользователем'))
    ordering = "status"


class PositionRatingDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
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


class PositionRatingListView(LoginRequiredMixin, View):

    def get(self, request, pk):
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = PositionRating.objects.filter(
            current_position=next_position_object.current_position.id).order_by('-common_rating')

        return render(request, 'dvizhenie/position_rating_all.html',
                      {"position_rating": position_rating})


@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def commit_next_position(request, pk):
    """Подтверждает (меняет статус пары в NextPosition на 'подтверждено') следующую позицию для БУ"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(status='Подтверждено')
        pad_id = NextPosition.objects.filter(id=pk)[0].next_position.id
        Pad.objects.filter(id=pad_id).update(status='commited_next_positions')

    return redirect('define_next_position')


@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def change_next_position(request, pk):
    """Берет из рейтинга другую позицию для БУ и вставляет в NextPosition со статусом
    'Изменено. Требуется подтверждение'"""

    if request.method == 'GET':
        different_next_position = PositionRating.objects.filter(id=pk)[0]
        try:
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                next_position=different_next_position.next_position)
        except IntegrityError:
            NextPosition.objects.filter(next_position=different_next_position.next_position).update(next_position=None)
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                next_position=different_next_position.next_position)
        finally:
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                status='Изменено. Требуется подтверждение')

    return redirect('next_position')


@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def delete_next_position(request, pk):
    """Удаляет текущее предложение NextPosition"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(next_position=None)
        NextPosition.objects.filter(id=pk).update(status='Удалено пользователем')

    return redirect('next_position')


class CommitedNextPositionView(LoginRequiredMixin, ListView):
    template_name = 'dvizhenie/commited_next_position.html'
    context_object_name = 'next_positions'
    queryset = NextPosition.objects.filter(status='Подтверждено')


@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def delete_commited_position(request, pk):
    """Меняет статус подтвержденной пары на 'Требуется подтверждение'"""

    if request.method == 'GET':
        next_position = NextPosition.objects.filter(id=pk)
        next_position.update(status='Требуется подтверждение')
        Pad.objects.filter(id=next_position[0].next_position.id).update(status='')
        next_position.delete()
    return redirect('commited_next_position')


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


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class Search(LoginRequiredMixin, ListView):
    template_name = "dvizhenie/search.html"
    context_object_name = "result"

    def get_id(self) -> dict:
        return {'pad': Pad.objects.filter(number__contains=self.request.GET.get('q')).values_list('id'),
                'rig': DrillingRig.objects.filter(number__contains=self.request.GET.get('q')).values_list('id')}

    def get_queryset(self) -> list:
        pads_id = self.get_id()['pad']
        rigs_id = self.get_id()['rig']
        result = []
        result_pads_id = []
        result_rigs_id = []
        for pad_id in pads_id:
            pad = Pad.objects.filter(id=pad_id[0])
            rig_position = RigPosition.objects.filter(pad=pad_id[0])
            res_ = [pad, rig_position]
            result_pads_id.append(res_)
        result.append(result_pads_id)

        for rig_id in rigs_id:
            rig = DrillingRig.objects.filter(id=rig_id[0])
            rig_position = RigPosition.objects.filter(drilling_rig=rig_id[0])
            res_ = [rig, rig_position]
            result_rigs_id.append(res_)
        result.append(result_rigs_id)

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
            return redirect('export_data')
    else:
        form = UploadFileForm()

    return render(request, "dvizhenie/upload_file.html", {"form": form})
