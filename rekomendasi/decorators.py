from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan role user
    allowed_roles: list of roles yang diizinkan (e.g., ['admin', 'kepala_sekolah'])
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Cek apakah user memiliki profile
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Profil user tidak ditemukan. Hubungi administrator.")
                return redirect('login')
            
            user_role = request.user.profile.role
            
            # Cek apakah role user diizinkan
            if user_role not in allowed_roles:
                messages.error(request, f"Akses ditolak. Fitur ini hanya untuk {', '.join(allowed_roles)}.")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator khusus untuk admin only"""
    return role_required(['admin'])(view_func)

def siswa_or_admin_required(view_func):
    """Decorator untuk siswa dan admin"""
    return role_required(['siswa', 'admin'])(view_func)

def kepala_sekolah_or_admin_required(view_func):
    """Decorator untuk kepala sekolah dan admin"""
    return role_required(['kepala_sekolah', 'admin'])(view_func)

def get_user_role(user):
    """Utility function untuk mendapatkan role user"""
    if hasattr(user, 'profile'):
        return user.profile.role
    return None

def create_user_profile_if_not_exists(user, role='siswa'):
    """Create UserProfile if doesn't exist"""
    from .models import UserProfile
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role=role)
    return user.profile
