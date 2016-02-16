usage="usage: $(basename "$0") -f|--file [CSV_FILE]

where:
    -f|--file  .csv file to be analyzed"

if [ -z "$1" ]
 then
  echo "$usage"
  exit 1
 fi

# get command line args
while [[ $# > 1 ]]
do
key="$1"

case $key in
    -f|--file)
    CSV_FILE="$2"
    shift # past argument
    ;;
    --default)
    DEFAULT=YES
    ;;
    *)
            # unknown option
    ;;
esac
shift # past argument or value
done

echo 'Beginning Naive Bayesian Classification'

# process csv into proper file structure
python jake.py -f $CSV_FILE

while read numsets; do
	NUM_SETS=$numsets
done <numsets.txt

# run baysian classification
echo 'beginning classification...'
python timcv.py \
	-o Headers:include_score:True \
	-o TestDriver:show_histograms:False \
	-o TestDriver:show_false_positives:False \
	-o TestDriver:show_unsure:False \
    -o TestDriver:save_trained_pickles:True \
-n $NUM_SETS | tee classification_log.txt

# sort data
python jake.py -f Data/all_ratios.csv -c 3

# create new results.csv with new columns
python jake.py -f $CSV_FILE -c 2

# clean up created files
rm -rf Data
rm numsets.txt