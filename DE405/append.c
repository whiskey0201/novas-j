/**==========================================================================**/
/**                                                                          **/
/**  SOURCE FILE: append.c                                                   **/
/**                                                                          **/
/**      Purpose: This program concatenates two binary ephemeris files. The  **/
/**               file names are input from the command line,  and the data  **/
/**               from the second file is appended to the data in the first  **/
/**               file (excepting the header data, which is the same as the  **/
/**               header data  in the first file).  THEREFORE, users should  **/
/**               copy the file that contains the early part of the desired  **/
/**               data segment to a file with the desired name of the comb-  **/
/**               ined data file, and use  this name  as the first argument  **/
/**               on the command line invokation of this program. Of course, **/
/**               those who prefer to live dangerously are welcome to do so. **/
/**                                                                          **/
/**   Programmer: David Hoffman/EG5                                          **/
/**               NASA, Johnson Space Center                                 **/
/**               Houston, TX 77058                                          **/
/**               e-mail: david.a.hoffman1@jsc.nasa.gov                      **/
/**                                                                          **/
/**==========================================================================**/


#include <stdio.h>
#include "ephem_util.h"
#ifndef TYPES_DEFINED
#include "ephem_types.h"
#endif

main (argc, argv)
  char *argv[];
   int argc;
{
  headOneType  H11,  H21;
  headTwoType  H12,  H22;
  recOneType   R1 ,  R2;
  double       binRec[ARRAY_SIZE], T1, T2, T3 , T4;
  FILE        *fileOne, *fileTwo;

    /*------------------------------------------------------------------------*/
    /* Open data files; quit if unable to open any of them.                   */
    /*------------------------------------------------------------------------*/

    if ( argc == 3 ) {
         fileOne = fopen(argv[1],"r+");
         fileTwo = fopen(argv[2],"r");
       }
    else { 
         Warning(1);
         return 1;
       }

  if ( (fileOne==NULL) || (fileTwo==NULL) ) {         /* Print warning & quit */
       if (fileOne==NULL) Warning(5);                 /*    if unable to open */
       if (fileTwo==NULL) Warning(4);
       return 1;
     }

  /*--------------------------------------------------------------------------*/
  /* Read binary header records.                                              */
  /*--------------------------------------------------------------------------*/

  fread(&H11,sizeof(double),ARRAY_SIZE,fileOne);
  fread(&H12,sizeof(double),ARRAY_SIZE,fileOne);
  fread(&H21,sizeof(double),ARRAY_SIZE,fileTwo);
  fread(&H22,sizeof(double),ARRAY_SIZE,fileTwo);

  /*--------------------------------------------------------------------------*/
  /* Ensure both files are part of desired ephemeris.                         */
  /*--------------------------------------------------------------------------*/

  R1 = H11.data;
  R2 = H21.data;

  if ( R1.DENUM != R2.DENUM ) {
       Warning(16);
       return 1;
     }

  if ( R1.DENUM != EPHEMERIS ) {
       Warning(17);
       return 1;
     }

  /*--------------------------------------------------------------------------*/
  /* The Chebeyshev coefficient record for the last interval covered by an    */
  /* and ephemeris file is repeated before the end of the file. Furthermore,  */
  /* this same record appears at the start of the next ephemeris file. Thus   */
  /* two records have to be skipped when splicing the two files together, and */
  /* the first record from file 2 must _overwrite_ the last record of file 1. */
  /*--------------------------------------------------------------------------*/

  fseek(fileOne,-ARRAY_SIZE*sizeof(double),SEEK_END);     /* Find last record */
  fread(&binRec,sizeof(double),ARRAY_SIZE,fileOne);       /*          Read it */
  fseek(fileOne,-ARRAY_SIZE*sizeof(double),SEEK_END);     /*            Reset */

  T1 = binRec[0];
  T2 = binRec[1];
  
  fread(&binRec,sizeof(double),ARRAY_SIZE,fileTwo);      /* Start of file two */

  T3 = binRec[0];
  T4 = binRec[1];
  
  /*--------------------------------------------------------------------------*/
  /* Ensure that the first record of file two matches the last record of      */
  /* file one.                                                                */
  /*--------------------------------------------------------------------------*/

  if ( (T1 != T3) & (T2 != T4) ) 
     {
       Warning(19);
       return 1;
     }

  /*--------------------------------------------------------------------------*/
  /* Append remainder of file two to file one (Main Loop).                    */
  /*--------------------------------------------------------------------------*/

  while ( !feof(fileTwo) ) {
          fwrite(&binRec,sizeof(double),ARRAY_SIZE,fileOne);
          fread(&binRec,sizeof(double),ARRAY_SIZE,fileTwo);
        }

  /*--------------------------------------------------------------------------*/
  /* Close files & quit.                                                      */
  /*--------------------------------------------------------------------------*/

  fclose(fileOne);
  fclose(fileTwo);
  
  return 0;

} /**========================================================= END: append.c **/
