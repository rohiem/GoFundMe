from django.shortcuts import get_object_or_404, redirect, render
from .forms import UserForm,ProfileForm
from django.contrib.auth.decorators import login_required
from .models import History,Petition,Profile
from django.urls import reverse,reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from django.conf import settings

import stripe
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
stripe.api_key = "sk_test_IuOGDfRGnLAtweFksrmP3RRM00hqU6j3VY"



def SignUp(request):
    if request.method=='POST':
        form1 = UserForm(request.POST or None)
        form2 = ProfileForm(request.POST or None,request.FILES or None)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            profile=form2.save(commit=False)
            profile.user=user
            profile.save()

            return redirect('/')
    else:
        form1 =UserForm()
        form2=ProfileForm()

    context={"form1":form1,"form2":form2}

    return render(request,'signup.html',context)

class PetitionCreation(LoginRequiredMixin, CreateView):
    model = Petition
    template_name = 'create.html'
    fields =["target","title","for_who","zip_code","image","story","youtube"]

    def form_valid(self, form):
        form.instance.user =self.request.user
        return super(PetitionCreation, self).form_valid(form)


class PetitionUpdate(LoginRequiredMixin, UpdateView):
    model = Petition
    template_name = 'update_petition.html'
    fields =["target"]

    def form_valid(self, form):
        form.instance.user =self.request.user
        return super(PetitionUpdate, self).form_valid(form)


def home(request):
    petitions_created=Petition.objects.all().order_by('-created')[:3]
    petitions_edited=Petition.objects.all().order_by('-edited')[:3]
    qs=Petition.objects.all().order_by("-created")
    queryset=request.GET.get("q",None)
    if queryset is not None:
        qs=Petition.objects.filter(Q(title__icontains=queryset)|
        Q(user__username__icontains=queryset)
            )
    context={"petitions":petitions_created,"petitions_edited":petitions_edited,"qs":qs}
    if request.user.is_authenticated:

        followings=Petition.objects.filter(follows=request.user).order_by("-edited")[0:3]
        context.update({"followings":followings})
    return render(request,"home.html",context)


def petition_detail(request,pk):
    petition=Petition.objects.get(id=pk)
    history=History.objects.filter(petition=petition)[::-1]
    count=History.objects.filter(petition=petition).count()

    petition_detail = get_object_or_404(Petition, id=pk)

    total_follows = petition_detail.total_follows()
    followed = False
    if petition_detail.follows.filter(id=request.user.id).exists():
        followed = True
    return render(request, 'petition_detail.html',{"petition":petition,"sum":sum,"total_follows":total_follows,"followed":followed,"count":count,"history":history})


def follow(request, pk):
    petition = get_object_or_404(Petition , id=request.POST.get("petition_id"))
    followed = False
    if petition.follows.filter(id=request.user.id).exists():
        petition.follows.remove(request.user)
        followed = False
    else:
        petition.follows.add(request.user)
        followed = True
    return HttpResponseRedirect(reverse("core:petition_detail", args=[str(pk)]))
@login_required(login_url='core:login')
def petition_donation(request,pk):
    petition=Petition.objects.get(id=pk)
    history=History.objects.filter(petition=petition)
    sum=0
    for amount in history:
        sum+=amount.amount
    return render(request, 'pay.html',{"petition":petition,"sum":sum})

@login_required(login_url='core:login')
def charge(request,pk):
    if request.method == 'POST':
        print('Data:', request.POST)
        petition=Petition.objects.get(id=pk)
        amount=int(request.POST['amount'])
        history=History(user=request.user,amount=amount ,petition =petition)

        history.save()
        customer=stripe.Customer.create(
			email=request.user.email,
			name=request.user.username,
			source=request.POST['stripeToken']
			)
			
        charge=stripe.Charge.create(
			customer=customer,
			amount=amount*100,
			currency="usd",
			description="Donation",
			)

    return redirect(reverse('core:success' ,args=[amount,pk]))

@login_required(login_url='core:login')
def successMsg(request,pk, args):
    amount = args
    send_mail(
    'donation succefully sent',
    'we received your donation.$'+amount,
    settings.EMAIL_HOST_USER,
    [request.user.email],
    fail_silently=False,
)
    petition=Petition.objects.get(id=pk)
    history=History.objects.filter(petition=petition)
    sum=0
    for amount in history:
        sum+=amount.amount
    petition.donated=sum
    petition.save()
    return render(request, 'success.html', {'amount':amount})


@login_required(login_url='core:login')
def update_profile_view(request,slug):
    profile=get_object_or_404(Profile,slug=slug)
    user=get_object_or_404(User,id=profile.user_id)
    if request.method=='POST':
        userForm=UserForm(request.POST or None ,instance=user)
        profileForm=ProfileForm(request.POST or None,request.FILES or None,instance=profile)
        if userForm.is_valid() and profileForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            profileForm.save()
            return redirect(reverse("core:profile",args=[str(slug)]))
    else:
        userForm=UserForm(request.POST or None ,instance=user)
        profileForm=ProfileForm(request.POST or None,request.FILES or None,instance=profile)
    mydict={'form1':userForm,'form2':profileForm}

    return render(request,'update_profile.html',context=mydict)

@login_required(login_url='core:login')
def profile_view(request,slug):
    profile=get_object_or_404(Profile,slug=slug)
    user=get_object_or_404(User,id=profile.user.id)
    petitions=Petition.objects.filter(user=user)
    follows=Petition.objects.filter(follows=user).order_by("-edited")
    return render(request,'profile.html',{"profile":profile,"petitions":petitions,"follows":follows})
