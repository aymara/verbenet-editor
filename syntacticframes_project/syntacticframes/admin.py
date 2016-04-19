from django.contrib import admin
from django.core.urlresolvers import reverse

from reversion.admin import VersionAdmin

from .models import LevinClass, VerbNetClass, VerbNetFrameSet, VerbNetMember, \
    VerbNetFrame, VerbNetRole, VerbTranslation


# Inline models
class InlineEditLinkMixin(object):
    readonly_fields = ['edit_details']
    edit_label = "Edit"

    def edit_details(self, obj):
        if obj.id:
            opts = self.model._meta
            return "<a href='%s' target='_blank'>%s</a>" % (reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.object_name.lower()),
                args=[obj.id]
            ), self.edit_label)
        else:
            return "(save to edit details)"
    edit_details.allow_tags = True


class VerbNetMemberInline(InlineEditLinkMixin, admin.TabularInline):
    fk_name = 'frameset'
    model = VerbNetMember
    extra = 0

admin.site.register(LevinClass)


class VerbNetClassAdmin(VersionAdmin):
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


class VerbNetFrameSetAdmin(VersionAdmin):
    search_fields = ('name',)
    inlines = [VerbNetMemberInline]

admin.site.register(VerbNetFrameSet, VerbNetFrameSetAdmin)


class VerbNetMemberAdmin(VersionAdmin):
    search_fields = ("lemma",)
    pass

admin.site.register(VerbNetMember, VerbNetMemberAdmin)


class VerbNetFrameAdmin(VersionAdmin):
    search_fields = ('syntax', 'example',)

admin.site.register(VerbNetFrame, VerbNetFrameAdmin)


class VerbNetRoleAdmin(VersionAdmin):
    search_fields = ("name",)
    pass

admin.site.register(VerbNetRole, VerbNetRoleAdmin)


class VerbTranslationAdmin(VersionAdmin):
    search_fields = ("verb",)
    pass

admin.site.register(VerbTranslation, VerbTranslationAdmin)
