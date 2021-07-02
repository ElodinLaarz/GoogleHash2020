import sys
from operator import itemgetter
from biased_selector import biased_selector

def pseudoscore(video, cache):
    global vid_dict, cache_dict, num_endpoints
    return ((vid_dict[video][1]/num_endpoints)*(cache_dict[cache][0]/num_endpoints)*vid_dict[video][2]*cache_dict[cache][1])

def score(per_cache_contents): #TODO
    global ep_dict, reqs
    video_topology = {}
    for cache_id in per_cache_contents:
        contents = per_cache_contents[cache_id][1:]
        for vid_id in contents:
            try:
                video_topology[vid_id].append(cache_id)
            except KeyError:
                video_topology[vid_id] = [cache_id]
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
    return score

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
        vid_dict[key] = [int(e,10), 0, 0]
        key += 1
    #Endpoints
    ep_dict = {}
    cache_dict = {}
    for i in range(num_endpoints):
        line = f.readline().split()
        dc_latency = int(line[0],10)
        caches = int(line[1],10)
        cache_list = []
        for j in range(caches):
            line = f.readline().split()
            cache_id = int(line[0],10)
            cache_latency = int(line[1],10)
            try:
                cache_dict[cache_id][1] *= cache_dict[cache_id][0]
                cache_dict[cache_id][0] += 1
                cache_dict[cache_id][1] = (cache_dict[cache_id][1] + (dc_latency - cache_latency))/cache_dict[cache_id][0] 
            except KeyError:
                cache_dict[cache_id] = [1, dc_latency - cache_latency]
            cache_list.append((cache_id, cache_latency))
        ep_dict[i] = (dc_latency, caches, cache_list)
    #Requests
    reqs = []
    for i in range(num_requests):
        line = f.readline().split()
        req_id = int(line[0],10) #Video ID
        ep_id = int(line[1],10)
        iterations = int(line[2],10)
        reqs.append((req_id, ep_id, iterations))
        vid_dict[req_id][1] += 1 #Assuming that there aren't any duplicate request entries naming the same EP requesting the same Video
        vid_dict[req_id][2] += iterations

    #Order (video, cache) tuples:
    tup_list = []
    list_dict = {}
    for i in range(num_vids):
        for j in range(num_caches):
            tup = (i,j)
            tup_list.append([pseudoscore(i,j), tup])
        tup_list.sort(key=itemgetter(0))
        list_dict[i] = tup_list
        tup_list = []
    #---------------------------------------------------------------------------------------------------------------------------------------------------#
    #Create a biased selector for each video tuple list: TODO: Maybe make the list_dict ordered from highest requested video to lowest.
    max_score = 0
    max_contents = None
    for k in range(10):
        selectors = [biased_selector(list_dict[e], lambda x: x**2) for e in list_dict]
        per_cache_contents = {}
        while selectors != []:
            delete_list = []
            for i in range(len(selectors)):
                selector = selectors[i]
                success = False
                while not success: #Success here is biased towards equal video representation. TODO: Maybe skip the video if the choice selected doesn't fit.
                    try:
                        selection = selector.draw(replace=False)
                    except IndexError:
                        break
                    video_size = vid_dict[selection[1][0]][0]
                    try:
                        if (per_cache_contents[selection[1][1]][0] + video_size) <= cache_size: #Choice fits
                            per_cache_contents[selection[1][1]][0] += video_size
                            per_cache_contents[selection[1][1]].append(selection[1][0])
                            success = True
                    except KeyError:
                        if video_size <= cache_size:
                            per_cache_contents[selection[1][1]] = [video_size, selection[1][0]]
                if not success:
                    delete_list.append(i)
            offset = 0
            delete_list.sort()
            for e in delete_list:
                del(selectors[e-offset])
                offset += 1
        prelim_score = score(per_cache_contents)
        print("Attempt " + str(k) + " got a score of " + str(prelim_score))
        if  prelim_score > max_score:
            max_contents = per_cache_contents
            max_score = prelim_score
    print("Max score: " + str(max_score))
    print("With the following contents: " + str(max_contents))

