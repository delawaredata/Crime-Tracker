import datetime
from django.db.models import Q
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
# from django.http import HttpResponseRedirect
from myproject.crime.models import Incident
from myproject.crime.forms import *


def _monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def index(request, map=False):
    """
    Main page. Includes map of incidents, headlines
    of recent incidents and photos of recent victims.
    Can be viewed at:
        /crime/  -- MAIN (can take "page" variable for pagination)
        /crime/map/  -- MAP
    Both returned pages accest a "time_frame" variable to limit
    the scope of the incidents. Appropriate GET values are:
        - all
        - week
        - one_month
        - six_months
        - year
    """
    # TIME FRAME FILTER
    today = datetime.date.today()
    since_date = None

    try:
        time_frame = str(request.GET.get('time_frame'))
    except ValueError:
        time_frame = 'all'

    if time_frame == 'all':
        incidents = Incident.objects.all().order_by('-inc_date')
    elif time_frame == 'week':
        since_date = today - datetime.timedelta(weeks=1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'one_month':
        since_date = _monthdelta(today, -1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'six_months':
        since_date = _monthdelta(today, -6)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'year':
        since_date = today.replace(year=today.year - 1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    else:
        incidents = Incident.objects.all().order_by('-inc_date')

    # MAIN INCIDENT DETAILS
    incident_details = []
    for incident in incidents:
        victims = incident.victims.all()
        suspects = incident.suspects.all()
        incident_details.append([incident, victims, suspects])

    # CHECK FOR MAP, APPLY
    if not map:  # For the normal main page.
        pagination = True
        paginator = Paginator(incident_details, 5)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            details = paginator.page(page)
        except (EmptyPage, InvalidPage):
            details = paginator.page(paginator.num_pages)

        variables = RequestContext(request, {
            'details': details,
            'since_date': since_date,
            'pagination': pagination
        })
        return render_to_response('crime/index.html', variables)
    else:  # Returned for the map page.
        pagination = False
        variables = RequestContext(request, {
            'details': incident_details,
            'since_date': since_date,
            'pagination': pagination
        })
        return render_to_response('crime/map.html', variables)


def victims_page(request):
    today = datetime.date.today()
    since_date = None

    try:
        time_frame = str(request.GET.get('time_frame'))
    except ValueError:
        time_frame = 'all'

    if time_frame == 'all':
        incidents = Incident.objects.all().order_by('-inc_date')
    elif time_frame == 'week':
        since_date = today - datetime.timedelta(weeks=1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'one_month':
        since_date = _monthdelta(today, -1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'six_months':
        since_date = _monthdelta(today, -6)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'year':
        since_date = today.replace(year=today.year - 1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    else:
        incidents = Incident.objects.all().order_by('-inc_date')

    victims_details = []
    for incident in incidents:
        victims = incident.victims.all().order_by('is_killed')
        victims_details.append([incident, victims])

    paginator = Paginator(victims_details, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        details = paginator.page(page)
    except (EmptyPage, InvalidPage):
        details = paginator.page(paginator.num_pages)

    variables = RequestContext(request, {
        'details': details,
        'since_date': since_date
    })
    return render_to_response('crime/victims.html', variables)


def suspects_page(request):
    today = datetime.date.today()
    since_date = None

    try:
        time_frame = str(request.GET.get('time_frame'))
    except ValueError:
        time_frame = 'all'

    if time_frame == 'all':
        incidents = Incident.objects.all().order_by('-inc_date')
    elif time_frame == 'week':
        since_date = today - datetime.timedelta(weeks=1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'one_month':
        since_date = _monthdelta(today, -1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'six_months':
        since_date = _monthdelta(today, -6)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    elif time_frame == 'year':
        since_date = today.replace(year=today.year - 1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date')
    else:
        incidents = Incident.objects.all().order_by('-inc_date')

    suspect_details = []
    for incident in incidents:
        suspects = incident.suspects.all().order_by('-arrest_date')
        suspect_details.append([incident, suspects])

    paginator = Paginator(suspect_details, 12)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        details = paginator.page(page)
    except (EmptyPage, InvalidPage):
        details = paginator.page(paginator.num_pages)

    variables = RequestContext(request, {
        'details': details,
        'since_date': since_date
    })
    return render_to_response('crime/suspects.html', variables)


def incident_page(request, Incident_id, Incident_inc_slug):
    """
    Includes details about a specific incident.
    Can be viewed at /crime/<INCIDENT_ID>/<INCIDENT_SLUG>/
    """
    incident = Incident.objects.get(id=Incident_id)
    victims = incident.victims.all()
    suspects = incident.suspects.all()
    variables = RequestContext(request, {
        'incident': incident,
        'suspects': suspects,
        'victims': victims
    })
    return render_to_response('crime/incident_page.html', variables)


def search_page(request):
    form = SearchForm()
    details = []
    show_results = False
    pagination = False
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})

            incidents = Incident.objects.filter(
                Q(headline__icontains=query) | Q(summary__icontains=query)
                ).order_by('-inc_date')
            for incident in incidents:
                victims = incident.victims.all()
                suspects = incident.suspects.all()
                details.append([incident, victims, suspects])
    variables = RequestContext(request, {
        'form': form,
        'details': details,
        'show_results': show_results,
        'pagination': pagination
    })
    if 'ajax' in request.GET:
        return render_to_response('crime/incident_list.html', variables)
    else:
        return render_to_response('crime/search.html', variables)
