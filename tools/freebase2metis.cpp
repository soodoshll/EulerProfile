#include <iostream>
#include <cstdlib>
#include <vector>
#include <cassert>

using AdjList = std::vector<std::vector<size_t>>;

const size_t node_num = 86054151;

size_t load_triple(AdjList &adj_list, const char *fn) {
  FILE *f = fopen(fn, "r");
  size_t h, t, r, cnt = 0;
  while (fscanf(f, "%ld%ld%ld", &h, &t, &r) != EOF) {
      adj_list[h].emplace_back(t);
      adj_list[t].emplace_back(h);
      ++cnt;
  }
  return cnt;
}

int main(const int argc, const char ** argv) {
  assert(argc >= 3);
  const char *src_path = argv[1];
  const char *dest_path = argv[2];
  AdjList adj_list(node_num);
  size_t edge_num = load_triple(adj_list, src_path);
  std::cout << "Data loaded " << edge_num << " triples " << std::endl;
  FILE *dest_file = fopen(dest_path, "w");
  fprintf(dest_file, "%ld %ld\n", node_num, edge_num);
  for (size_t i = 0 ; i < node_num ; ++i ) {
    if (i % 10000 == 0) {
      std::cout << i << std::endl;
    }
    for (const auto &e : adj_list[i]) {
      fprintf(dest_file, "%ld ", e+1);
    }
    fputs("\n", dest_file);
  }
  fclose(dest_file);
  return 0;
}