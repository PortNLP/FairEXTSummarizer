import numpy as np
from collections import defaultdict


EPSILON = 0.0001

FAIRLETS = []
FAIRLET_CENTERS = []

class TreeNode:

    def __init__(self):
        self.children = []

    def set_cluster(self, cluster):
        self.cluster = cluster

    def add_child(self, child):
        self.children.append(child)

    def populate_colors(self, colors):
        "Populate auxiliary lists of red and blue points for each node, bottom-up"
        self.reds = []
        self.blues = []
        if len(self.children) == 0:
            # Leaf
            for i in self.cluster:
                if colors[i] == 0:
                    self.reds.append(i)
                else:
                    self.blues.append(i)
        else:
            # Not a leaf
            for child in self.children:
                child.populate_colors(colors)
                self.reds.extend(child.reds)
                self.blues.extend(child.blues)


### K-MEDIAN CODE ###

def kmedian_cost(points, centroids, dataset):
    "Computes and returns k-median cost for given dataset and centroids"
    return sum(np.amin(np.concatenate([np.linalg.norm(dataset[:,:]-dataset[centroid,:], axis=1).reshape((dataset.shape[0], 1)) for centroid in centroids], axis=1), axis=1))

def fair_kmedian_cost(centroids, dataset):
    "Return the output_FairGPT k-median cost for given centroids and fairlet decomposition"
    total_cost = 0
    for i in range(len(FAIRLETS)):
        # Choose index of centroid which is closest to the i-th fairlet center
        cost_list = [np.linalg.norm(dataset[centroids[j],:]-dataset[FAIRLET_CENTERS[i],:]) for j in range(len(centroids))]
        cost, j = min((cost, j) for (j, cost) in enumerate(cost_list))
        # Assign all points in i-th fairlet to above centroid and compute cost
        total_cost += sum([np.linalg.norm(dataset[centroids[j],:]-dataset[point,:]) for point in FAIRLETS[i]])
    return total_cost


### FAIRLET DECOMPOSITION CODE ###

def balanced(p, q, r, b):
    if r==0 and b==0:
        return True
    if r==0 or b==0:
        return False
    return min(r*1./b, b*1./r) >= p*1./q


def make_fairlet(points, dataset):
    "Adds fairlet to fairlet decomposition, returns median cost"
    FAIRLETS.append(points)
    cost_list = [sum([np.linalg.norm(dataset[center,:]-dataset[point,:]) for point in points]) for center in points]
    cost, center = min((cost, center) for (center, cost) in enumerate(cost_list))
    FAIRLET_CENTERS.append(points[center])
    return cost


def basic_fairlet_decomposition(p, q, blues, reds, dataset):
    """
    Computes vanilla (p,q)-fairlet decomposition of given points (Lemma 3 in NIPS17 paper).
    Returns cost.
    Input: Balance parameters p,q which are non-negative integers satisfying p<=q and gcd(p,q)=1.
    "blues" and "reds" are sets of points indices with balance at least p/q.
    """
    assert p <= q, "Please use balance parameters in the correct order"
    if len(reds) < len(blues):
        temp = blues
        blues = reds
        reds = temp
    R = len(reds)
    B = len(blues)
    assert balanced(p, q, R, B), "Input sets are unbalanced: "+str(R)+","+str(B)

    if R==0 and B==0:
        return 0

    b0 = 0
    r0 = 0
    cost = 0
    while (R-r0)-(B-b0) >= q-p and R-r0 >= q and B-b0 >= p:
        cost += make_fairlet(reds[r0:r0+q]+blues[b0:b0+p], dataset)
        r0 += q
        b0 += p
    if R-r0 + B-b0 >=1 and R-r0 + B-b0 <= p+q:
        cost += make_fairlet(reds[r0:]+blues[b0:], dataset)
        r0 = R
        b0 = B
    elif R-r0 != B-b0 and B-b0 >= p:
        cost += make_fairlet(reds[r0:r0+(R-r0)-(B-b0)+p]+blues[b0:b0+p], dataset)
        r0 += (R-r0)-(B-b0)+p
        b0 += p
    assert R-r0 == B-b0, "Error in computing fairlet decomposition"
    for i in range(R-r0):
        cost += make_fairlet([reds[r0+i], blues[b0+i]], dataset)
    return cost


def node_fairlet_decomposition(p, q, node, dataset, donelist, depth):

    # Leaf
    if len(node.children) == 0:
        node.reds = [i for i in node.reds if donelist[i]==0]
        node.blues = [i for i in node.blues if donelist[i]==0]
        assert balanced(p, q, len(node.reds), len(node.blues)), "Reached unbalanced leaf"
        return basic_fairlet_decomposition(p, q, node.blues, node.reds, dataset)

    # Preprocess children nodes to get rid of points that have already been clustered
    for child in node.children:
        child.reds = [i for i in child.reds if donelist[i]==0]
        child.blues = [i for i in child.blues if donelist[i]==0]

    R = [len(child.reds) for child in node.children]
    B = [len(child.blues) for child in node.children]

    if sum(R) == 0 or sum(B) == 0:
        assert sum(R)==0 and sum(B)==0, "One color class became empty for this node while the other did not"
        return 0

    NR = 0
    NB = 0

    # Phase 1: Add must-remove nodes
    for i in range(len(node.children)):
        if R[i] >= B[i]:
            must_remove_red = max(0, R[i] - int(np.floor(B[i]*q*1./p)))
            R[i] -= must_remove_red
            NR += must_remove_red
        else:
            must_remove_blue = max(0, B[i] - int(np.floor(R[i]*q*1./p)))
            B[i] -= must_remove_blue
            NB += must_remove_blue

    # Calculate how many points need to be added to smaller class until balance
    if NR >= NB:
        # Number of missing blues in (NR,NB)
        missing = max(0, int(np.ceil(NR*p*1./q)) - NB)
    else:
        # Number of missing reds in (NR,NB)
        missing = max(0, int(np.ceil(NB*p*1./q)) - NR)

    # Phase 2: Add may-remove nodes until (NR,NB) is balanced or until no more such nodes
    for i in range(len(node.children)):
        if missing == 0:
            assert balanced(p, q, NR, NB), "Something went wrong"
            break
        if NR >= NB:
            may_remove_blue = B[i] - int(np.ceil(R[i]*p*1./q))
            remove_blue = min(may_remove_blue, missing)
            B[i] -= remove_blue
            NB += remove_blue
            missing -= remove_blue
        else:
            may_remove_red = R[i] - int(np.ceil(B[i]*p*1./q))
            remove_red = min(may_remove_red, missing)
            R[i] -= remove_red
            NR += remove_red
            missing -= remove_red

    # Phase 3: Add unsatuated fairlets until (NR,NB) is balanced
    for i in range(len(node.children)):
        if balanced(p, q, NR, NB):
            break
        if R[i] >= B[i]:
            num_saturated_fairlets = int(R[i]/q)
            excess_red = R[i] - q*num_saturated_fairlets
            excess_blue = B[i] - p*num_saturated_fairlets
        else:
            num_saturated_fairlets = int(B[i]/q)
            excess_red = R[i] - p*num_saturated_fairlets
            excess_blue = B[i] - q*num_saturated_fairlets
        R[i] -= excess_red
        NR += excess_red
        B[i] -= excess_blue
        NB += excess_blue

    assert balanced(p, q, NR, NB), "Constructed node sets are unbalanced"

    reds = []
    blues = []
    for i in range(len(node.children)):
        for j in node.children[i].reds[R[i]:]:
            reds.append(j)
            donelist[j] = 1
        for j in node.children[i].blues[B[i]:]:
            blues.append(j)
            donelist[j] = 1

    assert len(reds)==NR and len(blues)==NB, "Something went horribly wrong"

    return basic_fairlet_decomposition(p, q, blues, reds, dataset) + sum([node_fairlet_decomposition(p, q, child, dataset, donelist, depth+1) for child in node.children])


def tree_fairlet_decomposition(p, q, root, dataset, colors):
    "Main fairlet clustering function, returns cost wrt original metric (not tree metric)"
    assert p <= q, "Please use balance parameters in the correct order"
    root.populate_colors(colors)
    assert balanced(p, q, len(root.reds), len(root.blues)), "Dataset is unbalanced"
    root.populate_colors(colors)
    donelist = [0] * dataset.shape[0]
    return node_fairlet_decomposition(p, q, root, dataset, donelist, 0)


### QUADTREE CODE ###

def build_quadtree(dataset, max_levels=0, random_shift=True):
    "If max_levels=0 there no level limit, quadtree will partition until all clusters are singletons"
    dimension = dataset.shape[1]
    lower = np.amin(dataset, axis=0)
    upper = np.amax(dataset, axis=0)

    shift = np.zeros(dimension)
    if random_shift:
        for d in range(dimension):
            spread = upper[d] - lower[d]
            shift[d] = np.random.uniform(0, spread)
            upper[d] += spread

    return build_quadtree_aux(dataset, range(dataset.shape[0]), lower, upper, max_levels, shift)


def build_quadtree_aux(dataset, cluster, lower, upper, max_levels, shift):
    """
    "lower" is the "bottom-left" (in all dimensions) corner of current hypercube
    "upper" is the "upper-right" (in all dimensions) corner of current hypercube
    """

    dimension = dataset.shape[1]
    cell_too_small = True
    for i in range(dimension):
        if upper[i]-lower[i] > EPSILON:
            cell_too_small = False

    node = TreeNode()
    if max_levels==1 or len(cluster)<=1 or cell_too_small:
        # Leaf
        node.set_cluster(cluster)
        return node

    # Non-leaf
    midpoint = 0.5 * (lower + upper)
    subclusters = defaultdict(list)
    for i in cluster:
        subclusters[tuple([dataset[i,d]+shift[d]<=midpoint[d] for d in range(dimension)])].append(i)
    for edge, subcluster in subclusters.items():
        sub_lower = np.zeros(dimension)
        sub_upper = np.zeros(dimension)
        for d in range(dimension):
            if edge[d]:
                sub_lower[d] = lower[d]
                sub_upper[d] = midpoint[d]
            else:
                sub_lower[d] = midpoint[d]
                sub_upper[d] = upper[d]
        node.add_child(build_quadtree_aux(dataset, subcluster, sub_lower, sub_upper, max_levels-1, shift))
    return node