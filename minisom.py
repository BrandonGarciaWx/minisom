from numpy import meshgrid,sqrt,sqrt,array,unravel_index,nditer,linalg,random,subtract,power,exp,pi,zeros

"""
Minimalistic implementation of the Self Organizing Maps (SOM)

SOM is able to convert complex, nonlinear statistical relationsihps between high-dimensional data items into simple geometric relationships on a low-dimensional display.

http://www.sis.pitt.edu/~ssyn/som/som.html
"""

class MiniSom:
    def __init__(self,x,y,input_len,sigma=0.1,learning_rate=0.5):
        """
            Initializes a Self Organizing Maps.
            x,y - dimensions of the SOM
            input_len - number of the elements of the vectors in input
            sigma - spread of the neighborhood function (Gaussian)
            learning_rate - initial learning rate
            (at the iteration t we have learning_rate(t) = learning_rate / (1 + t/T) where is #num_iteration/2)
        """
        self.learning_rate = learning_rate
        self.sigma = sigma
        self.weights = random.rand(x,y,input_len)*2-1 # random initialization
        self.weights = array([v/linalg.norm(v) for v in self.weights]) # normalization
        self.activation_map = zeros((x,y))
        self.neigx,self.neigy = meshgrid(range(y),range(x)) # used to evaluate the neighborhood function    

    def _activate(self,x):
        """ Updates matrix activation_map, in this matrix the element i,j is the response of the neuron i,j to x """
        s = subtract(x,self.weights) # x - w
        it = nditer(self.activation_map, flags=['multi_index'])
        while not it.finished:
            self.activation_map[it.multi_index] = linalg.norm(s[it.multi_index]) # || x - w ||
            it.iternext()

    def activate(self,x):
        """ Returns the activation map to x """
        self._activate(x)
        return self.activation_map

    def gaussian(self,c,sigma=0.1):
        """ Bidimentional Gaussian centered in c """
        d = sqrt( power((c[0]-self.neigx),2) + power((c[1]-self.neigy),2) )
        return exp(-(d*d))/(2*pi*sigma) # a matrix is returned

    def winner(self,x):
        """ Computes the coordinates of the winning neuron for the sample x """
        self._activate(x)
        return unravel_index(self.activation_map.argmin(),self.activation_map.shape)

    def update(self,x,win,t):
        """
            Updates the weights of the neurons.
            x - current pattern to learning
            win - position of the winning neuron for x (array or tuple).
            eta - learning rate
            t - iteration index
        """
        # eta(t) = eta(0) / (1 + t/T) keeps the learning rate nearly constant for the first T iterations and then adjusts it
        eta = self.learning_rate/(1+t/self.T)
        g = self.gaussian(win,self.sigma)*eta # improves the performances
        it = nditer(g, flags=['multi_index'])
        while not it.finished:
            self.weights[it.multi_index] += g[it.multi_index]*(x-self.weights[it.multi_index]) # eta * neighborhood_function * (x-w)           
            self.weights[it.multi_index] = self.weights[it.multi_index] / linalg.norm(self.weights[it.multi_index]) # weights normalization
            it.iternext()

    def random_weights_init(self,data):
        """ Initializes the weights of the SOM picking random samples from data """
        it = nditer(self.activation_map, flags=['multi_index'])
        while not it.finished:
            self.weights[it.multi_index] = data[int(random.rand()*len(data)-1)]
            self.weights[it.multi_index] = self.weights[it.multi_index]/linalg.norm(self.weights[it.multi_index])
            it.iternext()

    def train_random(self,data,num_iteration):        
        """ Trains the SOM picking samples at random from data """
        self.T = num_iteration/2 # keeps the learning rate nearly constant for the first half of the iterations        
        for iteration in range(num_iteration):
            rand_i = int(round(random.rand()*len(data)-1)) # pick a random sampleprint data[rand_i]           
            self.update(data[rand_i],self.winner(data[rand_i]),iteration)
            self._show_progress(iteration,num_iteration)

    def train_batch(self,data,num_iteration):
        """ Trains using all the vectors in data sequentially """
        self.T = num_iteration/2 # keeps the learning rate nearly constant for the first half of the iterations
        iteration = 0
        while iteration < num_iteration:
            idx = iteration % (len(data)-1)
            self.update(data[idx],self.winner(data[idx]),iteration)
            self._show_progress(iteration,num_iteration-1)
            iteration += 1

    def _show_progress(self,iteration,num_iteration):        
        progress = round((iteration/float(num_iteration))*50)
        #sys.stdout.write('\r')
        #sys.stdout.write('\r[ {0} {1}] {2}%'.format('#'*int(progress),' '*int(50-(progress)), int(progress*2)))
        #sys.stdout.flush()

    def distance_map(self):
        """ Returns the average distance map of the weights """
        um = zeros((self.weights.shape[0],self.weights.shape[1]))
        it = nditer(um, flags=['multi_index'])
        while not it.finished:
            for ii in range(it.multi_index[0]-1,it.multi_index[0]+2):
                for jj in range(it.multi_index[1]-1,it.multi_index[1]+2):
                    if ii >= 0 and ii < self.weights.shape[0] and jj >= 0 and jj < self.weights.shape[1]:
                        um[it.multi_index] += linalg.norm(self.weights[ii,jj,:]-self.weights[it.multi_index])
            it.iternext()
        um = um/8 # should be different at the borders
        return um

    def activation_response(self,data):
        """ 
            Returns a matrix where the element i,j is the number of times
            that the neuron i,j have been winner.
        """
        a = zeros((self.weights.shape[0],self.weights.shape[1]))
        for x in data:
            a[self.winner(x)] += 1
        return a

if __name__ == '__main__':
    import sys
    # reading the data from a csv file
    from numpy import genfromtxt
    data = genfromtxt('iris.csv', delimiter=',',usecols=(0,1,2,3))    
    #data = array([x/linalg.norm(x) for x in data]) # normalization
        
    # initialization and training
    som = MiniSom(6,6,4,sigma=0.3,learning_rate=0.5)
    som.random_weights_init(data)
    print "Training..."
    som.train_random(data,100)
    #som.train_batch(data,150*5)
    print "\n...ready!"
    
    from pylab import plot,axis,show,pcolor,colorbar,bone
    bone()
    pcolor(som.distance_map().T)
    #pcolor(som.activate(data[1]).T)
    #pcolor(som.activation_response(data).T)
    colorbar()
    # plotting the response for each pattern
    target = genfromtxt('iris.csv',delimiter=',',usecols=(4),dtype=str) # loading the labels
    t = zeros(len(target),dtype=int)
    t[target == 'setosa'] = 0
    t[target == 'versicolor'] = 1
    t[target == 'virginica'] = 2
    markers = ['o','s','D']
    colors = ['r','g','b']
    for cnt,xx in enumerate(data):
     w = som.winner(xx) # getting the winner
     plot(w[0]+.5,w[1]+.5,markers[t[cnt]],markerfacecolor='None',markeredgecolor=colors[t[cnt]],markersize=12,markeredgewidth=2)
    axis([0,som.weights.shape[0],0,som.weights.shape[1]])
    show()
    