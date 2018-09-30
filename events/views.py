from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from events.models import Event, Reservation
from events.forms import CreateEventForm, JoinForm
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from django.template.defaulttags import register
import calendar
from django.utils import timezone

from events.settings import BOOKING_TOMORROW


class EventListView(ListView):
    template_name = 'events/event_list.html'
    model = Event

    # Returns number of spots filled for an event
    @register.filter
    def reserved_places(event):
        return event.reserved_places()

    # Checks if an event has been joined by the user
    @register.filter
    def is_joined(event, user):
        return event.is_joined(user)

    # Return the reservation for an event
    @register.filter
    def get_reservation_pk(event, user):
        return get_object_or_404(Reservation, event=event, user=user).pk

    # Converts a given month number to an abbreviation (eg. 8 = Aug)
    @register.filter
    def month_abbr(month_num):
        return calendar.month_abbr[int(month_num)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'events': Event.objects.filter(date__gte=timezone.now()).order_by('date', 'time'),
        })
        return context

class EventView(DetailView):
    template_name = 'events/event.html'
    model = Event

class JoinView(CreateView):
    template_name = 'events/join_event.html'
    model = Reservation
    form_class = JoinForm

    def get_context_data(self, **kwargs):
        context = super(JoinView, self).get_context_data(**kwargs)
        context['event'] = self.get_event()
        return context


    def get_form_kwargs(self):
        kwargs = super(JoinView, self).get_form_kwargs()
        if kwargs['instance'] is None:
            kwargs['instance'] = Reservation()
        kwargs['instance'].user = self.request.user
        kwargs['instance'].event = self.get_event()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('join_confirmation_view', kwargs={'pk': self.get_event().pk})

    def get_event(self):
        try:
            return Event.objects.get(pk=self.kwargs['event_id'])
        except Event.DoesNotExist:
            raise Http404("The event does not exist")


class JoinConfirmationView(DetailView):
    model = Event
    template_name = 'events/join_confirmation.html'

class LeaveView(DeleteView):
    model = Reservation
    template_name = 'events/leave.html'
    success_url = '/events'

    def get_context_data(self, **kwargs):
        context = super(LeaveView, self).get_context_data(**kwargs)
        context['event'] = self.get_reservation().event
        return context

    def get_reservation(self):
        try:
            return Reservation.objects.get(pk=self.kwargs['pk'])
        except Event.DoesNotExist:
            raise Http404("Cannot leave this event. No reservation was found")

class CreateEventView(CreateView):
    template_name = 'events/create_event.html'
    model = Event
    form_class = CreateEventForm
    success_url = '/events'
    initial = {'date':BOOKING_TOMORROW}

    def get_form_kwargs(self):
        kwargs = super(CreateEventView, self).get_form_kwargs()
        if kwargs['instance'] is None:
            kwargs['instance'] = Event()
        kwargs['instance'].host = self.request.user
        return kwargs

