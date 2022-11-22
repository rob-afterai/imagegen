from django.shortcuts import render, redirect
from wsgiref.util import FileWrapper
import mimetypes
from .forms import UserRegisterForm, DatasetForm
from django.http import StreamingHttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from .models import Dataset, Obj
import shutil
import json
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, ContainerClient, generate_blob_sas, BlobSasPermissions


connect_str = "DefaultEndpointsProtocol=https;AccountName=afteraisub1storage;AccountKey=pmabm0K12K0TGF2DiHvLd8Z0hg+/EA3UEs/eAd2KXE1Txj9s/VDxNowVQdixuv1RK83qeY97UlXH+AStJtJ6Iw==;EndpointSuffix=core.windows.net"


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            # todo: if number of symbol in username, fail.
            messages.success(request, f'Account created for {username}!')
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_client = blob_service_client.create_container(username)
            print('Created user ' + str(username))
            print('Created container ' + str(container_client))
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    datasets = user.dataset_set.all()
    context = {
        'datasets': datasets
    }
    return render(request, 'users/profile.html' , context)


def create_dataset(request):
    dataset = Dataset(user=request.user)
    n = request.user.profile.dataset_count
    dataset.name = "dataset" + str(n)
    request.user.profile.dataset_count += 1
    request.user.profile.save()
    dataset.save()
    return redirect('edit_dataset', dataset.pk)


def edit_dataset(request, pk):
    dataset = Dataset.objects.get(pk=pk)
    if not request.user.is_authenticated:
        print('user not authenticated')
        return redirect('home')
    form = DatasetForm()
    context = dict()
    
    if request.method == "POST":
        # search for objs
        print('post')
        if 'searched' in request.POST:
            searched = request.POST['searched']
            obj = Obj.objects.filter(name__contains=searched).first()
            print('search for \'' + searched + '\'')
            if obj:
                print("found " + obj.name)
                # add obj to dataset obj list as a json string
                objs_json = json.loads(dataset.objs_list_json_str)
                objs_json.append(obj.name)
                dataset.objs_list_json_str = json.dumps(objs_json)
                print(dataset.objs_list_json_str)
                dataset.save()
            else:
                print("no object found")
        # form
        else:
            # form = DatasetForm(request.POST)
            # if form.is_valid():
            #     dataset.no_images = form.cleaned_data.get('no_images')
            #     dataset.image_height = form.cleaned_data.get('image_height')
            #     dataset.image_width = form.cleaned_data.get('image_width')
            #     dataset.image_extension = form.cleaned_data.get('image_extension')
            #     dataset.color_mode = form.cleaned_data.get('color_mode')
            #     dataset.segmented_labelling = form.cleaned_data.get('segmented_labelling')
            #     dataset.json_label = form.cleaned_data.get('json_label')
            #     print('dataset saved')
            # else:
            #     print('form invalid')
            pass

    print('dataset created')
    context['lib_objs'] = []
    for ob_name in json.loads(dataset.objs_list_json_str):
        o = Obj.objects.get(name=ob_name)
        context['lib_objs'].append(o)
    context['dataset'] = dataset
    context["form"] = form
    dataset.save()
    return render(request, 'users/create_dataset.html', context)


def view_dataset(request, pk):
    dataset = Dataset.objects.get(pk=pk)
    form = DatasetForm()
    context = dict()

    # get selected objects from library
    context['lib_objs'] = []
    for ob_name in json.loads(dataset.objs_list_json_str):
        o = Obj.objects.get(name=ob_name)
        context['lib_objs'].append(o)
    context['dataset'] = dataset
    context["form"] = form

    # get generated images
    _account_key = "pmabm0K12K0TGF2DiHvLd8Z0hg+/EA3UEs/eAd2KXE1Txj9s/VDxNowVQdixuv1RK83qeY97UlXH+AStJtJ6Iw=="
    username = request.user.username
    container = ContainerClient.from_connection_string(connect_str, username)
    account_name = 'afteraisub1storage'
    context['image_paths'] = []
    for blob in container.list_blobs():
        if not blob.name.startswith(dataset.name):
            continue
        sas_url = generate_blob_sas(account_name,
                                    container_name=username,
                                    blob_name = blob.name,
                                    account_key = _account_key,
                                    permission=BlobSasPermissions(read=True),
                                    expiry= datetime.utcnow() + timedelta(hours=1))
        url = 'https://' + account_name + '.blob.core.windows.net/' + username + '/' + blob.name + '?' + sas_url
        print(url)
        context['image_paths'].append([url, 'scene_000001.JPEG'])
    return render(request, 'users/view_dataset.html', context)


def remove_obj(request, pk, obj_pk):
    dataset = Dataset.objects.get(pk=pk)
    obj = Obj.objects.get(pk=obj_pk)
    objs_json = json.loads(dataset.objs_list_json_str)
    print('removing obj ' + str(obj.name))
    new_list = []
    for o in objs_json:
        if o != obj.name:
            new_list.append(o)
    dataset.objs_list_json_str = json.dumps(new_list)
    dataset.save()
    return redirect('dataset', pk)


def test(request):
    if request.method == "POST":
        print('post')
        form = DatasetForm(request.POST)
        # if form.is_valid():
        no_images = form.cleaned_data['no_images']
        ds = Dataset()
        ds.no_images = no_images
        # ds.save()
    else:
        form = DatasetForm()
    return render(request, "users/test.html", {"form":form})


def generate_images(request, pk):
    # 1. get database and container
    jobs_container = ContainerClient.from_connection_string(connect_str, "jobs")
    dataset = Dataset.objects.get(pk=pk)
    blob_name = request.user.username + "/" + dataset.name + ".json"

    # 2. write params to dict
    settings_dict = dict()
    settings_dict['username'] = request.user.username
    settings_dict['dataset_name'] = dataset.name
    settings_dict["no_images"] = dataset.no_images
    settings_dict["image_height"] = dataset.image_height
    settings_dict["image_width"] = dataset.image_width
    settings_dict["image_extension"] = dataset.image_extension
    settings_dict["color_mode"] = dataset.color_mode
    settings_dict['segmented_labelling'] = dataset.segmented_labelling
    settings_dict['json_label'] = dataset.json_label

    objs_json = json.loads(dataset.objs_list_json_str)
    settings_dict['objects'] = []
    for obj_name in objs_json:
        settings_dict['objects'].append(obj_name)

    # 3. upload to job container
    json_str = json.dumps(settings_dict, indent=4)
    blob_client = jobs_container.get_blob_client(blob_name)
    blob_client.upload_blob(json_str)

    print("Sending instructions to server for " + dataset.name)
    dataset.job_generated = True
    # return success message
    return redirect('view_dataset', pk)


def download_dataset(request, pk):
    chunk_size = 8192
    dataset = Dataset.objects.get(pk=pk)
    src_folder = dataset.path_to_images + "/images"
    dst_folder = dataset.path_to_images + "_zip"
    print("src_folder: " + src_folder)
    print("dst_folder: " + dst_folder)
    # zip_folder = dataset.path_to_images + "\\" + dataset.title
    print("zip_folder: " + zip_folder)
    shutil.make_archive(zip_folder, 'zip', src_folder)
    zip_folder_zip = zip_folder + ".zip"
    response = StreamingHttpResponse(FileWrapper(open(zip_folder_zip, 'rb'), chunk_size),
        content_type=mimetypes.guess_type(zip_folder)[0])
    response['Content-Length'] = os.path.getsize(zip_folder_zip)
    response['Content-Disposition'] = f"Attachment; filename={zip_folder_zip}"  # dataset.title
    return response


def delete_dataset(request, pk):
    print('deleting')
    if request.method=='POST':
        dataset = Dataset.objects.get(pk=pk)
        print("dataset: " + str(dataset))
        # todo: delete folder in azure
        dataset.delete()
        print("no_datasets: " + str(len(request.user.dataset_set.all()) + 1))
    return redirect('profile')
