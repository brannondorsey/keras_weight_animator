#!/bin/bash
MAX_WIDTH="${MAX_WIDTH:-1920}"
MAX_HEIGHT="${MAX_HEIGHT:-1920}"
FRAMERATE="${FRAMERATE:-30}"

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$#" -ne 1 ] ; then
	echo "usage: create_image_sequence.sh <sequence_dir>"
	exit 1
fi

if [ -d "$1" ] ; then
	INPUT_DIR="$1"
else
	echo "\"$1\" is not a directory"
	exit 1
fi

check() {
	$(which $1 &> /dev/null)
	if [ $? -ne 0 ] ; then
		if [ $1 == 'mogrifyl' ] ; then
			echo "please install imagemagick"
		else
			echo "please install $1"
		fi
		exit 1
	fi
}

upscale() {
	FILE="$1"
	SIZE="$2"
	echo "$FILE $SIZE"
	mogrify -scale "$SIZE" "$FILE"
}

export -f upscale

check parallel
check mogrify
check ffmpeg

# for each image directory
for DIR in $(find $INPUT_DIR -type d -name 'epoch_*') ; do
	
	# copy files
    # cp -R "${DIR}" "${DIR}"

	SIZE=$(ls $DIR | head -n 1 | sed 's/^.*_//' | sed 's/\.png//')
	NEW_SIZE=$(python "$CUR_DIR/get_scale.py" $SIZE $MAX_WIDTH $MAX_HEIGHT)
	
	echo $SIZE $NEW_SIZE
	# resize images in parallel
	find "${DIR}" -name "*.png" | parallel upscale {} "$NEW_SIZE"
	
	# create the videos
	ffmpeg -y -framerate "$FRAMERATE" -pattern_type glob \
	    -i "${DIR}/*.png" -pix_fmt yuv420p \
	    -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
	    "${DIR}.mp4"
done
