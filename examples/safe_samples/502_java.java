Request load(String data) throws Exception {
  return new ObjectMapper().readValue(data, Request.class);
}
