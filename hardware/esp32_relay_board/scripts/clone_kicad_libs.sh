#!/bin/sh -x
# Quick script to git clone all KiCad libraries (*.lib components and *.pretty footprints).
curl -S 'https://github.com/KiCad?page=[1-5]' | \
(perl -lne 'print $& while s|KiCad/[^/]+.pretty||'; echo KiCad/kicad-library) | \
sort -u | while read i; do test -d ${i#KiCad/} || git clone https://github.com/$i; done
for i in */.git; do (cd $i/.. && git pull); done
