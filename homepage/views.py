from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from homepage.models import Ticket, MyUser
from homepage.forms import LoginForm, AddTicketForm

# Create your views here.
@login_required
def index(request):
    my_tickets = Ticket.objects.all()
    new_tickets = Ticket.objects.filter(status="NW")
    inprogress_tickets = Ticket.objects.filter(status="IP")
    done_tickets = Ticket.objects.filter(status="DN")
    invalid_tickets = Ticket.objects.filter(status="IN")
    return render(request,
     "index.html",
      {
        "tickets": my_tickets,
        "new_tickets": new_tickets,
        "inprogress_tickets": inprogress_tickets,
        "done_tickets": done_tickets,
        "invalid_tickets": invalid_tickets,
      }
      )

@login_required
def ticket_detail(request, ticket_id):
    my_ticket = Ticket.objects.filter(id=ticket_id).first()
    return render(request, "ticket_detail.html", {"ticket": my_ticket})

@login_required
def assign_ticket_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.assigned = request.user.username
    ticket.status = "IP"
    ticket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def complete_ticket_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.assigned = None
    ticket.completed = request.user.username
    ticket.status = "DN"
    ticket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def reopen_ticket_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.assigned = request.user.username
    ticket.completed = None
    ticket.status = "IP"
    ticket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def return_ticket_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.assigned = None
    ticket.completed = None
    ticket.status = "NW"
    ticket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def invalid_ticket_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.assigned = None
    ticket.completed = None
    ticket.status = "IN"
    ticket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def ticket_edit_view(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    if request.method == "POST":
        form = AddTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ticket.title = data["title"]
            ticket.description = data["description"]
            ticket.save()
        return HttpResponseRedirect(reverse("ticket_view", args=[ticket.id]))

    data = {
        "title": ticket.title,
        "description": ticket.description
    }
    form = AddTicketForm(initial=data)
    return render(request, "generic_form.html", {"form": form})

@login_required
def user_detail(request, user_id):
    name = MyUser.objects.filter(id=user_id).first()
    user_tickets = Ticket.objects.filter(filing_user=name.id)
    inprogress_tickets = Ticket.objects.filter(status="IP", filing_user=name.id)
    completed_tickets = Ticket.objects.filter(status="DN", filing_user=name.id)
    invalid_tickets = Ticket.objects.filter(status="IN", filing_user=name.id)
    return render (
                    request,
                    "user_detail.html",
                    {"user_tickets": user_tickets,
                     "name": name,
                     "ip_tickets": inprogress_tickets,
                     "completed_tickets": completed_tickets,
                     "invalid_tickets": invalid_tickets,
                    })

@login_required
def add_ticket(request):
    user = MyUser.objects.filter(username=request.user.username).first()
    if request.method == "POST":
        form = AddTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Ticket.objects.create(
                title=data.get("title"),
                description=data.get("description"),
                filing_user=user,
                assigned=None
            )
            return HttpResponseRedirect(reverse("homepage"))
    
    form = AddTicketForm()
    return render(request, "generic_form.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data.get("username"), password=data.get("password"))
            if user:
                login(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse("homepage")))

    form = LoginForm()
    return render(request, "generic_form.html", {"form": form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("homepage"))