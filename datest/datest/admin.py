from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import Http404
from django.apps import apps
from django.utils.translation import gettext as _
from django.template.response import TemplateResponse

class EventAdminSite(AdminSite):
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Project": 1,
            "Api": 3,
            "BASEURL": 4,
            "Header": 5,
            "Testcase": 7,
            "TESTSUITE": 8,
            "Testbatch": 9,
            "TESTREPORT": 10,
            "Jenkinsreport": 11,
            "DebugTalk": 12
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        # Sort the models alphabetically within each app.
        if app_list != []:
            for i in range(len(app_list)-1):
                if app_list[i]['name'] == 'api测试':
                    app_list[i]['models'].sort(key=lambda x: ordering[x['object_name']])
        return app_list

    def app_index(self, request, app_label, extra_context=None):
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')

        super().app_index(request, app_label, extra_context=None)

        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        # Sort the models alphabetically within each app.
        ordering = {
            "Project": 1,
            "ApiGroup": 2,
            "Api": 3,
            "BASEURL": 4,
            "Header": 5,
            "TestcaseGroup": 6,
            "Testcase": 7,
            "TESTSUITE": 8,
            "Testbatch": 9,
            "TESTREPORT": 10,
            "Jenkinsreport": 11,
            "DebugTalk": 12
        }
        if app_dict!= {}:
            app_dict['models'].sort(key=lambda x: ordering[x['object_name']])
        app_name = apps.get_app_config(app_label).verbose_name
        context = {
            **self.each_context(request),
            'title': _('%(app)s administration') % {'app': app_name},
            'app_list': [app_dict],
            'app_label': app_label,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context)