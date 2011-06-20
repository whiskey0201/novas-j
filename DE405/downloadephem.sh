for i in 16 17 18 19  20 21
do for j in 00 20 40 60 80
    do ncftpget  ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de405/ascp$i$j.405
done
done

ncftpget  ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/de405/ascp2200.405
ncftpget ftp://ssd.jpl.nasa.gov/pub/eph/planets/ascii/ascii_format.txt