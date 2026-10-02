void read_file(std::string name) {
  auto root = std::filesystem::weakly_canonical("/srv/files");
  auto target = std::filesystem::weakly_canonical(root / name);
  if (target.string().starts_with(root.string())) std::ifstream file(target);
}
