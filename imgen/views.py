from django.shortcuts import render
from django.http import HttpResponse
import os
from pathlib import Path
from django.shortcuts import render, redirect
import requests
# from django.core.files.storage import FileSystemStorage
# from .models import Obj
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.core.files.storage import default_storage
from azure.storage.blob import ContainerClient
from django.contrib.auth.models import User
from django.apps import apps
Obj = apps.get_model(app_label='users', model_name='Obj')


BASE_DIR = Path(__file__).resolve().parent.parent


def home(request):
    return render(request, 'imgen/home.html')


def imgen(request):
    image_paths = []
    abs_dir = os.path.join(BASE_DIR, 'imgen', 'static', 'imgen', "image_thumbnails")
    rel_dir = '/' + '/'.join(['static', 'imgen', 'image_thumbnails'])
    dir_files = os.listdir(abs_dir)
    for file in dir_files:
        image_paths.append([f"{rel_dir}/{file}", file])
    
    rel_dir = "/static/imgen/objs"
    object_paths = []

    su = User.objects.filter(is_superuser=True)[0]
    obj_names = Obj.objects.filter(user_id=su.id)
    print(str(obj_names))
    context = {
        'object_paths': object_paths,
        'image_paths': image_paths,
    }
    context['lib_objs'] = obj_names
    return render(request, 'imgen/imgen.html', context)


def library(request):
    context = dict()
    con_str='DefaultEndpointsProtocol=https;AccountName=afteraisub1storage;AccountKey=pmabm0K12K0TGF2DiHvLd8Z0hg+/EA3UEs/eAd2KXE1Txj9s/VDxNowVQdixuv1RK83qeY97UlXH+AStJtJ6Iw==;EndpointSuffix=core.windows.net'

    if request.method == 'POST':
        print('post method')
        if 'obj_file' in request.FILES:
            # check file is valid - size limit & extension
            uploaded_file = request.FILES['obj_file']
            print('uploaded_file: ' + str(uploaded_file))
            if not uploaded_file._name[-4:] == ".obj":
                print("file is not a .obj")
                
            elif uploaded_file.size > 1_000_000:
                print('uploaded file size is ' + str(uploaded_file.size) + \
                '  is greater allowed size 10^6. Try removing verticed from the .obj')
            
            elif len(Obj.objects.all().filter(name=uploaded_file._name)) > 0:
                print('File already exists, please choose another name')
            
            else:
                # upload to azure
                print('uploading new obj')
                print(type(uploaded_file))
                container_name = request.user.username
                container_client = ContainerClient.from_connection_string(con_str, container_name)
                dst = "objs/" + uploaded_file._name
                print("dst: " + dst)
                blob_client = container_client.get_blob_client(dst)
                blob_client.upload_blob(uploaded_file)
                
                # store in database
                new_obj = Obj(user=request.user, name=uploaded_file._name)
                new_obj.save()
                print('obj saved to database')

    # get the names too
    su = User.objects.filter(is_superuser=True)[0]
    obj_names = Obj.objects.filter(user_id=su.id)
    context['lib_objs'] = obj_names
    return render(request, 'imgen/library.html', context)


# def add_obj_to_dataset(request, pk):
#     print('add_obj_to_dataset')
#     # user.active_dataset.objects.add(selected_obj)
#     # user.active_dataset.objs[name]
#     user = request.user
#     return redirect('imgen')


# def remove_obj_from_dataset(request):
#     print('remove_obj_from_dataset')
#     return redirect('imgen')


def download_dataset(request):
    print('Beginning download')
    file_name = "scene_000000.JPEG"
    blob_sas_url = 'https://afteraisub1storage.blob.core.windows.net/imgs?sp=racwdl&st=2022-10-24T20:37:57Z&se=2022-10-25T04:37:57Z&spr=https&sv=2021-06-08&sr=c&sig=Sw5x2hhDdu%2FcD3Yyh1X4b71hOO1k73SYtD3XCT38Jmo%3D'
    r = requests.get(blob_sas_url, stream=True)
    response = StreamingHttpResponse(streaming_content=r)
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


def contact(request):
    search_term = ''

    if 'search' in request.GET:
        search_term = request.GET['search']
        print('searching for "' + search_term + "\"")
        user_imgs_dir = "profiles/"  + request.user.username + "/objs"
        dir_files = os.listdir(user_imgs_dir)

    context = dict()
    return render(request, 'imgen/contact.html', context)


def view_that_asks_for_money(request):

    # What you want the button to do.
    paypal_dict = {
        "business": "receiver_email@example.com",
        "amount": "10000000.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('your-return-view')),
        "cancel_return": request.build_absolute_uri(reverse('your-cancel-view')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "payment.html", context)
