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
        #Analyse the current picture
        (f1,f2,f3,f4,f5) = feature_identifier(edge_pixels, orientations)

        features_percentages = np.load("Stats")

        (Tree, Steve, Sydney, Cube) = (0, 0, 0, 0)
        
        row = 0 #selects a character
        col = 0 #selects a feature
        for character in (Tree, Steve, Sydney, Cube):
            for feature in (f1,f2,f3,f4,f5):
                if feature:
                    character *= features_percentages[row,col]
                    col += 1
            row += 1

        cur_max = 0
        character_index = 0
        winner_index = 0
        for character in (Tree, Steve, Sydney, Cube):
            if character > cur_max:
                cur_max = character
                winner_index = character_index
            character_index += 1
        return labels.pop(winner_index)
    
    """
    This is your training method. Feel free to change the
    definition to take a directory name or whatever else you
    like. The load_image (below) function may be helpful in
    reading in each image from your datasets.
    """
    def train(self):
        #Generate a file using the numpy object

        stats_array = np.zeros([4, 5])
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
        a_object = 0
        for thing in self.labels:
            print thing
            (f1,f2,f3,f4,f5) = (False, False, False, False, False)
            (a,b,c,d,e) = (0,0,0,0,0) #used to count occurances of each feature per image set
            for count in range(1, 11):
                (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/" + thing + "/" + thing + str(count) + ".png")
                (f1,f2,f3,f4,f5) = feature_identifier(np_edges, orientations)
                if f1:
                    a+=1
                if f2:
                    b+=1
                if f3:
                    c+=1
                if f4:
                    d+=1
                if f5:
                    e+=1
                a_feature = 0
            for x in (a,b,c,d, e):
                stats_array[a_object, a_feature] = (x / 10.0)
                a_feature += 1

            a_object += 1

        np.save("Stats", stats_array)

        # for x in range(1, 11):
        #     (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Tree/Tree" + str(x) + ".png")
            
        # for x in range(1, 11):
        #     (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Sydney/Sydney" + str(x) + ".png")
        #     print feature_identifier(np_edges, orientations)
        # for x in range(1, 11):
        #     (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Steve/Steve" + str(x) + ".png")
        #     print feature_identifier(np_edges, orientations)
        # for x in range(1, 11):
        #     (np_edges, orientations) = load_image("/home/blake/AI2014/Hw5/snapshots/Training/Cube/Cube" + str(x) + ".png")
        #     print feature_identifier(np_edges, orientations)

        print stats_array



                

        
        
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
    ##########Feature 4##############
    #Idealy sydney will be the one with the verticle lines...nope turns out that's Steve
    #steve has a lot of verticle lines on the bottom half of the picture
    f4_count = 0
    ##########Feature 5##############
    #trying does the robot have a lot of horizontal edges?
    f5_count = 0

    for x in range(600):
        for y in range(800):
            #Only evaluate edge pixels
            if np_edges[x, y] > 105:
                edge_pixel_count += 1
                if x > 230: 
                    f1_count += 1
                if orientations[x,y] in (315, 0, 45) and x < 300:
                    f2_count += 1
                if orientations[x,y] in (0, 180) and x > 300:
                    f4_count += 1
                if orientations[x,y] in (90, 270) and x > 230:
                    f5_count += 1

    f3_count = edge_pixel_count

    if f1_count < 3000:
        f1 = True
    
    if f2_count > 2500:
        f2 = True

    if f3_count < 8000:
        f3 = True

    if f4_count > 1000:
        f4 = True

    if f5_count > 2200:
        f5 = True


    print "********"
    print "f1_count: " + str(f1_count)
    print "f2_count: " + str(f2_count)
    print "f3_count: " + str(f3_count)
    print "f4_count: " + str(f4_count)
    print "f5_count: " + str(f5_count)


    return (f1,f2,f3,f4,f5)








if __name__ == "__main__":
    o = ObjectClassifier()
    o.train()
