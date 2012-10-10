import datetime
from django.db.models import Q, Avg
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
# from django.http import HttpResponseRedirect
from myproject.crime.models import Incident, Suspect, Victim
from myproject.crime.forms import *


def _monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def _getAggregateInfo():
    """
    Returns a dictionary of stats from the data,
    including success rates and average ages.
    """
    homicide_count = Incident.objects.filter(is_homicide=True).count()
    homicide_arrest_count = Incident.objects.filter(is_homicide=True, is_suspects_unknown=False).count()
    homicide_success_rate = homicide_arrest_count * 100.00 / homicide_count
    # Success rate for non-homicides
    shooting_count = Incident.objects.filter(is_homicide=False).count()
    shooting_arrest_count = Incident.objects.filter(is_homicide=False, is_suspects_unknown=False).count()
    shooting_success_rate = shooting_arrest_count * 100.00 / shooting_count
    # Success rate for all incidents
    total_count = Incident.objects.all().count()
    tot_arrest_count = Incident.objects.filter(is_suspects_unknown=False).count()
    tot_success_rate = tot_arrest_count * 100.00 / total_count

    agg_info = {
        'sus_avg_age': Suspect.objects.all().aggregate(Avg('age')).values()[0],
        'vic_avg_age': Victim.objects.all().aggregate(Avg('age')).values()[0],
        'homicide_count': homicide_count,
        'homicide_arrest_count': homicide_arrest_count,
        'homicide_success_rate': homicide_success_rate,
        'shooting_count': shooting_count,
        'shooting_arrest_count': shooting_arrest_count,
        'shooting_success_rate': shooting_success_rate,
        'total_count': total_count,
        'tot_arrest_count': tot_arrest_count,
        'tot_success_rate': tot_success_rate
    }
    return agg_info


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

    agg_info = _getAggregateInfo()

    # CHECK FOR MAP, APPLY
    if not map:  # For the normal main page.
        pagination = True
        paginator = Paginator(incidents, 10)
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
            'agg_info': agg_info,
            'since_date': since_date,
            'time_frame': time_frame,
            'pagination': pagination
        })
        return render_to_response('crime/index.html', variables)
    else:  # Returned for the map page.
        pagination = False
        variables = RequestContext(request, {
            'details': incidents,
            'since_date': since_date,
            'time_frame': time_frame,
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
        incidents = Incident.objects.all().order_by('-inc_date', '-inc_time')
    elif time_frame == 'week':
        since_date = today - datetime.timedelta(weeks=1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'one_month':
        since_date = _monthdelta(today, -1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'six_months':
        since_date = _monthdelta(today, -6)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'year':
        since_date = today.replace(year=today.year - 1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    else:
        incidents = Incident.objects.all().order_by('-inc_date', '-inc_time')

    victims_details = []
    for incident in incidents:
        victims = incident.victims.filter(is_unidentified=False).order_by('is_killed')
        for victim in victims:
            if victim in victims_details:
                pass
            else:
                victims_details.append(victim)

    paginator = Paginator(victims_details, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        details = paginator.page(page)
    except (EmptyPage, InvalidPage):
        details = paginator.page(paginator.num_pages)

    agg_info = _getAggregateInfo()

    variables = RequestContext(request, {
        'details': details,
        'agg_info': agg_info,
        'time_frame': time_frame,
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
        incidents = Incident.objects.all().order_by('-inc_date', '-inc_time')
    elif time_frame == 'week':
        since_date = today - datetime.timedelta(weeks=1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'one_month':
        since_date = _monthdelta(today, -1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'six_months':
        since_date = _monthdelta(today, -6)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    elif time_frame == 'year':
        since_date = today.replace(year=today.year - 1)
        incidents = Incident.objects.filter(inc_date__gte=since_date).order_by('-inc_date', '-inc_time')
    else:
        incidents = Incident.objects.all().order_by('-inc_date', '-inc_time')

    suspect_details = []
    for incident in incidents:
        suspects = incident.suspects.all().order_by('-arrest_date')
        for suspect in suspects:
            if suspect in suspect_details:
                pass
            else:
                suspect_details.append(suspect)

    paginator = Paginator(suspect_details, 15)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        details = paginator.page(page)
    except (EmptyPage, InvalidPage):
        details = paginator.page(paginator.num_pages)

    agg_info = _getAggregateInfo()

    variables = RequestContext(request, {
        'details': details,
        'agg_info': agg_info,
        'time_frame': time_frame,
        'since_date': since_date
    })
    return render_to_response('crime/suspects.html', variables)


def incident_page(request, Incident_id, Incident_inc_slug):
    """
    Includes details about a specific incident.
    Can be viewed at /crime/<INCIDENT_ID>/<INCIDENT_SLUG>/
    """
    incident = Incident.objects.get(id=Incident_id)
    agg_info = _getAggregateInfo()
    variables = RequestContext(request, {
        'incident': incident,
        'agg_info': agg_info
    })
    return render_to_response('crime/incident_page.html', variables)


def search_page(request):
    form = SearchForm()
    show_results = False
    pagination = False
    agg_info = _getAggregateInfo()

    variables = RequestContext(request, {
        'form': form,
        'agg_info': agg_info,
        'show_results': show_results,
        'pagination': pagination
    })

    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})

            incidents = Incident.objects.filter(
                Q(headline__icontains=query) | Q(summary__icontains=query)
                ).order_by('-inc_date', '-inc_time')

            variables = RequestContext(request, {
                'form': form,
                'details': incidents,
                'agg_info': agg_info,
                'show_results': show_results,
                'pagination': pagination
            })

    if 'ajax' in request.GET:
        return render_to_response('crime/incident_list.html', variables)
    else:
        return render_to_response('crime/search.html', variables)
