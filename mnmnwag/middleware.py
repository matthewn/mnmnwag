class AddUnpolyHeadersMiddleware(object):
    """
    Django reimplementation of
    https://github.com/unpoly/unpoly-rails/blob/master/lib/unpoly/rails/request_echo_headers.rb

    Echoes the request's URL as a response header `X-Up-Location` and the
    request's HTTP method as `X-Up-Method`.

    The Unpoly frontend requires these headers to detect redirects, which are
    otherwise undetectable for an AJAX client.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Up-Location'] = request.get_raw_uri()
        response['X-Up-Method'] = request.method
        return response
