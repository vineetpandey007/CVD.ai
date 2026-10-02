void showName(HttpServletRequest req, PrintWriter out) {
  out.println("<p>" + req.getParameter("name") + "</p>");
}
