# this is mostly taken from the wagtail bakerydemo

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404
from django.shortcuts import render

from wagtail.models import Page
from wagtail.contrib.search_promotions.models import Query


def search(request):
    if 'mahnamahna' not in request.get_host():
        raise Http404
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        search_results = Page.objects.live().public().search(search_query)

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'is_search_page': True,
        'page_message': 'seek and ye shall find. (or perhaps not.)',
        'search_query': search_query,
        'search_results': search_results,
    })
