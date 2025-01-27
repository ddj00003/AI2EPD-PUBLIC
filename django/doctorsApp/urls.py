from django.urls import path
from . import views

app_name = 'doctorsApp'
urlpatterns = [
    path('', views.main, name='home'),
    path('summary/<int:id>', views.summary, name='summary'),
    path('getSummary/<int:id>', views.get_summary, name='getSummary'),
    path('infoContract/<int:id>', views.info_contract, name='infoContract'),
    path('editContract/<int:id>', views.edit_contract, name='editContract'),
    path('createContract/<int:id>', views.create_new_contract, name='createContract'),
    path('downloadSummary/<int:id>', views.download_summary, name='downloadSummary'),
    path('saveContract/<int:id>', views.save_contract, name='saveContract'),
    path('viewAllContracts/<int:id>', views.view_all_contracts, name='viewAllContracts'),
    path('getSummaryCustom/<int:id>', views.get_summary_custom, name='getSummaryCustom'),
]