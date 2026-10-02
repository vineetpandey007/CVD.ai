void showName(HttpServletRequest req, PrintWriter out) {
  out.println("<p>" + Encode.forHtml(req.getParameter("name")) + "</p>");
}
