#file paths
crystal_main = ./crystalcafe-scraper/main.py
wiz_main = ./wizchan-scraper/main.py 

crystal: 
	python $(crystal_main)

wiz: 
	python $(wiz_main)

run: crystal

clean:
	rm -rf __pycache__      

.PHONY: run clean

#make test 
#import sys <- in python
#sys.argsv[index] <- in puthon
#instead of hardcoding directory name use argv
#argv:[./proc, arg1, arg2]
#command line arguments [./proc arg1 arg2]
#arg1 -> name of test dir
#arg2 -> site we are scraping
#-d testdir (create flags)