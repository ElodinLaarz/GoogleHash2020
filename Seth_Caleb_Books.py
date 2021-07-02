import numpy as np
import sys

# {k:v} where k is the book index and v is the value/score of that book
value_of_each_book = {}
books_associated_to_library = []

total_collection_of_libraries = []

# inFile = 'data/d_tough_choices.txt'

# will be skewed to the right
probability_of_choosing_library = []

# will contain the first line: num books, num libraries, total days
initial_information = []

class Library(object):
    def __init__(self, library_key, setup_time, books_per_day, total_days):
        self.key = library_key
        self.collection_of_submitted_books = []
        self.books_per_day = books_per_day
        self.setup_time = setup_time
        self.score = self.scoring(total_days)
    def __str__(self):
        string_of_books = ''
        for s in self.collection_of_submitted_books:
            string_of_books += str(s) + ' '
        return f'{self.key} {len(self.collection_of_submitted_books)}\n'+string_of_books+'\n'
    def __repr__(self):
        return f'{self.score_value}'

    def books_submitted(self,days_left):
        num_books = (days_left-self.setup_time)*self.books_per_day
        if num_books <= 0:
            self.collection_of_submitted_books = []
        elif num_books < len(books_associated_to_library[self.key]):
            self.collection_of_submitted_books = books_associated_to_library[self.key][:num_books]
        else:
            self.collection_of_submitted_books = books_associated_to_library[self.key][:]
        return self.collection_of_submitted_books

    def scoring(self,days_left):
        self.books_submitted(days_left)
        self.score = sum(list(map(lambda x: value_of_each_book[x],self.collection_of_submitted_books)))
        return self.score

def create_sorted_prob_list(size = 1, dist = np.random.uniform, **kwargs):
    prob_list = sorted(dist(size = size, **kwargs))
    total = sum(prob_list)
    prob_list = prob_list/total
    return prob_list

with open(sys.argv[1],'r') as input_file:
    # num books, num libraries, total days
    initial_information = list(map(int,input_file.readline().split()))
    probability_of_choosing_library = create_sorted_prob_list(size=initial_information[1],
                                                              dist=np.random.exponential, scale = 0.0001) # Not entirely sure why this scale is chosen
    # Put the book:score values into a dictionary
    order = list(map(int,input_file.readline().split()))
    for i in range(initial_information[0]):
        value_of_each_book[i] = order[i]

    # Build the array of libraries
    for library_index in range(initial_information[1]):
        #num books, setup time, max books per day
        current_library_information = list(map(int,input_file.readline().split()))
        books_in_current_library = list(map(int,input_file.readline().split()))
        books_associated_to_library.append(sorted(books_in_current_library,key=lambda b: value_of_each_book[b]))

#         for book in books_associated_to_library[-1]:
#             # check if dictionary already has a value and associate the library to the book
#             if libraries_associated_to_book.get(book):
#                 libraries_associated_to_book[book].append(library_index)
#             else:
#                 libraries_associated_to_book[book] = [library_index]
        # add a library object to our total collection
        total_collection_of_libraries.append(Library(library_index,current_library_information[1],current_library_information[2],initial_information[2]))

# sort the list of library objects
total_collection_of_libraries = sorted(total_collection_of_libraries,key=lambda lib: lib.score)

libraries_sorted_index_associated_to_book = {}
for sorted_index,library in enumerate(total_collection_of_libraries):
    for book in books_associated_to_library[library.key]:
        if libraries_sorted_index_associated_to_book.get(book):
            libraries_sorted_index_associated_to_book[book].append(sorted_index)
        else:
            libraries_sorted_index_associated_to_book[book] = [sorted_index]

library_indices = [i for i in range(len(total_collection_of_libraries))]
# finds the maximal points a book is worth and later uses it as an exponent
point_exponent = value_of_each_book[max(value_of_each_book)]
factor = 0.99
libraries_to_submit = []
time_remaining = initial_information[2]

#IM ALL IN YOUR LOOP
while time_remaining > 1 and not all(probability_of_choosing_library == 0):
    # choose with probability
    # note: try to keep in mind when using the index of the sorted array or the
    # key of the library (index of unsorted array)
    probability_of_choosing_library = probability_of_choosing_library/sum(probability_of_choosing_library)
    random_index = np.random.choice(library_indices,p=probability_of_choosing_library)
    random_library_choice = total_collection_of_libraries[random_index]

    # do not choose the same library again
    probability_of_choosing_library[random_index] = 0

    # setup time check is there to avoid scoring unnecessarily
    if random_library_choice.setup_time < time_remaining and random_library_choice.scoring(time_remaining) > 0:
        libraries_to_submit.append(random_library_choice)
        for book in random_library_choice.collection_of_submitted_books:
            for library_index in libraries_sorted_index_associated_to_book[book]:
                if library_index != random_index:
                    books_associated_to_library[total_collection_of_libraries[library_index].key].remove(book)
                    probability_of_choosing_library[library_index]*=factor**(1+int(10*(value_of_each_book[book]/point_exponent))) #does not take into account the score of the book
        time_remaining -= random_library_choice.setup_time
# print(sum(list(map(lambda x: x.score,libraries_to_submit))))
with open(sys.argv[2],'w') as output_file:
    output_file.write(f'{len(libraries_to_submit)}\n')
    for cur_library_to_print in libraries_to_submit:
        output_file.write(str(cur_library_to_print))