

from django.http import JsonResponse


def needed_channel(request):
    needed_channel = request.POST.get('needed_channel', 'Дай-май')
    result = {'needed_channel': needed_channel}
    return JsonResponse(result)