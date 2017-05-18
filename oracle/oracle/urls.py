"""oracle URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from app.views import (CheckContractCode, DumpContractState, GetBalance,
                       GetStorage, NewTxNotified, Proposes, ProposalList,
                       Multisig_addr, Sign, SignNew, NewProposes, AddressNotified)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^proposals/', Proposes.as_view()),
    url(r'^newproposals/', NewProposes.as_view()),
    url(r'^sign/', Sign.as_view()),
    url(r'^signnew/', SignNew.as_view()),
    url(r'^multisigaddress/', Multisig_addr.as_view()),
    url(r'^proposallist/', ProposalList.as_view()),
    url(r'^storage/(?P<multisig_address>[a-zA-Z0-9]+)/', GetStorage.as_view()),
    url(r'^states/(?P<multisig_address>[a-zA-Z0-9]+)/$', DumpContractState.as_view()),
    url(r'^balance/(?P<multisig_address>[a-zA-Z0-9]+)/(?P<address>[a-zA-Z0-9]+)$',
        GetBalance.as_view()),
    url(r'^getcontract/(?P<multisig_address>[a-zA-Z0-9]+)/', CheckContractCode.as_view()),
    url(r'^notify/(?P<tx_hash>[a-zA-Z0-9]+)', NewTxNotified.as_view()),
    url(r'^states/', include('evm_manager.urls', namespace='evm_manager')),
    url(r'^addressnotify/(?P<multisig_address>[a-zA-Z0-9]+)(|/)$', AddressNotified.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
