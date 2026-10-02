def show_name(request):
    return "<p>" + request.args["name"] + "</p>"
