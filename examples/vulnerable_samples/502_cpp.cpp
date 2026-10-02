void load(std::istream& data) {
  boost::archive::text_iarchive archive(data);
  archive >> user_object;
}
