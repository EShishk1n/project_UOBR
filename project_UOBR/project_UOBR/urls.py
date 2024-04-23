from django.contrib import admin
from django.urls import path, include

from dvizhenie.views import StaticPagesViews, DrillingRigViews, RigPositionViews, NextPositionsViews, SearchView, \
    LoadDataViews, PadViews

urlpatterns = []

urlpatterns += [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls'))
]

urlpatterns += [
    path('', StaticPagesViews.start_page, name='start_page'),
    path('about_app', StaticPagesViews.about_app, name='about_app'),
    path('contacts', StaticPagesViews.contacts, name='contacts')
]

urlpatterns += [
    path('rig', DrillingRigViews.DrillingRigView.as_view(), name='rig'),
    path('rig/add', DrillingRigViews.DrillingRigAddView.as_view(), name='rig_add'),
    path('rig/<int:pk>', DrillingRigViews.DrillingRigUpdateView.as_view(), name='rig_update'),
    path('rig/<int:pk>/delete', DrillingRigViews.DrillingRigDeleteView.as_view(), name='rig_delete')
]

urlpatterns += [
    path('pad', PadViews.PadView.as_view(), name='pad'),
    path('pad/add', PadViews.PadAddView.as_view(), name='pad_add'),
    path('pad/<int:pk>', PadViews.PadUpdateView.as_view(), name='pad_update'),
    path('pad/<int:pk>/delete', PadViews.PadDeleteView.as_view(), name='pad_delete')
]

urlpatterns += [
    path('rig_position', RigPositionViews.RigPositionView.as_view(), name='rig_position'),
    path('rig_position_add', RigPositionViews.RigPositionAddView.as_view(), name='rig_position_add'),
    path('rig_position/<int:pk>', RigPositionViews.RigPositionUpdateView.as_view(), name='rig_position_update'),
    path('rig_position/<int:pk>/delete', RigPositionViews.RigPositionDeleteView.as_view(), name='rig_position_delete')
]

urlpatterns += [
    path('next_position', NextPositionsViews.NextPositionView.as_view(), name='next_position'),
    path('next_position/<int:pk>', NextPositionsViews.get_detail_info_for_next_position, name='position_rating'),
    path('position_rating/<int:pk>', NextPositionsViews.get_detail_info_for_position_rating, name='position_rating_'),
    path('next_position/all/<int:pk>', NextPositionsViews.get_rating_for_all_possible_next_positions,
         name='position_rating_all'),
    path('commit_next_position/<int:pk>', NextPositionsViews.commit_next_position, name='commit_next_position'),
    path('change_next_position/<int:pk>', NextPositionsViews.change_next_position, name='change_next_position'),
    path('delete_next_position/<int:pk>', NextPositionsViews.delete_next_position, name='delete_next_position'),
    path('reset_all_changes', NextPositionsViews.reset_all_changes, name='reset_all_changes'),
    path('commited_next_position', NextPositionsViews.CommitedNextPositionView.as_view(),
         name='commited_next_position'),
    path('delete_commited_position/<int:pk>', NextPositionsViews.delete_commited_position,
         name='delete_commited_position'),
    path('commit_commited_position/<int:pk>', NextPositionsViews.commit_commited_position,
         name='commit_commited_position'),
]

urlpatterns += [
    path('search', SearchView.Search.as_view(), name='search')
]

urlpatterns += [
    path('upload_file', LoadDataViews.upload_file, name='upload_file'),
    path('export_data_pads', LoadDataViews.export_data_pads, name='export_data_pads'),
    path('export_data_rig_positions', LoadDataViews.export_data_rig_positions, name='export_data_rig_positions')
]
