from django.contrib import admin

from .models import LevinClass, VerbNetClass, VerbNetFrameSet, VerbNetMember \
    VerbNetFrame, VerbNetRole, VerbTranslation

admin.site.register(LevinClass)


class VerbNetClassAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbNetClass, VerbNetClassAdmin)


class VerbNetFrameSetAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbNetFrameSet, VerbNetFrameSetAdmin)


class VerbNetMemberAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbNetMember, VerbNetMemberAdmin)


class VerbNetFrameAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbNetFrame, VerbNetFrameAdmin)


class VerbNetRoleAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbNetRole, VerbNetRoleAdmin)


class VerbTranslationAdmin(reversion.VersionAdmin):
    pass
admin.site.register(VerbTranslation, VerbTranslationAdmin)
