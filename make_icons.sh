#!/bin/sh

rm -rf share/icons

dir=share/icons/hicolor/scalable/apps
mkdir -p ${dir}
cp share/curator.svg ${dir}/curator.svg
for size in 16 22 24 32 36 48 64 72 96 128 192 256; do

    dir=share/icons/hicolor/${size}x${size}/apps
    mkdir -p ${dir}
    rsvg-convert -w ${size} -h ${size} -o ${dir}/curator.png share/curator.svg
done
for size in 16 22 24 48; do
    darkdir=share/icons/ubuntu-mono-dark/apps/${size}
    lightdir=share/icons/ubuntu-mono-light/apps/${size}
    mkdir -p ${darkdir} ${lightdir}
    rsvg-convert -w ${size} -h ${size} -o ${darkdir}/curator-tray.svg share/curator-dark.svg
    rsvg-convert -w ${size} -h ${size} -o ${lightdir}/curator-tray.svg share/curator-light.svg
done
