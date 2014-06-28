#!/bin/bash

f=`find . -name '*.md' | head -n1`
echo "Found file $f to compile..."

# MMD_TEXT_FILES_DIR is where you downloaded https://github.com/fletcher/peg-multimarkdown-latex-support
dir=$MMD_TEX_FILES_DIR
orig=`pwd`

echo "Switching to compilation dir $dir"
cp $f $dir
cp *.png $dir -v
cd $dir

echo "Compiling to TeX..."
multimarkdown --to=latex $f > "$f.tex"

echo "Compiling to PDF..."
if pdflatex "$f.tex"; then
	echo "PDF compiled with success."
else
	echo "PDF Compilation failed"
fi

echo "Cleaning LateX log..."
rm -vf "$f.log"


echo "Opening PDF..."
evince "$f.pdf" & 

echo "Switching back to original directory $orig"
cd $orig
