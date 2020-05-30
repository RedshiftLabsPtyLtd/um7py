TARGET_EGG_INFO=um7py.egg-info
DIST=dist
BUILD=build

all:
	python3.7 setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm  -rf ${TARGET_EGG_INFO} ${DIST} ${BUILD}