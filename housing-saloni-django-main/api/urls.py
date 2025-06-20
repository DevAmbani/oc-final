from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file_view, name='upload_file_view'),
    path('delete/<int:pk>', views.delete_scrapped_data, name='delete_scrapped_data'),
    path('mark_issue/<int:pk>', views.mark_issue, name='mark_issue'),
    path('analysis', views.analysis, name='analysis'),
    path('analysis/<int:page_number>', views.get_analysis, name='analysis'),
    path('new_analysis', views.new_analysis, name='new_analysis'),
    path('new_analysis/<int:page_number>', views.get_new_analysis, name='new_analysis'),
    path('human_feedback/<int:pk>', views.human_feedback, name='human_feedback'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('add_tag/<int:pk>', views.add_tag, name='add_tag'),
    path('search_tag', views.search_tag, name='search_tag'),
    path('delete_tag/<int:pk>', views.delete_tag, name='delete_tag'),
    # path('get_user', views.get_user, name='get_user'),
]