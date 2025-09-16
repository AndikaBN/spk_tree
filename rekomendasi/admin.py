
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Student, Prediction, TrainingRecord, UserProfile

# Inline UserProfile untuk User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend User admin untuk include UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_role', 'get_phone')
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = 'Role'
    
    def get_phone(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.phone
        return '-'
    get_phone.short_description = 'Phone'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'nis', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'nis')
    ordering = ('-created_at',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "nis", "jurusan")
    search_fields = ("name", "nis", "jurusan")

@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display = ("name", "nilai_mtk", "nilai_bindo", "nilai_bing", "nilai_ipa", "minat", "jurusan")
    list_filter = ("jurusan", "minat")

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ("student", "jurusan_prediksi", "probability", "created_at")
    list_filter = ("jurusan_prediksi",)
