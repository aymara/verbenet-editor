from django.contrib import admin
from django.core.urlresolvers import reverse

import reversion

from .models import LevinClass, VerbNetClass, VerbNetFrameSet, VerbNetMember, \
    VerbNetFrame, VerbNetRole, VerbTranslation

admin.site.register(LevinClass)


class VerbNetClassAdmin(reversion.VersionAdmin):
    readonly_fields = ("levin_class", "name", "show_url",)
    search_fields = ("name",)

    def show_url(self, instance):
        url = "{}#{}".format(
            reverse("syntacticframes.views.classe", kwargs={"class_number": instance.number()}),
            instance.name)
        return """<a href="{0}">{0}</a>""".format(url)

    show_url.short_description = "URL"
    show_url.allow_tags = True

admin.site.register(VerbNetClass, VerbNetClassAdmin)


class VerbNetFrameSetAdmin(reversion.VersionAdmin):
    search_fields = ('name',)

admin.site.register(VerbNetFrameSet, VerbNetFrameSetAdmin)


class VerbNetMemberAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetMember, VerbNetMemberAdmin)


class VerbNetFrameAdmin(reversion.VersionAdmin):
    search_fields = ('syntax', 'example',) 

admin.site.register(VerbNetFrame, VerbNetFrameAdmin)


class VerbNetRoleAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbNetRole, VerbNetRoleAdmin)


class VerbTranslationAdmin(reversion.VersionAdmin):
    pass

admin.site.register(VerbTranslation, VerbTranslationAdmin)
