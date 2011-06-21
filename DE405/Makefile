
ephemfiles = ascp2000.405.bin  ascp2020.405.bin  ascp2040.405.bin  ascp2060.405.bin ascp2080.405.bin
progs = convert append

#====================================================================#
#  Define Targets & Dependencies.                                    #
#====================================================================#
de405.bin: ${progs} ${ephemfiles}
	rm -f ephemtmp.bin
	for file in ${ephemfiles};do \
		if [ -f ephemtemp ] ;\
		then \
			 ./append ephemtmp.bin $${file}; \
		else \
			 cp $${file} ephemtmp.bin; \
		fi;\
	done
	mv ephemtmp.bin de405.bin


clean:
	rm -f de405.bin ephemtmp.bin ${Object_Files} ${ephemfiles} append convert ascp*405




Object_Files = convert.o        ephem_util.o       append.o   
convert: convert.o ephem_util.o
	cc -o convert convert.o ephem_util.o -lm
append: append.o ephem_util.o
	cc -o append append.o ephem_util.o -lm


#this stuff isn't needed because we're only deallig the DE405
#200: 
#	cp ephem_types.h ephem_types.tmp
#	rm ephem_types.h
#	sed 's/EPHEMERIS .../EPHEMERIS 200/' ephem_types.tmp > ephem_types.h
#	rm ephem_types.tmp

#405: 
#	cp ephem_types.h ephem_types.tmp
#	rm ephem_types.h
#	sed 's/EPHEMERIS .../EPHEMERIS 405/' ephem_types.tmp > ephem_types.h
#	rm ephem_types.tmp

extract: extract.o ephem_util.o
	cc -o extract extract.o ephem_util.o -lm

append: append.o ephem_util.o
	cc -o append append.o ephem_util.o -lm

#====================================================================#
# Make dependencies on header files explicit.                        #
#====================================================================#

convert.o: ephem_util.h ephem_types.h
	cc -c convert.c

ephem_util.o: ephem_types.h
	cc -c ephem_util.c

append.o: ephem_util.h ephem_types.h
	cc -c append.c

%.405: %.405.bz2
	bunzip2 -k  $< 
	touch $@


%.405.bin: %.405 header.405 convert
	./convert header.405 $< $@


