#include <iostream>
#include <string>
#include <cstdlib>
#include <vector>
#include <ctime>
#include <chrono>

#include "rapidjson/stringbuffer.h"
#include "rapidjson/document.h"
#include "rapidjson/prettywriter.h"
#include "rapidjson/stringbuffer.h"

#include <omp.h>

using namespace rapidjson;

struct triple {
  size_t h, t, r;
  triple(const size_t h, const size_t t, const size_t r):h(h), t(t), r(r) {}
};

struct edge {
  size_t dest, edge_type;
  edge(const size_t dest, const size_t edge_type): dest(dest), edge_type(edge_type) {}
};

using AdjList = std::vector<std::vector<edge>>;

bool load_triple(std::vector<triple> &buf, AdjList &adj_list, const char *fn) {
  FILE *f = fopen(fn, "r");
  size_t h, t, r;
  while (fscanf(f, "%ld%ld%ld", &h, &t, &r) != EOF) {
      buf.emplace_back(h, t, r);
      adj_list[h].emplace_back(t, r);
  }
}

const size_t node_num = 86054151;
const size_t feat_dim = 100;
const size_t feat_num = 1000;

const size_t edge_type_num = 1;

int main(const int argc, const char ** argv) {
  assert(argc >= 4);
  const char *src_path = argv[1];
  const char *dest_path = argv[2];
  const size_t partition_num = std::atoi(argv[3]);
  std::cout << "Converting " << src_path << " to " << dest_path << " parition:" 
            << partition_num << std::endl;

  srand(time(0));
  std::vector<triple> data;
  AdjList adj_list(node_num);

  load_triple(data, adj_list, src_path);
  std::cout << "Data loaded " << data.size() << " triples " << std::endl;

  std::vector<size_t> partition_map(node_num);
  std::vector<std::vector<size_t>> partition_nodes(partition_num);
  for (size_t i = 0 ; i < node_num ; ++i) {
    size_t pid = i % partition_num;
    partition_map[i] = pid;
    partition_nodes[pid].emplace_back(i);
  }
  std::cout << "Random partition finished" << std::endl;

  float feat_pool[feat_num][feat_dim];
  for (size_t i = 0 ; i < feat_num ; ++i) {
    for (size_t j = 0 ; j < feat_dim ; ++j)
      feat_pool[i][j] = 1.0 * rand() / RAND_MAX;
  }

  // Open files
  std::vector<FILE *> out_fd;
  for (size_t i = 0 ; i < partition_num ; ++i) {
    std::string fn = std::string(dest_path) + "_" + std::to_string(i) + ".json";
    out_fd.push_back(fopen(fn.c_str(), "w"));
  }

  std::chrono::steady_clock::time_point time_start = std::chrono::steady_clock::now();

  size_t cnt = 0;
  #pragma omp parallel 
  {
  size_t p_id = omp_get_thread_num();
  auto &fd = out_fd[p_id];
  for (size_t i = p_id ; 
       i < p_id + partition_num * partition_nodes[p_id].size() && i < node_num;
       i += partition_num) {
    Document root;
    root.SetObject();
    auto &allocator = root.GetAllocator();
    root.AddMember("node_id", i, allocator);
    root.AddMember("node_type", 0, allocator);
    root.AddMember("node_weight", 1, allocator);
    Value neighbor;
    neighbor.SetObject();
    std::vector<Value> etypes(edge_type_num);
    for (size_t etype_id =0 ; etype_id < edge_type_num ; etype_id++) {
      Value &etype = etypes[etype_id];
      etype.SetObject();
    }
    for (auto &edge:adj_list[i]) {
      size_t dest = edge.dest;
      // size_t edge_type = edge.edge_type;
      size_t edge_type = 0;
      std::string dest_id_str = std::to_string(dest);
      Value destId;
      destId.SetString(dest_id_str.c_str(), dest_id_str.length(), allocator);
      etypes[edge_type].AddMember(destId, 1, allocator);
    }
    for (size_t etype_id =0 ; etype_id < edge_type_num ; etype_id++) {
      std::string etype_id_str = std::to_string(etype_id);
      Value etypeId;
      etypeId.SetString(etype_id_str.c_str(), etype_id_str.length(), allocator);
      neighbor.AddMember(etypeId, etypes[etype_id], allocator);
    }
    root.AddMember("neighbor", neighbor, allocator);
    // root.AddMember("neighbor");
    Value uint64Value(kObjectType);
    root.AddMember("uint64_feature", uint64Value, allocator);
    Value floatValue(kObjectType);

    Value featValue(kArrayType);
    // generate feat
    size_t f_id = rand() % feat_num;
    const auto &feat = feat_pool[f_id];
    for (size_t j = 0 ; j < feat_dim ; ++j) {
      // featValue.PushBack((float)rand() / RAND_MAX, allocator);
      featValue.PushBack(feat[j], allocator);
    }
    floatValue.AddMember("0", featValue, allocator);
    root.AddMember("float_feature", floatValue, allocator);

    Value boolValue(kObjectType);
    root.AddMember("binary_feature", boolValue, allocator);

    Value edgesValue(kArrayType);
    for (const auto &edge:adj_list[i]) {
      Value edgeValue(kObjectType);
      edgeValue.AddMember("src_id", i, allocator);
      edgeValue.AddMember("dst_id", edge.dest, allocator);
      edgeValue.AddMember("edge_type", edge.edge_type, allocator);
      edgeValue.AddMember("weight", 1, allocator);
      Value intValue(kObjectType), floatValue(kObjectType), boolValue(kObjectType);
      edgeValue.AddMember("uint64_feature", intValue, allocator);
      edgeValue.AddMember("float_feature", floatValue, allocator);
      edgeValue.AddMember("binary_feature", boolValue, allocator);
      edgesValue.PushBack(edgeValue, allocator);
    }
    root.AddMember("edge", edgesValue, allocator);

    StringBuffer buffer;
    Writer<StringBuffer> writer(buffer);
    writer.SetMaxDecimalPlaces(6);
    root.Accept(writer);
    auto out = buffer.GetString();
    fputs(out, fd);
    fputs("\n", fd);
    fflush(fd);
    #pragma omp critical
    {
    ++cnt;
    if (cnt % 100000 == 0) {
      std::chrono::steady_clock::time_point time_end = std::chrono::steady_clock::now();
      std::chrono::duration<double> time_used = 
        std::chrono::duration_cast<std::chrono::duration<double>>(time_end-time_start);
      time_start = std::chrono::steady_clock::now();
      std::cout << "#" << cnt << " time use:" << time_used.count() << "s" <<std::endl;
    }
    }
  }
  }


  
  return 0;
}