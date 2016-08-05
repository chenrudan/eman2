#!/usr/bin/env bash

for f in `ls *.cpp`;do
    fb=${f%.cpp}
    mv "$fb".cpp "$fb".py
done
