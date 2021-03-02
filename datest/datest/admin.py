from django.contrib import admin
from django.contrib.admin import AdminSite

class EventAdminSite(AdminSite):
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
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
            "TESTREPORT": 10
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        # Sort the models alphabetically within each app.
        for i in range(len(app_list)-1):
            app_list[i]['models'].sort(key=lambda x: ordering[x['object_name']])
        return app_list