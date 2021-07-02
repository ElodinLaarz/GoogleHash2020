import sys


with open(sys.argv[1], "r") as f:
    #Line1
    line = f.readline().split()
    num_vids = int(line[0],10)
    num_endpoints = int(line[1],10)
    num_requests = int(line[2],10)
    num_caches = int(line[3],10)
    cache_size = int(line[4],10)
    #Videos
    line = f.readline().split()
    key = 0
    vid_dict = {}
    for e in line:
        vid_dict[key] = int(e,10)
        key += 1
    #Endpoints
    ep_dict = {}
    for i in range(num_endpoints):
        line = f.readline().split()
        dc_latency = int(line[0],10)
        caches = int(line[1],10)
        cache_list = []
        for j in range(caches):
            line = f.readline().split()
            cache_id = int(line[0],10)
            cache_latency = int(line[1],10)
            cache_list.append((cache_id, cache_latency))
        ep_dict[i] = (dc_latency, caches, cache_list)
    #Requests
    reqs = []
    for i in range(num_requests):
        line = f.readline().split()
        req_id = int(line[0],10)
        ep_id = int(line[1],10)
        iterations = int(line[2],10)
        reqs.append((req_id, ep_id, iterations))

with open(sys.argv[2], "r") as f:
    N = int(f.readline().split()[0],10)
    cache_contents = {}
    video_topology = {}
    for i in range(N):
        line = f.readline().split()
        cache_id = int(line[0],10)
        contents = []
        total_size = 0
        for j in range(1, len(line)):
            vid_id = int(line[j],10)
            contents.append(vid_id)
            total_size += vid_dict[vid_id]
            try:
                video_topology[vid_id].append(cache_id)
            except KeyError:
                video_topology[vid_id] = [cache_id]
        cache_contents[cache_id] = contents
        assert(total_size <= cache_size)
    #Iterate over requests
    total_reqs = 0
    time_saved = 0
    for req in reqs:
        latencies = [ep_dict[req[1]][0]]
        for cache in ep_dict[req[1]][2]:
            try:
                if cache[0] in video_topology[req[0]]:
                    latencies.append(cache[1])
            except KeyError:
                pass
        time_saved += req[2]*(latencies[0] - min(latencies))
        total_reqs += req[2]
    score = (time_saved/total_reqs)*1000
    print(score)

