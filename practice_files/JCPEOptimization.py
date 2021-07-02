#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from itertools import product
import copy
import sys


# In[2]:


#Stolen Code
class Vehicle():
    def __init__(self, id):
        self.id = id
        self.history = []
        self.batch_num = 0
        self.last_avail_time = 0

    def bind_fn(self, fx): #Fx is expected to be of type f()(current_loc, current_time, start_loc, start_time, end_loc). Assumes the data set does not contain self impossible rides, ie, that if you start a ride on time you can finish it as well
        self.fn = fx

    def getEndTime(self, start_loc, start_time, end_loc):
        return abs(end_loc[0] - start_loc[0]) + abs(end_loc[1] - start_loc[1]) + start_time - 1

    def bind(self, batch, ride): #Probably don't need all this info but it is nice to keep track of. End time here will be the ACTUAL finish time of the vehicle, as will start time, capped to a min of ride_start_time. Start time is the delta step when the vehicle is allowed to make its first move
        self.ride_id = ride[-1]
        self.history.append(self.ride_id)
        self.start_loc = (ride[0], ride[1])
        self.end_loc = (ride[2], ride[3])
        self.start_time = (ride[4] if self.last_avail_time < ride[4] else self.last_avail_time)
        self.end_time = self.getEndTime(self.start_loc, self.start_time, self.end_loc)
        self.last_avail_time = self.end_time + 1
        self.batch = batch
        self.batch_num += 1 #Used to externally slice the data set to pass proper batch reference to bind()

    def bind_batch(self, batch):
        self.batch = batch
        self.batch_num += 1


    def score(self):
        try:
            tmp = [self.fn(self.end_loc, self.end_time, (e[0],e[1]), e[4], (e[2],e[3])) for e in self.batch] #Batch is assumed to be a list of tuples of type (ride_id, start_loc, start_time, end_loc, etc...)
            idx_max = max(range(len(tmp)), key=tmp.__getitem__)
            idx_min = min(range(len(tmp)), key=tmp.__getitem__)
            if (tmp[idx_max] - tmp[idx_min])/tmp[idx_max] < .26: #0 Turns the feature off. .0001 seems to be the smallest value that affects overall score. .0982
                return -1 #Request new batch as this batch didn't yield a sufficient score difference for its maxima. It is possible that this can mean all scores are just really good too, but if a car doesn't seem to discriminate at all between the remaining rides, it is likely not a good candidate anyway.
            ret = copy.deepcopy(self.batch[idx_max])
            del(self.batch[idx_max])
            return ret
        except AttributeError:
            print("Missing a bind")
            return None
        except ValueError as e: #max(empty), batch is depleted. This can only happen in the very last batch when the total number of rides isn't evenly divded by the number of vehicles.
            return None


# In[3]:


#Some example functions to calculate score
import math

def getDist(current_loc, start_loc):
    return abs(start_loc[0] - current_loc[0]) + abs(start_loc[1] - current_loc[1])

def fn_bonus_greed_only(current_loc, current_time, start_loc, start_time, end_loc):
    #Check to see if the ride is actually possible to start on time
    if getDist(current_loc, start_loc) + current_time  > start_time:
        return 0
    return getDist(start_loc, end_loc) #No need to add bonus to all values

def fn_ratio_greed(current_loc, current_time, start_loc, start_time, end_loc):
    try:
        return (getDist(start_loc, end_loc) + (2 if getDist(current_loc, start_loc) + current_time > start_time else 0 )/getDist(current_loc, start_loc))
    except ZeroDivisionError:
        return (getDist(start_loc, end_loc) + (2 if getDist(current_loc, start_loc) + current_time > start_time else 0 )/.1)

def fn_log_greed(current_loc, current_time, start_loc, start_time, end_loc):
    try:
        return math.log(getDist(start_loc, end_loc) + (1000 if getDist(current_loc, start_loc) + current_time > start_time else 0 ),getDist(current_loc, start_loc))
    except (ValueError, ZeroDivisionError):
        return math.log(getDist(start_loc, end_loc) + (1000 if getDist(current_loc, start_loc) + current_time > start_time else 0 ),.1)
def fn_bonus_greed(current_loc, current_time, start_loc, start_time, end_loc):
    try:
        assert((current_time + getDist(current_loc, start_loc)) > start_time)
        try:
            return math.log(getDist(start_loc, end_loc), (start_time - current_time))*1000
        except (ValueError, ZeroDivisionError):
            return math.log(getDist(start_loc, end_loc),.1)*1000
    except AssertionError:
        try:
            return math.log(getDist(start_loc, end_loc), (start_time - current_time))
        except (ValueError, ZeroDivisionError):
            return math.log(getDist(start_loc, end_loc),.1)

# In[4]:


with open(sys.argv[1], "r") as file:
    data = file.read().split()

num_rows = int(data[0])
num_cols = int(data[1])
num_vehicles = int(data[2])
num_rides = int(data[3])
bonus = int(data[4])
total_steps = int(data[5])
num_batches = int(num_rides/num_vehicles)

rides = []

for i in range(int(num_rides)):
    rides.append([int(x) for x in data[6+i*6:12+i*6]]+[i])

# for i, r in enumerate(rides):
#     start_coords = tuple([r[0],r[1]])
#     end_coords = tuple([r[2],r[3]])
#     earliest_start = r[4]
#     latest_end = r[5]
#     rides[i] = [start_coords, end_coords, earliest_start, latest_end]

# rides = np.array(rides)


# In[5]:


rides[0]


# In[6]:


def sim_score(c,ride):
    return c[0]*(ride[0]+ride[1])+c[1]*(ride[2]+ride[3])+c[2]*ride[4]+c[3]*ride[5]


# In[15]:

def algorithm(parameters):
    output = ""
    c = parameters
    sorted_rides = []

    # [start_x, start_y, end_x, end_y, start_time, end_time, index]
    sorted_rides = sorted(rides,key = lambda x : sim_score(c,x))


    # In[9]:


    batches = [sorted_rides[num_vehicles*i:num_vehicles*(i+1)] for i in range(num_batches)]
    batches.append(sorted_rides[num_vehicles*num_batches:])
    history = []
    vehicles = [Vehicle(i) for i in range(num_vehicles)]
    for i, v in enumerate(vehicles):
        v.bind(batches[1],batches[0][i])
    #     print(batches[1])
        v.bind_fn(fn_log_greed)
    while(vehicles):
        tmp = [v.end_time for v in vehicles]
        idx = min(range(len(tmp)), key=tmp.__getitem__)
        cur_vehicle = vehicles[idx]
        next_ride = cur_vehicle.score()
    #     print(cur_vehicle)
        if(next_ride != None):
            if next_ride == -1:
                try:
                    cur_vehicle.bind_batch(batches[cur_vehicle.batch_num+2])
                except IndexError:
                    print(str(len(cur_vehicle.history)) + " " + " ".join(map(str,cur_vehicle.history)))
                    vehicles.remove(cur_vehicle)
            else:
                try:
                    cur_vehicle.bind(batches[cur_vehicle.batch_num+1],next_ride)
                except IndexError:
                    cur_vehicle.bind(None, next_ride)
                    print(str(len(cur_vehicle.history)) + " " + " ".join(map(str,cur_vehicle.history)))
                    vehicles.remove(cur_vehicle)
        else:
            #history.append(cur_vehicle.history)
            output = output + "\n" + str(len(cur_vehicle.history)) + " " + " ".join(map(str,cur_vehicle.history))
#             print(str(len(cur_vehicle.history)) + " " + " ".join(map(str,cur_vehicle.history)))
            vehicles.remove(cur_vehicle)
    return output




