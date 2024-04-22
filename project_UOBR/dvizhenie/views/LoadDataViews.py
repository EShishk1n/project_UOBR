from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction, IntegrityError
from django.shortcuts import redirect, render

from dvizhenie.forms import ExportDataForm, UploadFileForm
from dvizhenie.services.funcs_for_views.handle_upload_file import handle_uploaded_file
from dvizhenie.services.load_data_from_excel.pads_data.put_pads_data import put_pads_data
from dvizhenie.services.load_data_from_excel.rigs_position_data.put_rigs_position_data import put_rigs_position_data
from dvizhenie.services.load_data_from_excel.take_file_creation_date import take_file_creation_date


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_rigposition', raise_exception=True)
@transaction.atomic
def export_data_rig_positions(request):
    """Обновляет даты окончания бурения по инф. из загруженного файла 'Движение_БУ'"""

    file_creation_date = take_file_creation_date()

    try:
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
            if form.is_valid():
                result = put_rigs_position_data(table_start_row=form.cleaned_data['table_start_row'],
                                                table_end_row=form.cleaned_data['table_end_row'])
                if result is None:
                    return redirect('rig_position')
                else:
                    return render(request, "dvizhenie/export_data_rig_positions.html",
                                  dict(error_message=result['error_message'], error_rig_position=str(
                                      result['rig_position']['number']) + str(result['rig_position']['field'])))
            else:
                return render(request, 'dvizhenie/export_data_rig_positions.html',
                              {'error_message': 'В форме введены некорректные данные! Введите целые числа больше 1.'})
        else:
            form = ExportDataForm()
            return render(request, "dvizhenie/export_data_rig_positions.html", {"form": form,
                                                                                "file_creation_date": file_creation_date})

    except AttributeError:
        return render(request, "dvizhenie/export_data_rig_positions.html",
                      {"error_message": 'Проверьте корректность заполнения таблицы в файле!!!'})


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_pad', raise_exception=True)
@transaction.atomic
def export_data_pads(request):
    """Обновляет информацию по кустам по инф. из загруженного файла 'Движение_БУ'"""

    file_creation_date = take_file_creation_date()
    try:
        if request.method == 'POST':
            form = ExportDataForm(request.POST)
            if form.is_valid():
                result = put_pads_data(table_start_row=form.cleaned_data['table_start_row'],
                                       table_end_row=form.cleaned_data['table_end_row'])
                if result is None:
                    return redirect('pad')
                else:
                    return render(request, "dvizhenie/export_data_pads.html",
                                  dict(error_message=result['error_message'], error_pad_data=str(
                                      result['pad_data']['number']) + str(result['pad_data']['field'])))
            else:
                return render(request, 'dvizhenie/export_data_pads.html',
                              {'error_message': 'В форме введены некорректные данные! Введите целые числа больше 1.'})

        else:
            form = ExportDataForm()

        return render(request, "dvizhenie/export_data_pads.html", {"form": form,
                                                                   "file_creation_date": file_creation_date})
    except AttributeError:
        return render(request, "dvizhenie/export_data_pads.html",
                      {"error_message": 'Проверьте корректность заполнения таблицы в файле!!!'})
    except IntegrityError:
        return render(request, "dvizhenie/export_data_pads.html",
                      {"error_message": 'Проверьте корректность заполнения таблицы в файле!!!'})


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_rigposition', raise_exception=True)
def upload_file(request):
    """Рендерит страницу с загрузкой, загружает файл"""

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if str(request.FILES['file'])[-5:] == '.xlsx':
                handle_uploaded_file(request.FILES["file"])
                return redirect(request.session['return_path'])
            else:
                return render(request, "dvizhenie/upload_file.html",
                              {"form": form, "error_message": 'Необходимо загрузить файл в формате ".xlsx"!'})

    else:
        form = UploadFileForm()
        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')

    return render(request, "dvizhenie/upload_file.html", {"form": form})
