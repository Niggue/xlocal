#!bin/bash

printf "\nMerging .dat files ... "
# setting column titles
printf "link_index,Code,Neighborhood,City,Offer_type,Property_type,Rooms,Baths,Parking_lots,Built_area,Private_area,Stratus,Price,Price/Area,Old\n" > datamerge.csv

printf "\nTitles ready"
# merging .dat files
cat mecu.dat finra.dat punpro.dat >> datamerge.csv
printf "\nData content ready"

echo

printf "All data merged!"


