#!/bin/sh

REPO_COMMIT_SHORT=$(echo "$XYCE_REPO_COMMIT" | cut -c 1-7)

../configure \
	CXXFLAGS="-O3" \
	ARCHDIR="$XYCE_DIR/XyceLibs/Parallel" \
	CPPFLAGS="-I/usr/include/suitesparse" \
	--enable-mpi \
	CXX=mpicxx \
	CC=mpicc \
	F77=mpif77 \
	--enable-stokhos \
	--enable-amesos2 \
	--verbose \
	--prefix="${TOOLS}/${XYCE_NAME}/Parallel/${REPO_COMMIT_SHORT}"
