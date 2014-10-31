import numpy as np
import random
import Image

"""
This is your object classifier. You should implement the train and
classify methods for this assignment.
"""
class ObjectClassifier():
    labels = ['Tree', 'Sydney', 'Steve', 'Cube']
    
    """
    Everytime a snapshot is taken, this method is called and
    the result is displayed on top of the four-image panel.
    """
    def classify(self, edge_pixels, orientations):
        #This will use a file that we generate in the trainer

        #(np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Steve/Steve2.png")
        #(np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Cube/Cube2.png")
        a = 0
        b = ""
        edge_pixel_count = 0
        for x in range(600):
            a+=1
            b = "Row" + str(a)
            for y in range(800):
                if edge_pixels[x, y] > 105 and x > 230: # and orientations[x, y] in (0, 180, 270, 90):
                    edge_pixel_count += 1
                #b = b +"," + str(np_edges[x,y])
        if edge_pixel_count < 3000:
            return self.labels[3]

        print "count: " + str(edge_pixel_count)
        return random.choice(self.labels)
    
    """
    This is your training method. Feel free to change the
    definition to take a directory name or whatever else you
    like. The load_image (below) function may be helpful in
    reading in each image from your datasets.
    """
    def train(self):
        #Generate a file using the numpy object

        stats_array = np.empty([4, 5])
        #Feature 1   2   3   4   5
        #Steve  :
        #Sydney :
        #Tree   :
        #Cube   :
        #(np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Sydney/Sydney1.png")
        #(np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Steve/Steve6.png")
        #(np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Cube/Cube2.png")
        # (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Tree/Tree2.png")
        # a = 0
        # b = ""
        # edge_pixels = 0
        # total_edges = 0
        # for x in range(600):
        #     a+=1
        #     b = "Row" + str(a)
        #     for y in range(800):
        #         if np_edges[x,y] > 105:
        #             edge_pixels +=1

        #         b = b +"," + str(np_edges[x,y])
        #     print b
        # print "The edge pix!: " + str(edge_pixels)


########################Actual Train Method################################

        for x in range(1, 11):
            (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Cube/Cube" + str(x) + ".png")
            print feature_identifier(np_edges, orientations)



                

        
        
"""
Loads an image from file and calculates the edge pixel orientations.
Returns a tuple of (edge pixels, pixel orientations).
"""
def load_image(filename):
    im = Image.open(filename)
    np_edges = np.array(im)
    upper_left = push(np_edges, 1, 1)
    upper_center = push(np_edges, 1, 0)
    upper_right = push(np_edges, 1, -1)
    mid_left = push(np_edges, 0, 1)
    mid_right = push(np_edges, 0, -1)
    lower_left = push(np_edges, -1, 1)
    lower_center = push(np_edges, -1, 0)
    lower_right = push(np_edges, -1, -1)
    vfunc = np.vectorize(find_orientation)
    orientations = vfunc(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right)
    return (np_edges, orientations)

        
"""
Shifts the rows and columns of an array, putting zeros in any empty spaces
and truncating any values that overflow
"""
def push(np_array, rows, columns):
    result = np.zeros((np_array.shape[0],np_array.shape[1]))
    if rows > 0:
        if columns > 0:
            result[rows:,columns:] = np_array[:-rows,:-columns]
        elif columns < 0:
            result[rows:,:columns] = np_array[:-rows,-columns:]
        else:
            result[rows:,:] = np_array[:-rows,:]
    elif rows < 0:
        if columns > 0:
            result[:rows,columns:] = np_array[-rows:,:-columns]
        elif columns < 0:
            result[:rows,:columns] = np_array[-rows:,-columns:]
        else:
            result[:rows,:] = np_array[-rows:,:]
    else:
        if columns > 0:
            result[:,columns:] = np_array[:,:-columns]
        elif columns < 0:
            result[:,:columns] = np_array[:,-columns:]
        else:
            result[:,:] = np_array[:,:]
    return result

# The orientations that an edge pixel may have.
np_orientation = np.array([0,315,45,270,90,225,180,135])

"""
Finds the (approximate) orientation of an edge pixel.
"""
def find_orientation(upper_left, upper_center, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right):
    a = np.array([upper_center, upper_left, upper_right, mid_left, mid_right, lower_left, lower_center, lower_right])
    return np_orientation[a.argmax()]


#Return a tuble where each value coresponds to a feature, boolean values
def feature_identifier( np_edges, orientations):
    #features
    (f1,f2,f3,f4,f5) = (False, False, False, False, False)


    #edge pictures in entire image
    edge_pixel_count = 0

    ##########Feature 1##############
    #Number of edge pixles in the bottom 2/3 of the screen is greater than 3000
    #The cube doesnt contribute many edge pixels so this should help find it
    f1_count = 0
    ##########Feature 2##############
    #Taken from the assignment, count upward facing pixels in the upper half of he image
    #should be useful in identifying the tree
    f2_count = 0
    ##########Feature 3##############
    #This keeps track of the total amount of edge pixels, the cube has under 10K for all the pics
    f3_count = 0

    for x in range(600):
        for y in range(800):
            #Only evaluate edge pixels
            if np_edges[x, y] > 105:
                edge_pixel_count += 1
                if x > 230: 
                    f1_count += 1
                if orientations[x,y] in (315, 0, 45) and x < 300:
                    f2_count += 1

    
    if f1_count < 3000:
        f1 = True
    
    if f2_count > 2500:
        f2 = True

    if f3_count < 10000:
        pass


    print "f1_count: " + str(f1_count)
    print "Total_edges: " + str(edge_pixel_count)

    return (f1,f2,f3,f4,f5)








if __name__ == "__main__":
    o = ObjectClassifier()
    o.train()
