from django.shortcuts import redirect


def redirect_2_admin(request):
    return redirect("admin/")
