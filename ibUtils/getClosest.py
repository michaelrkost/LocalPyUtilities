from bisect import bisect_left, bisect_right


class Closest:
    """Assumes *no* redundant entries - all inputs must be unique
    from:
    https://stackoverflow.com/questions/9706041/
    finding-index-of-an-item-closest-to-the-value-in-a-list-thats-not-entirely-sort
    """

    def __init__(self, numlist=None, firstdistance=0):
        if numlist == None:
            numlist = []
        self.numindexes = dict((val, n) for n, val in enumerate(numlist))
        self.nums = sorted(self.numindexes)
        self.firstdistance = firstdistance

    def append(self, num):
        if num in self.numindexes:
            raise ValueError("Cannot append '%s' it is already used" % str(num))
        self.numindexes[num] = len(self.nums)
        bisect.insort(self.nums, num)

    def rank(self, target):
        rank = bisect.bisect(self.nums, target)
        if rank == 0:
            pass
        elif len(self.nums) == rank:
            rank -= 1
        else:
            dist1 = target - self.nums[rank - 1]
            dist2 = self.nums[rank] - target
            if dist1 < dist2:
                rank -= 1
        return rank

    def closest(self, target):
        try:
            return self.numindexes[self.nums[self.rank(target)]]
        except IndexError:
            return 0

    def distance(self, target):
        rank = self.rank(target)
        try:
            dist = abs(self.nums[rank] - target)
        except IndexError:
            dist = self.firstdistance
        return dist

    # ======================================================
    # Let's consider that the column col of the dataframe df is sorted.
    #
    # In the case where the value val is in the column, bisect_left will return
    # the precise index of the value in the list and bisect_right will return
    # the index of the next position.
    # In the case where the value is not in the list, both bisect_left and bisect_right
    # will return the same index: the one where to insert the value to keep the list sorted.
    def get_closestInDFCol(df, col, val):
        lower_idx = bisect_left(df[col].values, val)
        higher_idx = bisect_right(df[col].values, val)

        if higher_idx == lower_idx:  # val is not in the list - both number are equal
            # see which idx is closer to val // if idx is closer than idx-1
            if abs(val - df.at[higher_idx, 'strike']) > abs(val - df.at[lower_idx-1, 'strike']):
                return higher_idx-1 # idx-1 is closer
            else:
                return higher_idx
        else:  # val is in the list return either number as they are the same
            return lower_idx
