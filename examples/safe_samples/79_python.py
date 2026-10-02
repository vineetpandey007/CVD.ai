import html
def show_name(request):
    return "<p>" + html.escape(request.args["name"]) + "</p>"
