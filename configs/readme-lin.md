ABSTRACT

JANUS is a physical layer coding open-source promoted and developed by CMRE.
It is freely distributed under the GNU General Public License version 3.
The two primary purposes for JANUS are to announce the presence of a node and to
establish the initial contact between dissimilar nodes, establishing this way an
UW “lingua franca”.

BUILDING and INSTALLING

Example code to build the code in the directory 'build' inside the JANUS source
tree.  In this example the produced program will be installed in the directory
local_install also located inside the source tree.
Binaries will be compiled with debug option and allowed the prints for the
plug-ins code.

mkdir build
mkdir local-install
cd build
cmake -DCMAKE_INSTALL_PREFIX=../local-install -DCMAKE_BUILD_TYPE=Debug         \
-DJANUS_PLUGINS_DEBUG=1 ..                                                    &&
make -j8                                                                      &&
make install

In order to use floating point single precision where possible add cmake option:
  -DJANUS_REAL_SINGLE=1
To use single precision only in the fftw3 library (used in the base-bander) use:
  -DJANUS_FFTW_SINGLE=1

RUNNING EXAMPLES

Generation a base packet wav file named /tmp/janus.wav with sampling
rate of 48kHz.

./janus-porta/janus-tx --verbose 2                                       \
  --pset-file ./janus-porta/parameter_sets.csv               \
  --pset-id 1 --stream-driver 'wav' --stream-driver-args '/tmp/janus.wav'      \
  --stream-fs 48000

Running the decoder using alsa using the first audio device:


./janus-porta/janus-rx --verbose 2                                      \
  --pset-file ./janus-porta/parameter_sets.csv --pset-id 1   \
  --stream-driver 'wav' --stream-driver-args '/tmp/janus.wav' --stream-fs 48000

Using a configuration file but imposing a different option:

./janus-porta/janus-rx                                                   \
  --config-file ./janus-porta/janus.conf

where the file janus.conf might look like:

--verbose 2
--pset-file ./janus-porta/parameter_sets.csv
--pset-id 1
--stream-driver wav
--stream-driver-args /tmp/janus.wav
--stream-fs 48000