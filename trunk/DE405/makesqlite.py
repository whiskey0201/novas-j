
# Takes JPL ephemeris DE405 text files and outputs the
# same data in a sqlite datafile.
# heavily based on EphemPy by Raymond L. Buvel

ephemNumber = '405'
asciiDir = '.' #where to find the ascii files

# This automatically selects an output file name based on the ephemeris.  If
# you don't like this convention, change it here.
outFileName = 'DE%s.sqlite' % ephemNumber

#-----------------------------------------------------------------------------
import os, fileinput, glob, struct,sqlite3

#---------------------------------------
#Prepare the databse
#---------------------------------------

#make sure the file is empty
fp = open(outFileName,'wb')
fp.close()

dbase = sqlite3.connect(outFileName)
dbase.execute("pragma foreign_keys=on")
dbase.execute("create table metadata(name TEXT, value TEXT)")

#A table to hold object data
#each record is an array of approx 1020 numbers
# and contains parameters for 32days
#offset: is the the index where the the numbers releveant to the object starts
#ncoeffs: is the number of chebshev coefficents used for 
#        the the polynomials that approximate each coordinate
#ngranules:
#        is the number of subintervals which the 32 day interval is broken into.
#
#This means that the number of members in each record
#is the sum over all the objects of ncoeffs * 3(dimensions) * ngranules +2
#the +2 because the start time and the end time are the first two values
dbase.execute("create table objects(objectID INTEGER PRIMARY KEY, shortname TEXT, longname TEXT,offset INTEGER, ncoeffs INTEGER, ngranules INTEGER, ndim INTEGER)") 

#a table to hold the constants
dbase.execute("create table constants(name TEXT, value REAL)")

#A table to hold the data (the old way)
#dbase.execute("create table positiondata(recordID INTEGER PRIMARY KEY,tstart REAL, tend REAL, coeffdata BLOB)")
#the blob will contain approx 1018 double in intel byte order 

dbase.execute("create table records(recordID INTEGER PRIMARY KEY, tstart REAL, tend REAL)");
dbase.execute("create table positiondata (recordID INTEGER, objectID INTEGER, coeffdata BLOB, FOREIGN KEY(recordID) REFERENCES records(recordID),FOREIGN KEY(objectID) REFERENCES objects(objectID))")



dbase.commit()



#-----------------------------------------------------------------------------
# Prepare the list of ASCII format files for processing.  The files must be in
# time sequence.

files = glob.glob(os.path.join(asciiDir,'asc*.%s' % ephemNumber))


tmplist = []
for name in files:
    if name.find('ascp') >= 0:
        tmplist.append(name)
#    else:
#        raise ValueError('Unknown file')

tmplist.sort()

files = [os.path.join(asciiDir,'header.%s' % ephemNumber)] + tmplist
print 'Number of files =', len(files)-1


curGroup = None
header = {}

def processHeader(line):
    global curGroup, arraySize

    if line.startswith('GROUP'):
        curGroup = line.split()[-1]
        if curGroup == '1070':
            # Start of the data group.  Write out the header records.
            #writeHeader() #actually no rush to write out header data
            return
        header[curGroup] = []
    elif line.startswith('KSIZE='):
        lst = line.split()
        arraySize = int(lst[-1])
    else:
        header[curGroup].append(line)

#-----------------------------------------------------------------------------
# Process lines in the data section.  When a new record is detected, the
# previous record is written.



#-----------------------------------------------------------------------------
# Verify the time sequence and write out the record.  Sets the global variables
# startTime and endTime as the records are written.  These times are used to
# adjust the start and end times in the header record.


def invalidGroup(name):
    return ValueError('GROUP %s invalid' % name)

#-----------------------------------------------------------------------------


#dbase.execute('insert into metadata values (?,?)',('jevon','was here'))


inputstream = fileinput.input(files)


while True:
    line = inputstream.readline()
    if line=='':
        raise "I got to the end of the input data before the headers were even over" 
    line = line.strip()
    if not line:
        # Skip blank lines
        continue
    if curGroup != '1070':
        processHeader(line)
    else:
        break


           
############
#put in the header information to the databse
##########

#header 1030 is timevals, putting them in as strings
nums = map(float,header['1030'][0].split())
dbase.execute('insert into constants values (?,?)',('tstart',nums[0]))
dbase.execute('insert into constants values (?,?)',('tend',nums[1]))
dbase.execute('insert into constants values (?,?)',('trec',nums[2]))

#header 1010 is titles
h = header['1010']
dbase.execute('insert into metadata values (?,?)',('title',h[0]))
dbase.execute('insert into metadata values (?,?)',('description',h[0]+', '+h[1]+', '+h[2]))

#header 1040 and 1041 are constants
numnames =  int(header['1040'][0])
numvals = int(header['1041'][0])
names = []
values = []
for h in header['1040'][1:]:
    names.extend(h.split())

for h in header['1041'][1:]:
    h = h.replace('D','e')
    values.extend(map(float,h.split()))

assert(numnames==numvals)
assert(numnames==len(names))
assert(numvals==len(values))

for k in range(len(names)):
    dbase.execute('insert into constants values (?,?)',(names[k],values[k]))



#header 1050 has data on the structure of each record
structdata = []
for h in header['1050']:
    structdata.extend(map(int,h.split()))

assert(len(structdata)%3==0)
nobjects=len(structdata)/3

assert(nobjects==13)

names=[
['mercury','Mercury'],
['venus','Venus'],
['earth','Earth-Moon Bartcenter'],
['mars','Mars'],
['jupiter','Jupiter'],
['saturn','Saturn'],
['uranus','Uranus'],
['neptune','Neptune'],
['pluto','Pluto'],
['moon','Moon (geocentric)'],
['sun','Sun'],
['nutations','Nutations'],
['librations','Librations']
]

offsets = structdata[0:nobjects]
ncoeffs = structdata[nobjects:(2*nobjects)]
ngranules = structdata[(2*nobjects):(3*nobjects)]

ndim = []

for k in range(nobjects):
    ndim.append(3)

#the 'body' 'nutation' only has 2 degrees of freedom (euler angles) i think?
ndim[12-1]=2


totalparameters = 2 #were going to count up number of parameters but tstart and tend will be missing so we'll start at two

for k in range(len(offsets)):
    offsets[k]=offsets[k]-3; # shift ofsets by three, two because we have removed the tstart and tend values from the blob, and one because we are starting counting from zero
    assert(offsets[k]==totalparameters-2)
    totalparameters=totalparameters+ndim[k]*ncoeffs[k]*ngranules[k]
    
assert(totalparameters==1018)

for k in range(nobjects):
    dbase.execute('insert into objects values (?,?,?,?,?,?,?)',(k+1,names[k][0],names[k][1],offsets[k],ncoeffs[k],ngranules[k],ndim[k]))



###########################################################################
## Put in all the data
###########################################################################
datarecord  = []
k=0

while True:
    line = inputstream.readline()
    nums = line.split()
    if line=='' or len(nums)==2: #we have either finished the file or started a new record
        if (k%500)==0:
            print "Processed %d records" % (k)
            dbase.commit() #cant hurt?
        if datarecord: #we have some data to save to database
            assert((len(datarecord)-arraySize<=2) and (len(datarecord)>=arraySize))
            tstart = datarecord[0]
            tend = datarecord[1]
            #this puts the records into positiondata as one big datablob (the oldway)
            #datablob = sqlite3.Binary(struct.pack('!%dd'%(len(datarecord[2:arraySize])),*datarecord[2:arraySize]))
#            dbase.execute('insert into positiondata values (?,?,?,?)',(k,tstart,tend,datablob))
            #this puts the start and end times into the table 'records' and puts positiondata into positiondata
            #one row per object per record
            datarecord = datarecord[2:arraySize]
            dbase.execute("insert into records values (?,?,?)",(k,tstart,tend))
            for m in range(nobjects):
                bloboffset = offsets[m]
                bloblength = ndim[m]*ncoeffs[m]*ngranules[m]
                datablob = sqlite3.Binary((struct.pack('!%dd'%(bloblength),*datarecord[bloboffset:(bloboffset+bloblength)])))
                dbase.execute("insert into positiondata values (?,?,?)",(k,m+1,datablob))
            #dbase.execute("create table records(recordID INTEGER PRIMARY KEY, tstart REAL, tend REAL)");
            #dbase.execute("create table positiondata(FOREIGN KEY recordID REFERENCES records(recordID),FOREIGN KEY(objectID) REFERENCES objects(objectID), coeffdata BLOB)")
            k=k+1
            datarecord=[]
        if line=='': #we are at the end of the file and therefore all done
            break
        else:
            assert(arraySize==int(nums[1])) #we must be at the start of the next data record
    else: #where in the middle of a record
        line=line.replace('D','e')
        nums = line.split()
        assert(len(nums)==3)#there records are made of lines of three numbers
        datarecord.extend([float(x) for x in nums])

dbase.commit()


print 'making indexes'
dbase.execute('CREATE INDEX posdataidx ON positiondata(objectID,recordID)')
dbase.execute('CREATE INDEX recordidx ON records(tstart)')
       


dbase.commit()
dbase.close()



    
