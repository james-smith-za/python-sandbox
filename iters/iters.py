from itertools import islice # islice slices through an iter - useful in for loops

my_iter = iter(range(0,16)) # Note: iter objects can only be used once!

for i in my_iter:
    print 'i is now %d'%(i)
    f = raw_input('enter f: ')
    f = int(f)
    if i == f:
        print 'matched'
    else:
        diff = f - i
        print 'not matched. slicing.'
        next(islice(my_iter, diff - 1, diff), None) # This command will skip the correct number of iters to get you up to speed.


