void load(std::string data) {
  auto value = nlohmann::json::parse(data);
  if (value.contains("name")) user_object.name = value["name"].get<std::string>();
}
